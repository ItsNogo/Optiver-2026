"""mm_bot.py - tick-clock market maker and stale-quote taker for the 8 Optibook stocks.

What the research on 4 hours of exchange history showed (bot_data/summary.txt plus follow-up analysis):
  * The organizers' wall bot rests a ladder on each side of a hidden fair value: 3000/2000/1000 lots on
    the five narrow stocks (AMD, AVGO, MU, NVDA, VRT), 1000/750/500 on the three wide ones (CRWV, NBIS,
    SNDK). Fair value = midpoint of the two innermost ladder levels. It is a random walk.
  * The walls only move on a fixed one-second clock, at the same phase every second per stock.
    Quotes left resting across that instant are what gets picked off: fills within 100 ms of a wall
    move lose about 2.7 ticks, fills more than 300 ms after one earn about 0.35 ticks.
  * The organizers' taker sends uninformed 20-lot IOCs about 24 times a minute per stock and hits the
    best quote. Other teams leave quotes on the wrong side of the new fair value after a move.

So this bot:
  1. rests one bid and one ask inside the walls: at the touch on narrow stocks, at least 2 ticks from
     fair on wide stocks (where the edge is 1.5-3 ticks a lot);
  2. learns each stock's clock phase and pulls its narrow-stock quotes just before the walls can move,
     then re-quotes from the new walls;
  3. takes resting quotes that sit a full tick (narrow) or two ticks (wide) on the wrong side of its
     inventory-adjusted fair value;
  4. leans every price against inventory, caps inventory far below the 100-lot limit, nets inventory
     across the two correlated pairs, has a kill switch, and finishes flat.

Run as a plain script (never in a notebook). Only ONE process per team may be connected.

    python mm_bot.py --minutes 20              # run for 20 minutes from now
    python mm_bot.py --end 20:20:00            # run until this UTC time (use this form after a restart)
    python mm_bot.py --minutes 5 --only NBIS,CRWV,SNDK

Logs: mm_fills.csv (every fill with its edge versus fair), mm_state.csv (PnL and positions every second).
UNTESTED against the live exchange: tested only against a simulated exchange. Watch the first run.
"""
import argparse
import cmath
import csv
import logging
import math
import time
from collections import deque
from datetime import datetime, timedelta, timezone

from optibook.synchronous_client import Exchange

# --------------------------------------------------------------------------- parameters
POSITION_LIMIT = 100                 # exchange limit per instrument [challenge slides]
SOFT_CAP_NARROW, SOFT_CAP_WIDE = 40, 80   # passive fills and takes never push |position| above this
HARD_CAP = 95                        # if |position| ever gets here: cut to half the soft cap with a bounded IOC
QUOTE_SIZE = 20                      # the organizers' taker sends 20-lot orders
MIN_SIZE = 2                         # do not bother quoting less than this

WALL_BIG, WALL_SMALL = 2500, 700     # innermost ladder level: >= 2500 lots (narrow stocks) else >= 700 (wide stocks)
MIN_EDGE_NARROW = 0.5                # ticks between our quote and the inventory-adjusted fair value
MIN_EDGE_WIDE = 2.0                  # wide stocks: at least this many ticks from the adjusted fair value
PASSIVE_OFF = {"AVGO", "AMD", "NVDA"}   # no resting quotes here: the first live run lost on them (takes still allowed)
REFILL_S = 1.5                       # after one of our quotes is filled, do not re-quote that side for this long
# Lead-lag: the follower's walls copy the leader's move about 3 s later (corr ~0.94 on 3 s windows after the restart).
# follower: (leader, follower ticks per leader tick)
LEADS = {"NBIS": ("AVGO", 0.22), "CRWV": ("MU", 0.95), "SNDK": ("NVDA", 0.45)}
LL_LEAK = 0.15                       # ticks per second by which an unpaid expected move fades
LL_TIMEOUT = 7.0                     # seconds after which a move the follower still has not made is forgotten
LL_MIN, LL_CAP = 1.5, 30.0           # expected move that counts as a signal / largest we believe, in ticks
LL_WALL_EDGE = 2.0                   # take the follower's wall itself when the expected move beats it by this much
LL_TAKE_SIZE = 80                    # lots per take when the expected move is at least 4 ticks
SKEW_LIN, SKEW_CUB = 1.0, 1.0        # reservation price = fair - (LIN*x + CUB*x^3) ticks, x = inventory / soft cap
PENNY = True                         # improve the best competing quote by one tick when the minimum edge allows it
COMP_VOL = 5                         # a competing level only counts once this many lots rest at or better than it
TAKE = True                          # hit resting quotes that are on the wrong side of our reservation price
TAKE_EDGE_NARROW, TAKE_EDGE_WIDE = 1.0, 2.0   # ...by at least this many ticks
TAKE_SIZE = 20
TAKE_COOLDOWN = 0.25                 # seconds between takes in one stock

