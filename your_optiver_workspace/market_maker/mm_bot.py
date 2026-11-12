"""mm_bot.py - wall-anchored flow-capture market maker for the 8 Optibook stocks.

Idea (from the extractor research, see bot_data/summary.txt):
  * The organizers' wall bot rests 3000-lot levels on both sides of a hidden fair value.
    Fair value = midpoint of those two walls. It behaves like a random walk.
  * The organizers' taker bot sends uninformed 20-lot IOC orders about 23 times a minute per stock,
    with a limit price spread evenly between the fair value and the far side of the opposite wall.
    Anyone resting a quote inside the walls is paid the distance to fair by that flow.
  * So: rest one bid and one ask inside the walls, one tick better than the best competing quote but
    never closer to fair than a minimum edge; lean both quotes against inventory; take quotes that
    other teams leave on the wrong side of fair; stay far below the 100-lot limit; finish flat.

Run as a plain script (never in a notebook). Only ONE process per team may be connected.

    python mm_bot.py --minutes 20              # run for 20 minutes from now
    python mm_bot.py --end 20:20:00            # run until this UTC time (use this form after a restart)
    python mm_bot.py --minutes 5 --only NVDA,AMD

Logs: mm_fills.csv (every fill with its edge versus fair), mm_state.csv (PnL and positions every second).
UNTESTED against the live exchange: tested only against a simulated exchange. Watch the first run.
"""
import argparse
import csv
import logging
import math
import sys
import time
from datetime import datetime, timedelta, timezone

from optibook.synchronous_client import Exchange

# --------------------------------------------------------------------------- parameters
POSITION_LIMIT = 100      # exchange limit per instrument [challenge slides]
SOFT_CAP = 60             # passive fills can never take |position| above this
HARD_CAP = 80             # if |position| ever gets here: cut to SOFT_CAP / 2 with a bounded IOC
QUOTE_SIZE = 20           # the organizers' taker sends 20-lot orders
MIN_SIZE = 2              # do not bother quoting less than this

MIN_EDGE = 0.5            # ticks between our quote and the inventory-adjusted fair value (0.5 -> 1 tick on whole-tick fairs)
SKEW_LIN, SKEW_CUB = 1.0, 1.0   # reservation price = fair - (LIN*x + CUB*x^3) ticks, x = position / SOFT_CAP
PENNY = True              # improve the best competing quote by one tick when the minimum edge allows it
COMP_VOL = 5              # a competing level only counts once this many lots rest at or better than it
TAKE_EDGE = 1.0           # hit a resting quote that is at least this many ticks on the wrong side of our reservation price
TAKE_SIZE = 20            # most lots taken with one IOC
TAKE_COOLDOWN = 0.25      # seconds between takes in one stock

WALL_MIN = 2500           # a level with at least this many lots is an organizer wall (the 3000-lot level)
MAX_WALL_SPREAD = 30      # ticks; wider than this is not a believable pair of walls
MAX_JUMP = 12             # ticks; a fair-value jump larger than this must persist JUMP_CONFIRM_S before we believe it
JUMP_CONFIRM_S = 0.5
WALL_GRACE_S = 0.4        # keep quotes this long while the walls are unreadable (they are refreshed every 1-3 s)
VOL_PAUSE_TICKS = 4.0     # fair moved this much within VOL_WINDOW_S -> pull quotes in that stock for VOL_PAUSE_S
VOL_WINDOW_S, VOL_PAUSE_S = 2.0, 1.0

LOOP_SLEEP = 0.1          # seconds between passes. AGENTS.md says 0.2 or more: raise to 0.2 if you see throttling
ACTION_GAP = 0.04         # minimum seconds between two order actions (insert / delete), about 25 per second
MIN_REQUOTE_S = 0.4       # a quote that is still acceptable is not moved more often than this (keeps queue position)
RECONCILE_POS_S = 1.0     # re-read positions and cash from the exchange this often
RECONCILE_ORD_S = 3.0     # re-read our resting orders per stock this often

