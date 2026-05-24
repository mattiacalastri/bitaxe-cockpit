# Contributing to Bitaxe Cockpit

Grazie per l'interesse 🐙

## Development setup

```bash
git clone https://github.com/<you>/bitaxe-cockpit.git
cd bitaxe-cockpit
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Run against your Bitaxe:

```bash
export BITAXE_HOST=192.168.1.X
export BITAXE_WALLET_PREFIX=bc1qxxx
python bitaxe_cockpit.py
```

## Testing without a real Bitaxe

The cockpit hits `GET /api/system/info`. A canonical sanitized AxeOS payload
lives at `tests/fixtures/api/system/info.json`. To run the cockpit against a
mock server:

```bash
mkdir -p /tmp/bitaxe-mock/api/system
cp tests/fixtures/api/system/info.json /tmp/bitaxe-mock/api/system/info
cd /tmp/bitaxe-mock
python -m http.server 8080 &
BITAXE_HOST=localhost:8080 bitaxe-cockpit
```

Or in `tests/`, the `axeos_system_info` fixture (in `conftest.py`) loads the
JSON and is available to all tests:

```python
def test_my_panel(axeos_system_info):
    state = BitaxeState.from_api(axeos_system_info, response_ms=42.0)
    # ... your assertions
```

Run the test suite:

```bash
pytest tests/ -v
```

## Code style

- Line length 120 (`ruff format`)
- All UI strings live in source as **single concatenated strings without manual `\n`** — wrap is delegated to `soft_wrap()` runtime helper
- Italian-first labels in UI; English in docstrings, comments, code identifiers, README
- Each `Static` subclass should pass `expand=True` to `super().__init__()` to ensure proper `text-wrap` in Textual

## Adding a new panel

1. Subclass `Static`, set `add_class("panel")`, pass `expand=True`
2. Reactive `state: reactive[Optional[BitaxeState]] = reactive(None)`
3. Implement `watch_state` + `refresh_panel`
4. Append to grid in `BitaxeCockpit.compose()`
5. Add color rule in `bitaxe_cockpit.tcss` (e.g. `#mynew-panel { border: solid #XXXXXX; background: #YYYYYY; }`)
6. Update `update_all_panels()` if grouping in fast/slow adaptive rate

## Pull request checklist

- [ ] Code runs against a real Bitaxe (or documented mock)
- [ ] No hardcoded personal IPs, wallet prefixes, hostnames
- [ ] All new UI strings translatable (lift to module-level constants where reasonable)
- [ ] CHANGELOG.md updated
- [ ] Screenshots attached if UI changed
- [ ] `ruff check .` passes

## Code of Conduct

Be civil. The Bitcoin / open-hardware community thrives on respect. Personal attacks, harassment, or sectarian gatekeeping are not welcome. Otherwise — bring your weird ideas. The animated BITAXE wave started as one.

## Reporting bugs

Open an issue with:
- Bitaxe model + AxeOS firmware version (`/api/system/info` output)
- Terminal emulator + Textual version
- macOS / Linux distro
- Exact reproduction steps
- Screenshot if visual

🐙