TICK_AWARE = True                    # pull narrow-stock quotes around the walls' one-second reprice instant
TICK_PRE, TICK_POST = 0.12, 0.08     # seconds before / after the learned instant during which we do not rest quotes
PHASE_MIN_SAMPLES, PHASE_MIN_R = 8, 0.6   # how sure we must be of a stock's clock phase before using it

MAX_WALL_SPREAD = 30                 # ticks; wider than this is not a believable pair of walls
MAX_JUMP = 12                        # ticks; a larger fair-value jump must persist JUMP_CONFIRM_S before we believe it
JUMP_CONFIRM_S = 0.15
WALL_GRACE_S = 0.4                   # keep quotes this long while the walls are unreadable
VOL_PAUSE_TICKS = 4.0                # fair moved this much within VOL_WINDOW_S -> stand aside for VOL_PAUSE_S
VOL_WINDOW_S, VOL_PAUSE_S = 2.0, 1.0

LOOP_SLEEP = 0.05                    # seconds between passes (book reads look local; raise to 0.2 if throttled)
ACTION_GAP = 0.04                    # minimum seconds between two order actions: about 25 per second
MIN_REQUOTE_S = 0.4                  # a quote that is still acceptable is not moved more often than this
RECONCILE_POS_S = 1.0                # re-read positions and cash from the exchange this often
RECONCILE_ORD_S = 3.0                # re-read our resting orders per stock this often

