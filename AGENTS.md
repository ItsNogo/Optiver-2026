# Optibook Workspace

This workspace is for building Python trading bots on Optibook, a simulated
trading exchange. You trade against other teams' bots on a live order book.

## Environment

- Python: `/opt/venv/bin/python` (preselected). `pip install` works out of the box.
- The `optibook` client library is preinstalled.
- Credentials are picked up automatically — construct `Exchange()` with no
  arguments.
- `your_optiver_workspace/` is on `PYTHONPATH`, so `from common.libs import ...`
  works from anywhere.

## Connecting

```python
from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()
```

## Exchange rules (these bite)

- **One connection per team.** Connecting kicks any existing connection,
  including a teammate's. A kicked client does not crash loudly — check
  `exchange.is_connected()`. A "someone was already connected" message on
  connect is normal, not an error — you are connected.
- **Cancel on disconnect.** When your program stops, all your outstanding
  orders are pulled automatically. Positions remain.
- **Position limits per instrument.** Trades that would exceed the limit are
  rejected. Limits vary per challenge — check the challenge description.
- **Positions never expire or reset.** The only way out of a position is to
  trade out of it. Positions are per instrument and cannot be transferred
  between related instruments (e.g. the two legs of a dual listing) — trade
  out of each leg directly.
- **PnL** = realized cash plus current positions valued at the last traded
  price. `get_pnl()` computes this; pass a `valuations` dict to value
  positions differently (mid-point, theoretical, etc.).
- **No fill notifications.** Poll `poll_new_trades(instrument_id)` or watch
  `get_positions()` to detect fills.
- **Rate limits.** The exchange throttles request rates per team across all
  instruments. Pace polling loops — always `time.sleep()` in a loop iteration
  (0.2s or more).
- **Price change limits.** Orders priced too far from the last traded price
  are rejected (`instrument.price_change_limit`: `absolute_change`,
  `relative_change`).
- **Price limits.** Some instruments carry fixed bounds
  (`instrument.price_limit`: `min`, `max`, inclusive; `None` = unlimited).
  An order outside them comes back with `success=False` and the reason in
  `error_reason`; check the response instead of assuming the insert worked.
  If the limit changes later, your resting orders outside the new range are
  cancelled by the exchange, so re-read `get_outstanding_orders` rather than
  trusting a local list.
- **No historical snapshot.** Trade tick and private trade history start when
  your client connects.
- Prices must be on the instrument's `tick_size` grid. Order sides are
  `'bid'`/`'ask'`; order types are `'limit'`/`'ioc'`.
- **Fixed order range.** Every order must have a price in `[0, 1000000]` and
  a volume in `[1, 100000]`, whatever the instrument's limits. Outside that
  the insert (or amend) comes back with `success=False` and the reason.

## Defensive idioms

Order books can be empty and requests can fail — always check:

```python
book = exchange.get_last_price_book(instrument_id)
if book and book.bids:
    best_bid = book.bids[0].price

response = exchange.insert_order(instrument_id, price=10.0, volume=5,
                                 side='bid', order_type='limit')
if not response.success:
    print(response.error_reason)
```

Discover instruments at runtime with `exchange.get_tradable_instruments()`
instead of hardcoding ids.

## Historical data

Past trades, orders and pricebooks can be downloaded with
`optibook.historical_data_loader.HistoricalDataLoader` (full docs in the API
reference). Only available when the event exposes a historical-data API.

```python
from optibook.historical_data_loader import HistoricalDataLoader

loader = HistoricalDataLoader()          # host + credentials picked up automatically
df = loader.get_trades_df(start, end)    # pandas DataFrame
```

Loads are capped at 1 day per call; for longer ranges `download_all()` first,
then load day-sized chunks. Counterparty names are anonymized unless the
organizers open a counterparty data window.

## Directory map

- `api_reference.md` — **full client API reference. Read this before writing
  code against the client.**
- `your_optiver_workspace/` — your code lives here, one folder per challenge:
  - `dual_listing/`, `stock_future/`, `etf_future/`, `options_market_making/`
    — challenge folders, each with a `*_template.py` (worked example) and a
    `your_*_algo.py` (starting point for your own bot).
  - `common/` — shared helpers (e.g. `black_scholes.py`).
  - `optibook_guides/` — documentation:
    - `code_snippets.ipynb` — runnable examples of every core call.
    - PDF guides for background reading.

## Working conventions

- Put new bot code in the relevant challenge folder.
- **Run bots as plain Python scripts** (`python your_algo.py`), never in a
  Jupyter notebook — notebooks hang when a bot prints lots of output. Use
  notebooks for exploration only, not for running bots.
- Long-running bots should be resilient: reconnect logic is not needed
  (crash and restart is fine), but always handle empty books and failed
  requests without crashing.
