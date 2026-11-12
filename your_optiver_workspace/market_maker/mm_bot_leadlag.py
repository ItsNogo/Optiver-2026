"""mm_bot_leadlag.py - mm_bot.py plus a leader -> follower fair-value model.

Differences from mm_bot.py (same code otherwise; built from it by script, so its fixes carry over):
  1. BLACKOUT ON THE EXCHANGE CLOCK. The walls reprice 3 ms after each whole exchange second (narrow stocks)
     and 502 ms after it (CRWV, NBIS, SNDK). The bot measures its clock offset from book timestamps and pulls
     ALL quotes in one burst PULL_LEAD seconds before the narrow instant (guard(), run before every order
     action, so a slow pass cannot miss it). Narrow stocks are re-quoted 50 ms after it, followers 105 ms
     after it, because followers get picked off right after their LEADER moves. No resting order is sent
     that would land inside a blackout, and no takes happen inside one.
  2. LEADER -> FOLLOWER. NBIS follows AVGO, CRWV follows MU, SNDK follows NVDA (SNDK only after ~2 s). The
     still-expected part of the follower's move is added to its fair value (LAG_WEIGHTS, LEAD_SHRINK), so
     its quotes lean with the leader. After a leader JUMP the bot takes stale quotes inside the follower's
     walls (TAKE_EDGE_JUMP) and, if the predicted move clears the wall by TAKE_EDGE_WALL, the wall itself
     (TAKE_WALL, at most TAKE_WALL_SIZE lots, inventory stays under the soft cap). Exits are passive.
  3. PER-STOCK EDGES from the fill data: MIN_EDGE (quotes closer to fair lose after 30 s) and TAKE_EDGE
     (stale-quote takes only in AMD, AVGO, NBIS, CRWV, where they paid after costs).
Switches: LEADLAG, TAKE_WALL, LEADER_BLACKOUT, SCHEDULED_PULL. Order actions run at about 20 per second with
all 8 stocks; if the exchange throttles (FAIL lines, "fails" in the status line), restart with --only.

---- original description ----
mm_bot.py - tick-clock market maker and stale-quote taker for the 8 Optibook stocks.

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

    python mm_bot_leadlag.py --minutes 20      # run for 20 minutes from now
    python mm_bot_leadlag.py --end 20:20:00    # run until this UTC time (use this form after a restart)
    python mm_bot_leadlag.py --minutes 5 --only AVGO,NBIS,MU,CRWV,NVDA,SNDK

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
SOFT_CAP_NARROW, SOFT_CAP_WIDE = 40, 60   # passive fills and takes never push |position| above this
HARD_CAP = 80                        # if |position| ever gets here: cut to half the soft cap with a bounded IOC
QUOTE_SIZE = 20                      # the organizers' taker sends 20-lot orders
MIN_SIZE = 2                         # do not bother quoting less than this

WALL_BIG, WALL_SMALL = 2500, 700     # innermost ladder level: >= 2500 lots (narrow stocks) else >= 700 (wide stocks)
MIN_EDGE_NARROW = 0.5                # ticks between our quote and the inventory-adjusted fair value
MIN_EDGE_WIDE = 2.0                  # wide stocks: at least this, and at least wall_spread/2 - 3
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
JUMP_CONFIRM_S = 0.5
WALL_GRACE_S = 0.4                   # keep quotes this long while the walls are unreadable
VOL_PAUSE_TICKS = 4.0                # fair moved this much within VOL_WINDOW_S -> stand aside for VOL_PAUSE_S
VOL_WINDOW_S, VOL_PAUSE_S = 2.0, 1.0

LOOP_SLEEP = 0.05                    # seconds between passes (book reads look local; raise to 0.2 if throttled)
ACTION_GAP = 0.04                    # minimum seconds between two order actions: about 25 per second
MIN_REQUOTE_S = 0.4                  # a quote that is still acceptable is not moved more often than this
RECONCILE_POS_S = 1.0                # re-read positions and cash from the exchange this often
RECONCILE_ORD_S = 3.0                # re-read our resting orders per stock this often

REDUCE_ONLY_S = 120                  # last seconds: only quotes and takes that reduce inventory
FLATTEN_S = 45                       # last seconds: pull quotes and close positions with bounded IOCs
CUT_SLIP = 2                         # ticks through the wall a closing IOC may be priced
MAX_LOSS = 800.0                     # PnL since start (at fair value) below minus this: flatten everything and stop
STALE_BOOK_S = 5.0                   # a book whose timestamp has not changed for this long is not trusted
# Correlated pairs (30 s correlation ~0.9+): a share of the partner's inventory counts as our own for the skew.
USE_PAIRS = True
PAIR_WEIGHT = {"AVGO": ("NBIS", 0.2), "NBIS": ("AVGO", 0.6), "CRWV": ("MU", 0.4), "MU": ("CRWV", 0.4)}

# Leader -> follower model. LAG_WEIGHTS[follower][j] = follower ticks still expected per tick of leader move,
# when the follower has repriced j times since that leader move (j = 0: it has not reacted yet).
LEADLAG = True
LEADER = {"NBIS": "AVGO", "CRWV": "MU", "SNDK": "NVDA"}
# Measured on 127 leader jumps of 3+ ticks: NBIS ends ~0.39x the AVGO jump (0.20 at its first reprice), CRWV ~1.0x
# the MU jump (0.55 at its first reprice), SNDK ~0.42x the NVDA jump but only from its third reprice on.
LAG_WEIGHTS = {"NBIS": [0.45, 0.20, 0.08, 0.04], "CRWV": [1.20, 0.70, 0.35, 0.15], "SNDK": [0.44, 0.46, 0.46, 0.35, 0.20, 0.10]}
LEAD_SHRINK = 0.7                    # trust this fraction of the predicted drift
LEAD_MAX = 30.0                      # ticks; cap on the predicted drift
TICK_AWARE_WIDE = False              # (only used by the fallback when the exchange clock is unknown)
LEADER_BLACKOUT = True               # followers rest nothing around their LEADER's reprice instant (measured loss there)
LEAD_POST = 0.06                     # seconds after the leader's instant before a follower is quoted again
TAKE_WALL = True                     # after a leader jump, buy/sell the follower from its wall when the drift pays for it
TAKE_EDGE_WALL = 2.0                 # ...ticks by which the reservation price must clear the wall price
TAKE_WALL_SIZE = 40                  # lots per wall take (inventory stays under the soft cap)
LEAD_MIN_DRIFT = 2.0                 # wall takes need at least this much predicted drift (never inventory skew alone)
TAKE_EDGE_JUMP = 1.5                 # after a leader jump, take follower quotes this far on the wrong side of our value

# The walls reprice on the EXCHANGE clock: the five narrow stocks 3 ms after each whole second, the three wide
# (follower) stocks half a second later. Measured over 4 hours, unchanged by the exchange restart.
NARROW_SET = {"AMD", "AVGO", "MU", "NVDA", "VRT"}
WIDE_SET = {"CRWV", "NBIS", "SNDK"}
EXCH_PHASE = 0.003
SCHEDULED_PULL = True                # pull every quote in one burst shortly before that instant
PULL_LEAD = 0.16                     # seconds before the instant at which the burst starts
BURST_GAP = 0.005                    # seconds between the pulls of the burst
POST_NARROW, POST_FOLLOWER = 0.05, 0.105   # seconds after the instant before narrow / follower stocks are quoted again
# Minimum ticks between our quote and our value. Measured: fills closer than this lose after 30 s.
MIN_EDGE = {"AMD": 0.5, "AVGO": 0.5, "MU": 0.5, "VRT": 0.5, "NVDA": 1.0, "CRWV": 1.0, "NBIS": 1.0, "SNDK": 1.0}
# Stale-quote takes: only where they paid after costs. NVDA, SNDK, MU, VRT: no takes (SNDK only after a leader jump).
TAKE_EDGE = {"AMD": 1.0, "AVGO": 1.0, "NBIS": 1.5, "CRWV": 2.0}

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
        self.lead_moves = {i: deque() for i in self.iids}  # (local time, change in ticks) of each fair-value change
        self.jump_rec = {}                                 # jump candidates already passed to the follower model
        self.lag = deque(maxlen=400)                       # local time minus book timestamp: clock offset plus feed delay
        self.pulled_k = None                               # the reprice instant we already pulled for
        self.n_wall_takes = 0
        self.walls_bad_since = {}
        self.last_take = {i: 0.0 for i in self.iids}
        self.last_cut = {}
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
        self.fills_f = open("mm_fills.csv", "a", newline="")
        self.state_f = open("mm_state.csv", "a", newline="")
        self.fills_w, self.state_w = csv.writer(self.fills_f), csv.writer(self.state_f)
        self.fills_w.writerow(["utc", "instrument", "side", "price", "volume", "fair_ticks", "edge_ticks", "position", "trade_id"])
        self.state_w.writerow(["utc", "pnl", "max_drawdown"] + self.iids)

    def soft_cap(self, iid):
        return SOFT_CAP_WIDE if self.wide[iid] else SOFT_CAP_NARROW

    # ----------------------------------------------------------------- exchange calls
    def tick_phase(self):
        """Fraction of the LOCAL second at which the narrow walls reprice (followers: 0.5 s later). None if unknown."""
        if len(self.lag) >= 40:
            return (EXCH_PHASE + min(self.lag)) % 1.0      # smallest lag seen = clock offset plus the feed delay
        known = [self.phase[i] for i in self.iids if i in NARROW_SET and i in self.phase]
        return known[0] if known else None

    def guard(self):
        """Pull every resting quote in one burst just before the walls can move. Runs before each action and pass."""
        if not (TICK_AWARE and SCHEDULED_PULL):
            return
        ph = self.tick_phase()
        if ph is None:
            return
        now = time.time()
        if (now - ph) % 1.0 < 1.0 - PULL_LEAD:
            return
        k = math.floor(now - ph + PULL_LEAD)               # index of the reprice instant we are approaching
        if k == self.pulled_k:
            return
        self.pulled_k = k
        for iid in self.iids:
            mine = self.my[iid]
            if (mine["bid"] or mine["ask"]) and (LEADER_BLACKOUT or iid not in WIDE_SET):
                self.ex.delete_orders(iid)
                mine["bid"] = mine["ask"] = None
                self.n_actions += 1
                time.sleep(BURST_GAP)
        self.last_action = time.time()

    def pace(self):
        self.guard()
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
        if order_type == "limit" and self.in_blackout(iid, time.time() + self.action_gap):
            return None                                   # it would be resting when the walls move
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
        if ts is not None:
            try:
                self.lag.append(now - (ts.timestamp() if hasattr(ts, "timestamp") else float(ts)))
            except Exception:
                pass
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
            if self.jump_rec.get(iid) != cand:              # same new value seen on two passes: tell the follower model now
                self.jump_rec[iid] = cand
                self.lead_moves[iid].append((cand[1], fair - last))
            if now - cand[1] < JUMP_CONFIRM_S:
                return None
        self.jump.pop(iid, None)
        if last is not None and fair != last and abs(fair - last) <= MAX_JUMP:
            self.learn_phase(iid, now)
            self.lead_moves[iid].append((now, fair - last))
        self.wide[iid] = (iid in WIDE_SET) if iid in WIDE_SET or iid in NARROW_SET else wide
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

    def near_tick(self, iid, now, post):
        """True just before / after the learned instant at which this stock's walls can move."""
        if iid not in self.phase:
            return False
        d = (now - self.phase[iid]) % 1.0                  # seconds since the last expected move
        return d > 1.0 - max(TICK_PRE, self.loop_sleep + 0.08) or d < post

    def in_blackout(self, iid, now):
        """True while nothing of ours may rest: around this stock's reprice instant and, for a follower, its leader's."""
        if not TICK_AWARE:
            return False
        ph = self.tick_phase()
        if ph is not None:                                 # all blackouts hang off the narrow stocks' reprice instant
            d = (now - ph) % 1.0                           # seconds since it
            if iid in WIDE_SET or self.wide[iid]:          # follower: informed takers strike just after its leader moves
                return bool(LEADER_BLACKOUT) and (d > 1.0 - PULL_LEAD or d < POST_FOLLOWER)
            return d > 1.0 - PULL_LEAD or d < POST_NARROW
        if (TICK_AWARE_WIDE or not self.wide[iid]) and self.near_tick(iid, now, TICK_POST):
            return True
        lead = LEADER.get(iid)
        return bool(LEADLAG and LEADER_BLACKOUT and lead in self.tick and self.near_tick(lead, now, LEAD_POST))

    def drift(self, iid, now):
        """Follower only: ticks of fair-value move still expected from the leader's recent moves."""
        lead = LEADER.get(iid)
        if not LEADLAG or lead is None or lead not in self.lead_moves:
            return 0.0
        w, moves = LAG_WEIGHTS[iid], self.lead_moves[lead]
        while moves and now - moves[0][0] > len(w) + 1:
            moves.popleft()
        ph = self.phase.get(iid)
        total = 0.0
        for t_e, d in moves:
            if ph is not None:                             # follower reprices at local times congruent to ph (mod 1 s)
                j = math.floor(now - ph) - math.floor(t_e - ph)
            else:                                          # not learned yet: it reprices half a second after its leader
                j = math.floor(now - t_e + 0.5)
            if 0 <= j < len(w):
                total += d * w[j]
        return max(-LEAD_MAX, min(LEAD_MAX, LEAD_SHRINK * total))
    def reservation(self, iid, b, now):
        """Fair value (plus the move the leader predicts) leaned against our inventory and a share of the partner's."""
        p = self.pos[iid]
        if USE_PAIRS and iid in PAIR_WEIGHT and PAIR_WEIGHT[iid][0] in self.pos:
            p += PAIR_WEIGHT[iid][1] * self.pos[PAIR_WEIGHT[iid][0]]
        x = max(-1.5, min(1.5, p / self.soft_cap(iid)))
        return b["fair"] + self.drift(iid, now) - (SKEW_LIN * x + SKEW_CUB * x ** 3)

    def targets(self, iid, b, r, reduce_only):
        """-> (bid, bid_size, ask, ask_size) in ticks and lots."""
        pos, wb, wa, cap = self.pos[iid], b["wb"], b["wa"], self.soft_cap(iid)
        edge = MIN_EDGE.get(iid, max(MIN_EDGE_WIDE, (wa - wb) / 2 - 3) if self.wide[iid] else MIN_EDGE_NARROW)
        ask = math.ceil(r + edge - 1e-9)                               # closest to fair we are willing to sell
        bid = math.floor(r - edge + 1e-9)
        if PENNY:                                                      # do not give away more edge than needed
            ask = max(ask, (b["oa"] if b["oa"] is not None else wa) - 1)
            bid = min(bid, (b["ob"] if b["ob"] is not None else wb) + 1)
        ask = max(min(ask, wa), wb + 1)                                # stay between the walls
        bid = min(max(bid, wb), wa - 1)
        if bid >= ask:                                                 # cannot happen with a positive edge; be safe
            bid = ask - 1
        bid_size = max(0, min(QUOTE_SIZE, cap - pos))
        ask_size = max(0, min(QUOTE_SIZE, cap + pos))
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
        if iid in WIDE_SET or iid in NARROW_SET:
            need = TAKE_EDGE.get(iid)
        else:
            need = TAKE_EDGE_WIDE if self.wide[iid] else TAKE_EDGE_NARROW
        if LEADLAG and iid in LEADER and abs(self.drift(iid, now)) >= LEAD_MIN_DRIFT:
            need = TAKE_EDGE_JUMP                         # the leader just jumped: quotes inside this follower's walls are stale
        if need is None:
            return
        tb, ta = b["tb"], b["ta"]
        if tb and tb[0] - r >= need:                                    # someone bids above our value: sell to them
            resting = self.my[iid]["ask"]["vol"] if self.my[iid]["ask"] else 0
            vol = min(tb[1], TAKE_SIZE, max(0, pos if reduce_only else cap + pos - resting))
            if vol >= 1 and self.insert(iid, tb[0], vol, "ask", "ioc") is not None:
                self.last_take[iid] = now
                self.n_takes += 1
        elif ta and r - ta[0] >= need:                                  # someone offers below our value: buy from them
            resting = self.my[iid]["bid"]["vol"] if self.my[iid]["bid"] else 0
            vol = min(ta[1], TAKE_SIZE, max(0, -pos if reduce_only else cap - pos - resting))
            if vol >= 1 and self.insert(iid, ta[0], vol, "bid", "ioc") is not None:
                self.last_take[iid] = now
                self.n_takes += 1
        elif LEADLAG and TAKE_WALL and iid in LEADER and not reduce_only:
            d = self.drift(iid, now)                                    # the leader jumped: trade the follower's catch-up
            if d >= LEAD_MIN_DRIFT and r - b["wa"] >= TAKE_EDGE_WALL:
                side, px, vol, own = "bid", b["wa"], min(TAKE_WALL_SIZE, cap - pos), "ask"
            elif d <= -LEAD_MIN_DRIFT and b["wb"] - r >= TAKE_EDGE_WALL:
                side, px, vol, own = "ask", b["wb"], min(TAKE_WALL_SIZE, cap + pos), "bid"
            else:
                return
            if vol >= 1:
                self.cancel(iid, own)                                   # our own quote on that side would block the order
                if self.insert(iid, px, vol, side, "ioc") is not None:
                    self.last_take[iid] = now
                    self.n_takes += 1
                    self.n_wall_takes += 1
                    print(f"WALL TAKE {iid} {side} {vol}@{px} drift {d:+.1f}t pos {pos:+d}", flush=True)

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
        self.guard()
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
            if self.in_blackout(iid, now):                # the walls may move now: nothing of ours may rest, no takes
                self.pull(iid)
                continue
            r = self.reservation(iid, b, now)
            self.take(iid, b, r, now, reduce_only)
            bid, bsz, ask, asz = self.targets(iid, b, r, reduce_only)
            self.manage_side(iid, "bid", bid, bsz, now, deletes, inserts)
            self.manage_side(iid, "ask", ask, asz, now, deletes, inserts)
        for _, iid, side in sorted(deletes):              # stale quotes first, across all stocks
            self.cancel(iid, side)
        for iid, side, px, size in inserts:
            if self.my[iid][side] is None and not self.in_blackout(iid, time.time()):
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
            mode = "HALTED" if self.halted else "FLATTEN" if left < FLATTEN_S else "REDUCE" if left < REDUCE_ONLY_S else "ACTIVE"
            print(f"[{left:5.0f}s {mode}] pnl {self.pnl:8.1f} dd {self.max_dd:6.1f} | fills {self.n_fills} lots {self.lots} takes {self.n_takes} "
                  f"edge/lot {edge:+.2f}t | {self.n_actions / run:4.1f} act/s fails {self.n_fail} clocks {len(self.phase)} | {pos}", flush=True)
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
    print(f"now {now:%H:%M:%S} UTC, trading until {end:%H:%M:%S} UTC. If you have to restart, run:  python mm_bot_leadlag.py --end {end:%H:%M:%S}")
    if end <= now:
        raise SystemExit("end time is in the past")
    ex = Exchange(max_nr_trade_history=5000)
    ex.connect()
    if not ex.is_connected():
        raise SystemExit("not connected")
    Bot(ex, end.timestamp(), set(a.only.split(",")) if a.only else None).run()


if __name__ == "__main__":
    main()
