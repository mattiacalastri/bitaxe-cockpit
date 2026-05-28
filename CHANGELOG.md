# Changelog

All notable changes to **Bitaxe Cockpit** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Planned:
- Multi-device dashboard (`--hosts ip1,ip2,ip3`)
- Prometheus `/metrics` HTTP endpoint
- WebSocket streaming live (`/api/ws`) replacing REST polling
- Mining diary log book (best diff break log, downtime events, restart history)
- Localization to English / Spanish / German

## [0.3.0] — 2026-05-28

### Added — UX 3-layer redesign sess.2622

- **Arc Gauge braille primitive** — 4 dial semicircolari ASCII via Unicode Braille
  (2x4 sub-pixel per cella, range U+2800-28FF) per HASHRATE / ASIC TEMP / VRM / POWER.
  Layout 1x4 inline orizzontale (`#arc-grid` TCSS), threshold cascade verde/amber/rosso
  con lancetta Bresenham + arco fill proporzionale.
- **Translator inline** sotto ogni ArcGauge — paragoni umani per non-crypto-savvy:
  - HASHRATE: "Il chip prova {N} password al secondo · lavoro di ~{M} MacBook Pro M3"
  - ASIC: "Il silicio è {tisana/doccia/tè/acqua bollente/pasta scolata}" (threshold cascade)
  - VRM: "Il VRM converte 5V→0.4V — {fan al massimo/medio/tranquillo}"
  - POWER: "Consuma come una {smartphone/lampadina LED/alogena} · Costo €{X}/mese · €{Y}/anno"
- **Story Mode panel** — pannello narrativo italiano umano (zero jargon crypto):
  uptime + tentativi totali in unità grandi ("123 quadrilioni di combinazioni"),
  probabilità vittoria (1 su X, ETA secoli/millenni), earnings reali (vincita teorica
  €296k vs costo elettricità €40/anno + EV statistico €0.012/anno), reality grounding
  (78 Bitaxe singoli al mondo hanno trovato blocchi negli ultimi 2 anni), scala
  mondiale tier (Hobby/Enthusiast/Pro/Industrial con auto-detect posizione).
- **Toggle key `d`** — drilldown panel testuali on-demand (default VISIBILE,
  premi per nascondere e lasciare solo Story Mode + dial).

### Changed

- **Dogfooding [polpo-tui-toolkit](https://github.com/mattiacalastri/polpo-tui-toolkit)** —
  `polpo_arc_gauge.py` ora è shim che importa da sibling library invece di copia inline.
  Backward compat preservato (`from polpo_arc_gauge import ArcGauge` continua a funzionare).
  Pattern DRY cross-progetto per future TUI Polpo (m5-watcher, BTC cockpit, MRR, Health).
- **Layout grid** — `#main-grid` 2x7 → 2x5 (drilldown row dedicate, ArcGauge in
  `#arc-grid` separato 4x1 hero row).

### Fixed

- 25° substrato sintattico ≠ funzionale: 2 file `bitaxe_cockpit.py` divergenti
  coesistevano (repo community vs `~/scripts/` production Mattia). Backport mirato
  ricongiunge ArcGauge + StoryMode + binding `d`. Vedi cicatrice memory satellite.

## [0.2.0] — 2026-05-24

### Added
- **mDNS auto-discovery** of Bitaxe miners on LAN via `zeroconf`
  - `--discover` flag forces interactive selection
  - `--list` flag prints found miners + exits
  - Auto-runs when no `--host` and no `BITAXE_HOST` env var
  - Filters service names containing `bitaxe` / `axe` / `esp32`
- **Webhook alerts** (`WebhookNotifier`) — async fire-and-forget push to:
  - Telegram bot (`BITAXE_TG_TOKEN` + `BITAXE_TG_CHAT_ID`)
  - Discord webhook (`BITAXE_DISCORD_URL`)
  - Generic JSON POST (`BITAXE_WEBHOOK_URL`)
- **Alert events**: ASIC > 70°C, VRM > 80°C, overheat firmware mode, Bitaxe unreachable (3 consecutive failures), new lifetime best diff, uptime milestones (1h/24h/7d/30d)
- Per-event cooldown (default 5–15 min) prevents spam
- Optional `[discovery]` install extra for users wanting mDNS

### Changed
- `zeroconf` is now an **optional** dependency — graceful import error if missing
- `pyproject.toml` adds `[project.optional-dependencies] discovery` and `all`

## [0.1.0] — 2026-05-24

First public release.

### Added
- 8 live panels (Hashrate, Thermal, Mining, Block Hunt, Power, Pool & Wallet, System, Legend)
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