REDUCE_ONLY_S = 60                   # last seconds: only quotes and takes that reduce inventory
FLATTEN_S = 30                       # last seconds: pull quotes and close positions with bounded IOCs
CUT_SLIP = 2                         # ticks through the wall a closing IOC may be priced
MAX_LOSS = 800.0                     # PnL since start (at fair value) below minus this: flatten everything and stop
STALE_BOOK_S = 5.0                   # a book whose timestamp has not changed for this long is not trusted
# Correlated pairs (30 s correlation ~0.9+): a share of the partner's inventory counts as our own for the skew.
USE_PAIRS = False
PAIR_WEIGHT = {"AVGO": ("NBIS", 0.2), "NBIS": ("AVGO", 0.6), "CRWV": ("MU", 0.4), "MU": ("CRWV", 0.4)}

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
        if not self.iids:
            raise SystemExit("no tradable instruments match")
        self.pos = {i: 0 for i in self.iids}             # local view, corrected from the exchange every second
        self.cash = {i: 0.0 for i in self.iids}
        self.my = {i: {"bid": None, "ask": None} for i in self.iids}   # our resting order per side: {id, px, vol, t}
        self.wide = {i: False for i in self.iids}        # True for the 1000-lot-wall stocks
        self.fair = {}                                   # last trusted fair value per stock, in ticks (x.5 possible)
        self.fair_at = {}
        self.fair_hist = {i: deque() for i in self.iids}
        self.jump = {}
        self.chg = {i: deque(maxlen=30) for i in self.iids}   # fraction of the second at which fair changes were seen
        self.phase = {}                                  # learned clock phase per stock (local clock, seconds mod 1)
        self.pause_until = {i: 0.0 for i in self.iids}
        self.walls_bad_since = {}
        self.last_take = {i: 0.0 for i in self.iids}
        self.last_cut = {}
        self.debt = {b: 0.0 for b in LEADS}              # follower -> move it still owes its leader, in ticks
        self.ll_prev, self.debt_since, self.ll_t = {}, {}, time.time()
        self.side_block = {}                             # (iid, side) -> time until which that side is not re-quoted
        self.last_force_pull = {}
        self.last_ord_recon = {i: 0.0 for i in self.iids}
        self.last_pos_recon = 0.0
        self.last_action = 0.0
        self.action_gap, self.loop_sleep = ACTION_GAP, LOOP_SLEEP
        self.halted = False
        self.pnl = self.peak = self.max_dd = 0.0
        self.pnl0 = None
        self.book_seen = {}                              # iid -> (book timestamp, local time it first appeared)
        self.n_actions = self.n_fills = self.n_fail = self.n_takes = 0
        self.lots = 0
        self.edge_sum = 0.0
        self.max_pos = {i: 0 for i in self.iids}
        self.t0 = time.time()
        self.last_print = self.last_state = 0.0
        stamp = utc_now().strftime("%H%M%S")
        self.fills_f = open(f"mm_fills_{stamp}.csv", "w", newline="")
        self.state_f = open(f"mm_state_{stamp}.csv", "w", newline="")
        print(f"logs: mm_fills_{stamp}.csv, mm_state_{stamp}.csv")
        self.feed_ok, self.last_feed = True, 0.0
        self.fills_w, self.state_w = csv.writer(self.fills_f), csv.writer(self.state_f)
        self.fills_w.writerow(["utc", "instrument", "side", "price", "volume", "fair_ticks", "edge_ticks", "position", "trade_id"])
        self.state_w.writerow(["utc", "pnl", "max_drawdown"] + self.iids + ["fair_" + i for i in self.iids] + ["lead_" + i for i in self.iids])

    def soft_cap(self, iid):
        return SOFT_CAP_WIDE if self.wide[iid] else SOFT_CAP_NARROW

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
        print(f"FAIL {what}: {reason}", flush=True)
        low = reason.lower()
        if any(k in low for k in ("rate", "throttl", "too many", "frequen")):      # back off when throttled
            self.action_gap = min(0.5, self.action_gap * 1.5)
            self.loop_sleep = min(1.0, max(0.2, self.loop_sleep * 1.5))
            print(f"THROTTLED -> action gap {self.action_gap:.3f} s, loop sleep {self.loop_sleep:.2f} s", flush=True)

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
            self.last_ord_recon[iid] = 0.0                # force a re-read of our orders and positions
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
        if r.success or "find" in str(r.error_reason).lower():
            self.my[iid][side] = None                     # deleted, or already gone (filled)
        else:                                             # still resting as far as we know: keep it, re-read soon
            self.failed(f"delete {iid} {side}", r.error_reason)
            self.last_ord_recon[iid] = 0.0

    def pull(self, iid):
        """Remove both quotes of one stock with a single request."""
        mine = self.my[iid]
        if mine["bid"] or mine["ask"]:
            self.pace()
            self.ex.delete_orders(iid)                    # returns nothing; the periodic re-read confirms it
            mine["bid"] = mine["ask"] = None

    def poll_fills(self, iid):
        for t in self.ex.poll_new_trades(iid):            # the only place this poll is called
            sign = 1 if t.side == "bid" else -1
            self.pos[iid] += sign * t.volume
            o = self.my[iid][t.side]
            if o and o["id"] == t.order_id:
                self.side_block[(iid, t.side)] = time.time() + REFILL_S
                o["vol"] -= t.volume
                if o["vol"] <= 0:
                    self.my[iid][t.side] = None
            f = self.fair.get(iid)
            edge = None if f is None else round(sign * (f - t.price / self.tick[iid]), 2)   # ticks earned versus fair
            self.n_fills += 1
            self.lots += t.volume
            self.edge_sum += (edge or 0.0) * t.volume
            self.max_pos[iid] = max(self.max_pos[iid], abs(self.pos[iid]))
            self.fills_w.writerow([utc_now().isoformat(), iid, t.side, t.price, t.volume, f, edge, self.pos[iid], t.trade_id])

    def reconcile_positions(self):
        for iid in self.iids:
            self.poll_fills(iid)                          # drain first so a fill is not counted twice
        pc = self.ex.get_positions_and_cash()
        total, complete = 0.0, True
        for iid in self.iids:
            if iid in pc:
                self.pos[iid], self.cash[iid] = int(pc[iid]["volume"]), float(pc[iid]["cash"])
                self.max_pos[iid] = max(self.max_pos[iid], abs(self.pos[iid]))
            f = self.fair.get(iid)
            if f is None and self.pos[iid] != 0:
                complete = False                          # cannot value this position yet
            total += self.cash[iid] + (self.pos[iid] * f * self.tick[iid] if f is not None else 0.0)
        if complete:
            if self.pnl0 is None:
                self.pnl0 = total                         # PnL is reported relative to the moment the bot started
            self.pnl = total - self.pnl0
            self.peak = max(self.peak, self.pnl)
            self.max_dd = max(self.max_dd, self.peak - self.pnl)
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
        ts = getattr(book, "timestamp", None)
        seen = self.book_seen.get(iid)
        if seen is None or seen[0] != ts:
            self.book_seen[iid] = (ts, now)
        elif now - seen[1] > STALE_BOOK_S:
            return None                                   # the feed for this stock has stalled
        tick, mine = self.tick[iid], self.my[iid]
        big_b = next((k for k, lv in enumerate(book.bids) if lv.volume >= WALL_BIG), None)
        big_a = next((k for k, lv in enumerate(book.asks) if lv.volume >= WALL_BIG), None)
        if big_b is not None and big_a is not None:
            kb, ka, wide = big_b, big_a, False
        else:                                             # 1000/750/500 ladder: the wide stocks
            kb = next((k for k, lv in enumerate(book.bids) if lv.volume >= WALL_SMALL), None)
            ka = next((k for k, lv in enumerate(book.asks) if lv.volume >= WALL_SMALL), None)
            wide = True
        if kb is None or ka is None:
            return None
        wb, wa = to_ticks(book.bids[kb].price, tick), to_ticks(book.asks[ka].price, tick)
        if not 2 <= wa - wb <= MAX_WALL_SPREAD:
            return None

        def inside(levels, k_wall, own):
            best = top = None
            cum = 0
            for lv in levels[:k_wall]:
                pt = to_ticks(lv.price, tick)
                other = lv.volume - (own["vol"] if own and own["px"] == pt else 0)
                if other > 0:
                    if top is None:
                        top = (pt, other)                 # best price that is not ours, and its size
                    cum += other
                    if best is None and cum >= COMP_VOL:
                        best = pt                         # best competing level with real size
            return best, top

        ob, tb = inside(book.bids, kb, mine["bid"])
        oa, ta = inside(book.asks, ka, mine["ask"])
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
        if last is not None and fair != last and abs(fair - last) <= MAX_JUMP:
            self.learn_phase(iid, now)
        self.wide[iid] = wide
        self.fair[iid], self.fair_at[iid] = fair, now
        hist = self.fair_hist[iid]
        hist.append((now, fair))
        while now - hist[0][0] > VOL_WINDOW_S:
            hist.popleft()
        if max(f for _, f in hist) - min(f for _, f in hist) >= VOL_PAUSE_TICKS:
            self.pause_until[iid] = now + VOL_PAUSE_S
        return {"fair": fair, "wb": wb, "wa": wa, "ob": ob, "oa": oa, "tb": tb, "ta": ta}

    def learn_phase(self, iid, now):
        """Fair-value changes arrive at a fixed fraction of each second; estimate it on our own clock."""
        self.chg[iid].append(now % 1.0)
        if len(self.chg[iid]) < PHASE_MIN_SAMPLES:
            return
        z = sum(cmath.exp(2j * math.pi * f) for f in self.chg[iid]) / len(self.chg[iid])
        if abs(z) >= PHASE_MIN_R:                          # tightly clustered: trust it
            self.phase[iid] = (cmath.phase(z) / (2 * math.pi) - self.loop_sleep / 2) % 1.0
        else:
            self.phase.pop(iid, None)

    def update_debts(self, now):
        """Each leader move is 'owed' by its follower; the follower's own moves pay it back."""
        dt, self.ll_t = now - self.ll_t, now
        for b, (a, beta) in LEADS.items():
            fa, fb = self.fair.get(a), self.fair.get(b)
            if fa is None or fb is None:
                continue
            pa, pb = self.ll_prev.get(b, (fa, fb))
            d = self.debt[b] + beta * (fa - pa) - (fb - pb)
            d -= math.copysign(min(abs(d), LL_LEAK * dt), d)
            d = max(-LL_CAP, min(LL_CAP, d))
            if abs(d) >= LL_MIN:
                if now - self.debt_since.setdefault(b, now) > LL_TIMEOUT:
                    d = 0.0                               # the follower never moved: forget it
                    self.debt_since.pop(b, None)
            else:
                self.debt_since.pop(b, None)
            self.debt[b] = d
            self.ll_prev[b] = (fa, fb)

    def in_blackout(self, iid, now):
        """True around the instant the walls of this (narrow) stock can move."""
        if not TICK_AWARE or self.wide[iid] or iid not in self.phase:
            return False
        d = (now - self.phase[iid]) % 1.0                  # seconds since the last expected move
        return d > 1.0 - max(TICK_PRE, self.loop_sleep + 0.08) or d < TICK_POST

    def reservation(self, iid, b):
        """Fair value leaned against our inventory (own position plus a share of the correlated partner's)."""
        p = self.pos[iid]
        if USE_PAIRS and iid in PAIR_WEIGHT and PAIR_WEIGHT[iid][0] in self.pos:
            p += PAIR_WEIGHT[iid][1] * self.pos[PAIR_WEIGHT[iid][0]]
        x = max(-1.5, min(1.5, p / self.soft_cap(iid)))
        return b["fair"] + self.debt.get(iid, 0.0) - (SKEW_LIN * x + SKEW_CUB * x ** 3)

    def targets(self, iid, b, r, reduce_only):
        """-> (bid, bid_size, ask, ask_size) in ticks and lots."""
        pos, wb, wa, cap = self.pos[iid], b["wb"], b["wa"], self.soft_cap(iid)
        edge = MIN_EDGE_WIDE if self.wide[iid] else MIN_EDGE_NARROW
        ask = math.ceil(r + edge - 1e-9)                               # closest to fair we are willing to sell
        bid = math.floor(r - edge + 1e-9)
        no_ask, no_bid = ask > wa, bid < wb                            # our price would be behind the wall: do not quote
        now = time.time()
        if PENNY:                                                      # do not give away more edge than needed
            ask = max(ask, (b["oa"] if b["oa"] is not None else wa) - 1)
            bid = min(bid, (b["ob"] if b["ob"] is not None else wb) + 1)
        ask = max(min(ask, wa), wb + 1)                                # stay between the walls
        bid = min(max(bid, wb), wa - 1)
        if bid >= ask:                                                 # cannot happen with a positive edge; be safe
            bid = ask - 1
        bid_size = max(0, min(QUOTE_SIZE, cap - pos))
        ask_size = max(0, min(QUOTE_SIZE, cap + pos))
        if iid in PASSIVE_OFF and not reduce_only:
            bid_size = ask_size = 0
        if no_bid or now < self.side_block.get((iid, "bid"), 0):
            bid_size = 0
        if no_ask or now < self.side_block.get((iid, "ask"), 0):
            ask_size = 0
        if reduce_only:
            bid_size, ask_size = min(bid_size, max(0, -pos)), min(ask_size, max(0, pos))
        elif bid_size < MIN_SIZE or ask_size < MIN_SIZE:
            bid_size, ask_size = (0 if bid_size < MIN_SIZE else bid_size), (0 if ask_size < MIN_SIZE else ask_size)
        return bid, bid_size, ask, ask_size

    # ----------------------------------------------------------------- actions
    def manage_side(self, iid, side, px, size, now, deletes, inserts):
        """Queue the delete / insert needed to make our order on `side` match (px, size)."""
        o = self.my[iid][side]
        if o:
            if o["px"] == px and size > 0 and size / 2 <= o["vol"] <= size:
                return                                    # leave it: keeps its place in the queue
            # urgent: resting more than we may now hold, or priced closer to fair than we accept (stale after a move)
            urgent = size == 0 or o["vol"] > size or (o["px"] > px if side == "bid" else o["px"] < px)
            if not urgent and now - o["t"] < MIN_REQUOTE_S:
                return
            deletes.append((0 if urgent else 1, iid, side))
        if size > 0:
            inserts.append((iid, side, px, size))

    def take(self, iid, b, r, now, reduce_only):
        """Hit a resting quote that sits on the wrong side of our reservation price by the take edge."""
        if not TAKE or now - self.last_take[iid] < TAKE_COOLDOWN:
            return
        pos, cap = self.pos[iid], self.soft_cap(iid)
        need = TAKE_EDGE_WIDE if self.wide[iid] else TAKE_EDGE_NARROW
        tb, ta = b["tb"], b["ta"]
        if iid in LEADS and not reduce_only:                            # follower: its wall is about to move
            if (not ta or r - ta[0] < need) and r - b["wa"] >= LL_WALL_EDGE:
                ta = (b["wa"], LL_TAKE_SIZE)
            elif (not tb or tb[0] - r < need) and b["wb"] - r >= LL_WALL_EDGE:
                tb = (b["wb"], LL_TAKE_SIZE)
        big = LL_TAKE_SIZE if abs(self.debt.get(iid, 0.0)) >= 4 else TAKE_SIZE
        if tb and tb[0] - r >= need:                                    # someone bids above our value: sell to them
            resting = self.my[iid]["ask"]["vol"] if self.my[iid]["ask"] else 0
            vol = min(tb[1], big, max(0, pos if reduce_only else cap + pos - resting))
            if vol >= 1 and self.insert(iid, tb[0], vol, "ask", "ioc") is not None:
                self.last_take[iid] = now
                self.n_takes += 1
        elif ta and r - ta[0] >= need:                                  # someone offers below our value: buy from them
            resting = self.my[iid]["bid"]["vol"] if self.my[iid]["bid"] else 0
            vol = min(ta[1], big, max(0, -pos if reduce_only else cap - pos - resting))
            if vol >= 1 and self.insert(iid, ta[0], vol, "bid", "ioc") is not None:
                self.last_take[iid] = now
                self.n_takes += 1

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
            print(f"CUT {iid}: no reference price, position {pos} left open", flush=True)
            return
        self.last_cut[iid] = (now, pos)
        self.insert(iid, bound, vol, "ask" if pos > 0 else "bid", "ioc")

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
                print(f"KILL SWITCH: PnL {self.pnl:.1f} below -{MAX_LOSS}. Flattening and stopping.", flush=True)
        flatten = self.halted or left < FLATTEN_S
        reduce_only = left < REDUCE_ONLY_S
        deletes, inserts = [], []
        for iid in self.iids:                             # refresh every fair value before deciding anything
            self.read(iid, now)
        self.update_debts(now)
        for iid in self.iids:
            now = time.time()                             # order actions above may have taken time
            if now - self.last_ord_recon[iid] > RECONCILE_ORD_S:
                self.reconcile_orders(iid)
            b = self.read(iid, now)
            if b is None:
                self.walls_bad_since.setdefault(iid, now)
            else:
                self.walls_bad_since.pop(iid, None)
            pos = self.pos[iid]
            if flatten or abs(pos) >= HARD_CAP:
                if self.my[iid]["bid"] or self.my[iid]["ask"] or now - self.last_force_pull.get(iid, 0) > 1.0:
                    self.pace()
                    self.ex.delete_orders(iid)            # also removes any order we lost track of
                    self.my[iid] = {"bid": None, "ask": None}
                    self.last_force_pull[iid] = now
                self.cut(iid, b, 0 if flatten else self.soft_cap(iid) // 2, now)
                continue
            if b is None:                                 # walls unreadable: keep quotes briefly, then pull
                if now - self.walls_bad_since[iid] > WALL_GRACE_S:
                    self.pull(iid)
                continue
            if now < self.pause_until[iid]:               # fair is moving fast: stand aside
                self.pull(iid)
                continue
            r = self.reservation(iid, b)
            self.take(iid, b, r, now, reduce_only)
            if self.in_blackout(iid, now):                # the walls may move now: nothing of ours may rest
                self.pull(iid)
                continue
            bid, bsz, ask, asz = self.targets(iid, b, r, reduce_only)
            self.manage_side(iid, "bid", bid, bsz, now, deletes, inserts)
            self.manage_side(iid, "ask", ask, asz, now, deletes, inserts)
        for _, iid, side in sorted(deletes):              # stale quotes first, across all stocks
            self.cancel(iid, side)
        for iid, side, px, size in inserts:
            if self.my[iid][side] is None and not self.in_blackout(iid, time.time()):
                self.insert(iid, px, size, side)
        self.report(now, left)

    def show_feed(self, now):
        """Print social-media posts so we can see afterwards whether they precede the jumps. No trading effect."""
        if not self.feed_ok or now - self.last_feed < 0.5:
            return
        self.last_feed = now
        try:
            t = time.time()
            posts = self.ex.poll_new_social_media_feeds()
            if time.time() - t > 0.05:
                self.feed_ok = False                      # too slow to call inside the loop
            for post in posts or []:
                print(f"FEED {utc_now():%H:%M:%S} {getattr(post, 'post', post)!s:.200}", flush=True)
        except Exception as e:
            self.feed_ok = False
            print(f"feed disabled: {e!r}", flush=True)

    def report(self, now, left):
        self.show_feed(now)
        if now - self.last_state > 1.0:
            self.state_w.writerow([utc_now().isoformat(), round(self.pnl, 2), round(self.max_dd, 2)] + [self.pos[i] for i in self.iids]
                                  + [self.fair.get(i) for i in self.iids] + [round(self.debt.get(i, 0.0), 2) for i in self.iids])
            self.last_state = now
        if now - self.last_print > 5.0:
            run = max(1.0, now - self.t0)
            edge = self.edge_sum / self.lots if self.lots else 0.0
            pos = " ".join(f"{i}:{self.pos[i]:+d}" for i in self.iids)
            mode = "HALTED" if self.halted else "FLATTEN" if left < FLATTEN_S else "REDUCE" if left < REDUCE_ONLY_S else "ACTIVE"
            print(f"[{left:5.0f}s {mode}] pnl {self.pnl:8.1f} dd {self.max_dd:6.1f} | fills {self.n_fills} lots {self.lots} takes {self.n_takes} "
                  f"edge/lot {edge:+.2f}t | {self.n_actions / run:4.1f} act/s fails {self.n_fail} clocks {len(self.phase)} "
                  f"lead {' '.join(f'{k}:{v:+.1f}' for k, v in self.debt.items())} | {pos}", flush=True)
            self.fills_f.flush()
            self.state_f.flush()
            self.last_print = now

    def run(self):
        print(f"instruments: {self.iids}")
        t = time.time()
        for _ in range(50):
            self.ex.get_last_price_book(self.iids[0])
        ms = (time.time() - t) / 50 * 1000
        print(f"get_last_price_book takes {ms:.2f} ms per call (well under 1 ms = local read; several ms = network request)")
        if ms > 3:
            self.loop_sleep = max(self.loop_sleep, 0.2)
            print(f"book reads are slow -> loop sleep raised to {self.loop_sleep} s")
        self.reconcile_positions()
        for iid in self.iids:
            self.reconcile_orders(iid)
        print(f"start positions: {self.pos}  (PnL is shown relative to the start of this run)", flush=True)
        try:
            while True:
                if not self.ex.is_connected():
                    raise SystemExit("KICKED: another client connected with our credentials. Restart with --end.")
                if time.time() > self.t_end + 3:
                    break
                try:
                    self.step()
                except Exception as e:                    # never die mid-session; state is re-read on the next pass
                    print(f"ERROR in step: {e!r}", flush=True)
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
                  f"| takes {self.n_takes} | average edge {edge:+.2f} ticks per lot | order actions {self.n_actions} | failures {self.n_fail}")
            print(f"final positions {self.pos}")
            print(f"largest |position| per stock {self.max_pos}")
            print(f"learned clock phases {({k: round(v, 3) for k, v in self.phase.items()})}", flush=True)
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
