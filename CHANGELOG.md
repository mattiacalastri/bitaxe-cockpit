# Changelog

All notable changes to **Bitaxe Cockpit** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Planned:
- mDNS auto-discovery of Bitaxe miners on LAN
- Webhook alerts (Telegram / Discord / generic POST)
- Multi-device dashboard (`--hosts ip1,ip2,ip3`)
- Prometheus `/metrics` HTTP endpoint
- WebSocket streaming live (`/api/ws`) replacing REST polling

## [0.1.0] — 2026-05-24

First public release.

### Added
- 8 live panels (Hashrate, Thermal, Mining, Lottery, Power, Pool & Wallet, System, Legend)
- Animated ASCII BITAXE title with traveling wave gradient (4 Hz)
- Live Bitcoin block height from `mempool.space`
- Mini sparkline hashrate inline in KPI header line
- Uptime milestone badges (🥉 1h+ · 🥈 24h+ · 🥇 7g+ · 🏆 30g+)
- Gamified manual refresh (`r` key) with counter, streak system, best-latency tracker, 5 easter eggs
- Wallet integrity check (anti vendor pre-config trap)
- 4 themes (Polpo / Bitcoin / Mono / Hacker), cycle with `t`
- CSV history export to `~/.local/share/bitaxe_cockpit/history.csv`
- SVG snapshot with `s` key
- Rotating educational tooltips in header (16 tips, 8s rotation)
- Soft word-wrap helper preserving Rich markup (for EXPLAIN tooltips)
- macOS .app Ghostty wrapper (`bitaxe_ghostty_wrapper.c`)
- Full Italian-first UI

### Security / Privacy
- All hardcoded personal data removed (wallet prefix, host IP, hostname) — now env-configurable
- `BITAXE_WALLET_PREFIX` env var enables wallet check; if unset, check is disabled (no false positives for fresh installs)
- Ghostty wrapper resolves script path dynamically (no hardcoded `/Users/<name>` paths)

### Doctrine notes (for fork maintainers)
- Static widgets require `expand=True` for proper text-wrap in fixed-height containers
- `text-wrap: wrap` TCSS is necessary but not sufficient — must combine with `width: 100%` + `expand=True`
- When a panel's content exceeds its grid-row height, Textual silently inhibits word-wrap — use `grid-rows: auto` + `height: auto` on the panel for natural fit, or `soft_wrap()` helper for explicit pre-wrap preserving markup