REDUCE_ONLY_S = 120       # last seconds: only quotes that reduce inventory
FLATTEN_S = 45            # last seconds: pull quotes and close positions with bounded IOCs
CUT_SLIP = 2              # ticks through the wall a closing IOC may be priced
MAX_LOSS = 1500.0         # PnL (at fair value) below minus this: flatten everything and stop quoting
# Pairs whose fair values move together (5 s correlation): inventory in one counts toward the other.
# weight = lots of own-stock risk carried by one lot of the partner. Set USE_PAIRS False to switch off.
USE_PAIRS = True
PAIR_WEIGHT = {"AVGO": ("NBIS", 0.4), "NBIS": ("AVGO", 0.4), "CRWV": ("MU", 0.4), "MU": ("CRWV", 0.4),
               "NVDA": ("SNDK", 0.3), "SNDK": ("NVDA", 0.3)}

logging.getLogger("client").setLevel("ERROR")


def to_ticks(price, tick):
    return int(round(price / tick))


def to_price(ticks, tick):
    return round(ticks * tick, 2)


def utc_now():
    return datetime.now(timezone.utc)


class Bot:
    def __init__(self, ex, t_end, only=None):
        self.ex, self.t_end = ex, t_end
        inst = ex.get_tradable_instruments()
        self.tick = {i: v.tick_size for i, v in inst.items() if not only or i in only}
        self.iids = sorted(self.tick)
        self.pos = {i: 0 for i in self.iids}             # local view, corrected from the exchange every second
        self.cash = {i: 0.0 for i in self.iids}
        self.my = {i: {"bid": None, "ask": None} for i in self.iids}   # our resting order per side: {id, px, vol, t}
        self.fair = {}                                   # last trusted fair value per stock, in ticks (x.5 possible)
        self.fair_at = {}                                # when it was last confirmed
        self.fair_hist = {i: [] for i in self.iids}      # (time, fair) for the volatility pause
        self.jump = {}                                   # candidate fair after a large jump: (fair, first seen)
        self.pause_until = {i: 0.0 for i in self.iids}
        self.walls_bad_since = {}
        self.last_take = {i: 0.0 for i in self.iids}
        self.last_cut = {}                               # iid -> (time, position before)
        self.last_ord_recon = {i: 0.0 for i in self.iids}
        self.last_pos_recon = 0.0
        self.last_action = 0.0
        self.action_gap, self.loop_sleep = ACTION_GAP, LOOP_SLEEP
        self.halted = False
        self.pnl = self.peak = self.max_dd = 0.0
        self.n_actions = self.n_fills = self.n_fail = 0
        self.lots = 0
        self.edge_sum = 0.0
        self.max_pos = {i: 0 for i in self.iids}
        self.t0 = time.time()
        self.last_print = self.last_state = 0.0
        self.fills_f = open("mm_fills.csv", "a", newline="")
        self.state_f = open("mm_state.csv", "a", newline="")
        self.fills_w, self.state_w = csv.writer(self.fills_f), csv.writer(self.state_f)
        self.state_w.writerow(["utc", "pnl", "max_drawdown"] + self.iids)

    # ----------------------------------------------------------------- exchange calls
    def pace(self):
        wait = self.last_action + self.action_gap - time.time()
        if wait > 0:
            time.sleep(wait)
        self.last_action = time.time()
        self.n_actions += 1

    def failed(self, what, reason):
        self.n_fail += 1
        reason = str(reason)
        print(f"FAIL {what}: {reason}")
        low = reason.lower()
        if any(k in low for k in ("rate", "throttl", "too many", "frequen")):      # back off when throttled
            self.action_gap = min(0.5, self.action_gap * 1.5)
            self.loop_sleep = min(1.0, max(0.2, self.loop_sleep * 1.5))
            print(f"THROTTLED -> action gap {self.action_gap:.3f} s, loop sleep {self.loop_sleep:.2f} s")

    def insert(self, iid, px_t, vol, side, order_type="limit"):
        """Limit-aware insert. Returns the order id or None."""
        mine = self.my[iid]
        resting = mine[side]["vol"] if mine[side] else 0
        room = POSITION_LIMIT - self.pos[iid] - resting if side == "bid" else POSITION_LIMIT + self.pos[iid] - resting
        vol = int(min(vol, room))
        if vol < 1:
            return None
        other = mine["ask" if side == "bid" else "bid"]
        if other and ((side == "bid" and px_t >= other["px"]) or (side == "ask" and px_t <= other["px"])):
            return None                                   # would trade against our own resting order
        self.pace()
        r = self.ex.insert_order(iid, price=to_price(px_t, self.tick[iid]), volume=vol, side=side, order_type=order_type)
        if not r.success:
            self.failed(f"insert {iid} {side} {vol}@{px_t}", r.error_reason)
            self.last_ord_recon[iid] = 0.0                # force a re-read of our orders
            self.last_pos_recon = 0.0
            return None
        if order_type == "limit":
            mine[side] = {"id": r.order_id, "px": px_t, "vol": vol, "t": time.time()}
        return r.order_id

    def cancel(self, iid, side):
        o = self.my[iid][side]
        if not o:
            return
        self.pace()
        r = self.ex.delete_order(iid, order_id=o["id"])
        self.my[iid][side] = None                         # gone either way: deleted, or already filled
        if not r.success and "find" not in str(r.error_reason).lower():
            self.failed(f"delete {iid} {side}", r.error_reason)
            self.last_ord_recon[iid] = 0.0

    def poll_fills(self, iid):
        for t in self.ex.poll_new_trades(iid):            # the only place this poll is called
            sign = 1 if t.side == "bid" else -1
            self.pos[iid] += sign * t.volume
            o = self.my[iid][t.side]
            if o and o["id"] == t.order_id:
                o["vol"] -= t.volume
                if o["vol"] <= 0:
                    self.my[iid][t.side] = None
            f = self.fair.get(iid)
            px_t = t.price / self.tick[iid]
            edge = None if f is None else round(sign * (f - px_t), 2)   # ticks earned versus fair
            self.n_fills += 1
            self.lots += t.volume
            self.edge_sum += (edge or 0.0) * t.volume
            self.max_pos[iid] = max(self.max_pos[iid], abs(self.pos[iid]))
            self.fills_w.writerow([utc_now().isoformat(), iid, t.side, t.price, t.volume, f, edge, self.pos[iid], t.trade_id])

    def reconcile_positions(self):
        for iid in self.iids:
            self.poll_fills(iid)                          # drain first so a fill is not counted twice
        pc = self.ex.get_positions_and_cash()
        pnl = 0.0
        for iid in self.iids:
            if iid in pc:
                self.pos[iid], self.cash[iid] = int(pc[iid]["volume"]), float(pc[iid]["cash"])
                self.max_pos[iid] = max(self.max_pos[iid], abs(self.pos[iid]))
            f = self.fair.get(iid)
            if f is not None:
                pnl += self.cash[iid] + self.pos[iid] * f * self.tick[iid]
            elif self.pos[iid] == 0:
                pnl += self.cash[iid]
        self.pnl = pnl
        self.peak = max(self.peak, pnl)
        self.max_dd = max(self.max_dd, self.peak - pnl)
        self.last_pos_recon = time.time()

    def reconcile_orders(self, iid):
        """Make the local picture of our resting orders match the exchange. Keeps at most one per side."""
        tick, seen = self.tick[iid], {"bid": None, "ask": None}
        for o in self.ex.get_outstanding_orders(iid).values():
            if seen[o.side] is None:
                old = self.my[iid][o.side]
                seen[o.side] = {"id": o.order_id, "px": to_ticks(o.price, tick), "vol": o.volume,
                                "t": old["t"] if old and old["id"] == o.order_id else time.time()}
            else:                                         # a duplicate should never exist: remove it
                self.pace()
                self.ex.delete_order(iid, order_id=o.order_id)
        self.my[iid] = seen
        self.last_ord_recon[iid] = time.time()

    # ----------------------------------------------------------------- market reading
    def read(self, iid, now):
        """Walls, fair value and the best competing quotes. None when the book cannot be trusted."""
        book = self.ex.get_last_price_book(iid)
        if not book or not book.bids or not book.asks:
            return None
        tick, mine = self.tick[iid], self.my[iid]

        def scan(levels, own):
            wall = best = top = None
            cum = 0
            for lv in levels:
                pt = to_ticks(lv.price, tick)
                if lv.volume >= WALL_MIN:
                    wall = pt
                    break
                other = lv.volume - (own["vol"] if own and own["px"] == pt else 0)
                if other > 0:
                    if top is None:
                        top = (pt, other)                 # best price that is not ours, and its size
                    cum += other
                    if best is None and cum >= COMP_VOL:
                        best = pt                         # best competing level with real size
            return wall, best, top

        wb, ob, tb = scan(book.bids, mine["bid"])
        wa, oa, ta = scan(book.asks, mine["ask"])
        if wb is None or wa is None or not 2 <= wa - wb <= MAX_WALL_SPREAD:
            return None
        fair = (wb + wa) / 2
        last = self.fair.get(iid)
        if last is not None and abs(fair - last) > MAX_JUMP and now - self.fair_at.get(iid, 0) < 30:
            cand = self.jump.get(iid)
            if not cand or cand[0] != fair:
                self.jump[iid] = (fair, now)
                return None
            if now - cand[1] < JUMP_CONFIRM_S:
                return None
        self.jump.pop(iid, None)
        self.fair[iid], self.fair_at[iid] = fair, now
        hist = self.fair_hist[iid]
        hist.append((now, fair))
        while hist and now - hist[0][0] > VOL_WINDOW_S:
            hist.pop(0)
        if max(f for _, f in hist) - min(f for _, f in hist) >= VOL_PAUSE_TICKS:
            self.pause_until[iid] = now + VOL_PAUSE_S
        return {"fair": fair, "wb": wb, "wa": wa, "ob": ob, "oa": oa, "tb": tb, "ta": ta}

    def eff_pos(self, iid):
        """Inventory used for the skew: own position plus a share of the correlated partner's."""
        p = self.pos[iid]
        if USE_PAIRS and iid in PAIR_WEIGHT:
            partner, w = PAIR_WEIGHT[iid]
            if partner in self.pos:
                p += w * self.pos[partner] * (self.fair.get(partner, 0) * self.tick.get(partner, 0)
                                               / max(1e-9, self.fair.get(iid, 0) * self.tick[iid])
                                               if self.fair.get(partner) and self.fair.get(iid) else 0)
        return p

    def targets(self, iid, b, reduce_only):
        """-> (bid, bid_size, ask, ask_size, reservation) in ticks and lots."""
        pos, wb, wa = self.pos[iid], b["wb"], b["wa"]
        x = max(-1.5, min(1.5, self.eff_pos(iid) / SOFT_CAP))
        r = b["fair"] - (SKEW_LIN * x + SKEW_CUB * x ** 3)             # reservation price
        ask = math.ceil(r + MIN_EDGE - 1e-9)                           # closest to fair we are willing to sell
        bid = math.floor(r - MIN_EDGE + 1e-9)
        if PENNY:                                                      # do not give away more edge than needed
            ask = max(ask, (b["oa"] if b["oa"] is not None else wa) - 1)
            bid = min(bid, (b["ob"] if b["ob"] is not None else wb) + 1)
        ask = max(min(ask, wa), wb + 1)                                # never through the far wall, never past our own wall
        bid = min(max(bid, wb), wa - 1)
        if bid >= ask:                                                 # cannot happen with MIN_EDGE > 0; be safe
            bid = ask - 1
        bid_size = max(0, min(QUOTE_SIZE, SOFT_CAP - pos))
        ask_size = max(0, min(QUOTE_SIZE, SOFT_CAP + pos))
        if reduce_only:
            bid_size, ask_size = min(bid_size, max(0, -pos)), min(ask_size, max(0, pos))
        if bid_size < MIN_SIZE and not (reduce_only and bid_size > 0):
            bid_size = 0
        if ask_size < MIN_SIZE and not (reduce_only and ask_size > 0):
            ask_size = 0
        return bid, bid_size, ask, ask_size, r

    # ----------------------------------------------------------------- actions
    def manage_side(self, iid, side, px, size, now, deletes, inserts):
        """Queue the delete / insert needed to make our order on `side` match (px, size)."""
        o = self.my[iid][side]
        if o:
            ok_price = o["px"] == px
            ok_size = size > 0 and min(size, MIN_SIZE) <= o["vol"] <= max(size, QUOTE_SIZE)
            if ok_price and ok_size:
                return                                    # leave it: keeps its place in the queue
            # urgent = our price is on the wrong side of what we now accept (stale after a fair move) or size must go to 0
            urgent = size == 0 or (o["px"] > px if side == "bid" else o["px"] < px)
            if not urgent and now - o["t"] < MIN_REQUOTE_S:
                return
            deletes.append((0 if urgent else 1, iid, side))
        if size > 0:
            inserts.append((iid, side, px, size))

    def take(self, iid, b, r, now, reduce_only):
        """Hit a resting quote that sits at least TAKE_EDGE ticks on the wrong side of our reservation price."""
        if now - self.last_take[iid] < TAKE_COOLDOWN:
            return
        pos = self.pos[iid]
        tb, ta = b["tb"], b["ta"]
        if tb and tb[0] > b["wb"] and tb[0] - r >= TAKE_EDGE:           # someone bids above our value: sell to them
            cap = pos if reduce_only else SOFT_CAP + pos
            vol = min(tb[1], TAKE_SIZE, max(0, cap))
            if vol >= 1:
                self.last_take[iid] = now
                self.insert(iid, tb[0], vol, "ask", "ioc")
        elif ta and ta[0] < b["wa"] and r - ta[0] >= TAKE_EDGE:         # someone offers below our value: buy from them
            cap = -pos if reduce_only else SOFT_CAP - pos
            vol = min(ta[1], TAKE_SIZE, max(0, cap))
            if vol >= 1:
                self.last_take[iid] = now
                self.insert(iid, ta[0], vol, "bid", "ioc")

    def cut(self, iid, b, target_abs, now):
        """Bounded IOC that brings |position| down to target_abs. Waits 1 s for the position to update."""
        pos = self.pos[iid]
        t0, p0 = self.last_cut.get(iid, (0.0, None))
        vol = abs(pos) - target_abs
        if vol < 1 or (p0 == pos and now - t0 < 1.0):
            return
        if b:
            bound = b["wb"] - CUT_SLIP if pos > 0 else b["wa"] + CUT_SLIP
        elif iid in self.fair and now - self.fair_at[iid] < 10:
            bound = math.floor(self.fair[iid]) - 8 if pos > 0 else math.ceil(self.fair[iid]) + 8
        else:
            print(f"CUT {iid}: no reference price, position {pos} left open")
            return
        self.last_cut[iid] = (now, pos)
        self.insert(iid, bound, vol, "ask" if pos > 0 else "bid", "ioc")

    def pull(self, iid):
        for side in ("bid", "ask"):
            self.cancel(iid, side)

    # ----------------------------------------------------------------- one pass over all stocks
    def step(self):
        now = time.time()
        left = self.t_end - now
        for iid in self.iids:
            self.poll_fills(iid)
        if now - self.last_pos_recon > RECONCILE_POS_S:
            self.reconcile_positions()
            if self.pnl < -MAX_LOSS and not self.halted:
                self.halted = True
                print(f"KILL SWITCH: PnL {self.pnl:.1f} below -{MAX_LOSS}. Flattening and stopping.")
        flatten = self.halted or left < FLATTEN_S
        reduce_only = left < REDUCE_ONLY_S
        deletes, inserts = [], []
        books = {}
        for iid in self.iids:
            if now - self.last_ord_recon[iid] > RECONCILE_ORD_S:
                self.reconcile_orders(iid)
            b = books[iid] = self.read(iid, now)
            if b is None:
                self.walls_bad_since.setdefault(iid, now)
            else:
                self.walls_bad_since.pop(iid, None)
            pos = self.pos[iid]
            if flatten or abs(pos) >= HARD_CAP:
                self.pull(iid)
                self.cut(iid, b, 0 if flatten else SOFT_CAP // 2, now)
                continue
            if b is None:                                 # walls unreadable: keep quotes briefly, then pull
                if now - self.walls_bad_since[iid] > WALL_GRACE_S:
                    self.pull(iid)
                continue
            if now < self.pause_until[iid]:               # fair is moving fast: stand aside
                self.pull(iid)
                continue
            bid, bsz, ask, asz, r = self.targets(iid, b, reduce_only)
            self.take(iid, b, r, now, reduce_only)
            self.manage_side(iid, "bid", bid, bsz, now, deletes, inserts)
            self.manage_side(iid, "ask", ask, asz, now, deletes, inserts)
        for _, iid, side in sorted(deletes):              # stale quotes first, across all stocks
            self.cancel(iid, side)
        for iid, side, px, size in inserts:
            if self.my[iid][side] is None:
                self.insert(iid, px, size, side)
        self.report(now, left)

    def report(self, now, left):
        if now - self.last_state > 1.0:
            self.state_w.writerow([utc_now().isoformat(), round(self.pnl, 2), round(self.max_dd, 2)] + [self.pos[i] for i in self.iids])
            self.last_state = now
        if now - self.last_print > 5.0:
            run = max(1.0, now - self.t0)
            edge = self.edge_sum / self.lots if self.lots else 0.0
            pos = " ".join(f"{i}:{self.pos[i]:+d}" for i in self.iids)
            print(f"[{left:6.0f}s left] pnl {self.pnl:8.1f} dd {self.max_dd:6.1f} | fills {self.n_fills} lots {self.lots} "
                  f"edge/lot {edge:+.2f}t | {self.n_actions / run:4.1f} act/s fails {self.n_fail} | {pos}", flush=True)
            self.fills_f.flush()
            self.state_f.flush()
            self.last_print = now

    def run(self):
        print(f"instruments: {self.iids}")
        t = time.time()
        for _ in range(50):
            self.ex.get_last_price_book(self.iids[0])
        print(f"get_last_price_book takes {(time.time() - t) / 50 * 1000:.2f} ms per call "
              f"(well under 1 ms means it is a local read; several ms means every read is a network request -> raise LOOP_SLEEP)")
        self.reconcile_positions()
        for iid in self.iids:
            self.reconcile_orders(iid)
        print(f"start positions: {self.pos}")
        try:
            while True:
                if not self.ex.is_connected():
                    raise SystemExit("KICKED: another client connected with our credentials. Restart with --end.")
                if time.time() > self.t_end + 3:
                    break
                try:
                    self.step()
                except SystemExit:
                    raise
                except Exception as e:                    # never die mid-session; state is re-read on the next pass
                    print(f"ERROR in step: {e!r}")
                    self.last_pos_recon = 0.0
                    self.last_ord_recon = {i: 0.0 for i in self.iids}
                    time.sleep(0.2)
                time.sleep(self.loop_sleep)
        finally:
            for iid in self.iids:
                try:
                    self.ex.delete_orders(iid)
                except Exception:
                    pass
            try:
                self.reconcile_positions()
            except Exception:
                pass
            edge = self.edge_sum / self.lots if self.lots else 0.0
            print("\n==== SESSION SUMMARY ====")
            print(f"PnL at fair value {self.pnl:.1f} | max drawdown {self.max_dd:.1f} | fills {self.n_fills} | lots {self.lots} "
                  f"| average edge {edge:+.2f} ticks per lot | order actions {self.n_actions} | failures {self.n_fail}")
            print(f"final positions {self.pos}")
            print(f"largest |position| per stock {self.max_pos}")
            self.fills_f.close()
            self.state_f.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=None, help="run for this many minutes from now")
    ap.add_argument("--end", type=str, default=None, help="stop at this UTC time, HH:MM or HH:MM:SS (restart-safe)")
    ap.add_argument("--only", type=str, default=None, help="comma-separated instruments to trade")
    a = ap.parse_args()
    now = utc_now()
    if a.end:
        parts = [int(p) for p in a.end.split(":")] + [0]
        end = now.replace(hour=parts[0], minute=parts[1], second=parts[2], microsecond=0)
        if end < now - timedelta(hours=12):
            end += timedelta(days=1)
    else:
        end = now + timedelta(minutes=a.minutes if a.minutes is not None else 20)
    print(f"now {now:%H:%M:%S} UTC, trading until {end:%H:%M:%S} UTC. If you have to restart, run:  python mm_bot.py --end {end:%H:%M:%S}")
    if end <= now:
        raise SystemExit("end time is in the past")
    ex = Exchange(max_nr_trade_history=5000)
    ex.connect()
    if not ex.is_connected():
        raise SystemExit("not connected")
    Bot(ex, end.timestamp(), set(a.only.split(",")) if a.only else None).run()


if __name__ == "__main__":
    main()
