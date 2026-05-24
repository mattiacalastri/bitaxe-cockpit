# 🐙 Bitaxe Cockpit

> A live TUI cockpit for [Bitaxe](https://bitaxe.org) solo Bitcoin miners — Italian-first, dark theme, gamified, with animated ASCII title and real-time mining intelligence.

Built on [Textual](https://textual.textualize.io) for the terminal. Polls the AxeOS REST API of your Bitaxe and renders 8 panels of live telemetry: hashrate, thermal, mining progress, lottery odds, power & energy cost, pool & wallet integrity, system info, and quick reference.

## ✨ Features

- **Animated ASCII title** — BITAXE logo with traveling wave gradient (4 Hz refresh)
- **Live hashrate sparkline** + 60s history + J/TH efficiency
- **Thermal monitor** — ASIC junction + VRM regulator + margin guard rails
- **Solo lottery odds** — block probability per day, expected ETA, reward estimate in BTC/EUR
- **Energy cost calculator** — €/month + €/year at user-configurable kWh rate
- **Wallet integrity check** — detects "vendor pre-config trap" (Bitaxe sold with vendor's stratumUser still active)
- **Bitcoin network block height** — live from `mempool.space` every 60s
- **Uptime milestone badges** 🥉 1h+ · 🥈 24h+ · 🥇 7g+ · 🏆 30g+
- **Gamified manual refresh** — `r` key tracks counter, streak (latency < 60 ms), best response, easter eggs at 21/100/333 refreshes
- **4 themes** — Polpo (default), Bitcoin, Mono, Hacker (cycle with `t`)
- **Educational tooltips** — rotating tips explain hashrate, J/TH, solo mining, VRM bottleneck, etc.
- **CSV history export** — every poll appended to `~/.local/share/bitaxe_cockpit/history.csv`
- **SVG snapshot** with `s` key
- **Italian-first UI** — all labels, tooltips, notifications in Italian (English contributions welcome)

## 🖼 Screenshot

```
 ██████╗ ██╗████████╗ █████╗ ██╗  ██╗███████╗
 ██╔══██╗██║╚══██╔══╝██╔══██╗╚██╗██╔╝██╔════╝
 ██████╔╝██║   ██║   ███████║ ╚███╔╝ █████╗
 ██╔══██╗██║   ██║   ██╔══██║ ██╔██╗ ██╔══╝
 ██████╔╝██║   ██║   ██║  ██║██╔╝ ██╗███████╗

       ◆ COCKPIT ◆   Monitor Live · Bitcoin Solo Miner
              ⏱ 09:37:24   ·   ⛏ blocco #872,451

  ● LIVE  •  ⚡ 1.15 TH/s ▂▃▄▅▆▇  •  🌡 62°C  •  🔋 18W
            •  ✓ 3610 share  •  ⏱ 9h 37m  🥉 1h+
```

(See `docs/screenshots/` for full renderings.)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A Bitaxe miner on your LAN (any model: 401, 601 Gamma, 701 Ultra…)
- Ghostty terminal (optional, for the .app wrapper) or any modern terminal with Unicode + truecolor support

### Install

```bash
git clone https://github.com/<you>/bitaxe-cockpit.git
cd bitaxe-cockpit
pip install -e .
```

Or with `uv`/`uvx`:

```bash
uvx --from . bitaxe-cockpit
```

### Run

```bash
# Default: tries bitaxe.local (mDNS)
bitaxe-cockpit

# Explicit host
bitaxe-cockpit --host 192.168.1.64

# Custom refresh interval
bitaxe-cockpit --host 192.168.1.64 --interval 2.0
```

Or via environment variables:

```bash
export BITAXE_HOST=192.168.1.64
export BITAXE_WALLET_PREFIX=bc1qxxx      # first 8 chars of your address
export BITAXE_REFRESH_SEC=5.0
bitaxe-cockpit
```

## 🛡 Wallet Integrity Check (Anti vendor-trap)

Bitaxe vendors sometimes pre-configure your device with **their** Bitcoin address as `stratumUser`, so any block your unit hashes goes to **them** instead of you. This is a known commercial pattern at crypto events.

Set `BITAXE_WALLET_PREFIX` to the first ~8 characters of your own BTC address:

```bash
export BITAXE_WALLET_PREFIX=bc1qxxx
```

The cockpit polls `/api/system/info` and checks that `stratumUser` contains your prefix. If a vendor wallet is detected, the Pool & Wallet panel flags it red:

```
Wallet  VENDOR ❌
```

**Always also verify via WebSocket** — see `scripts/ws_check.py` for the canonical check (catches post-PATCH "API shows new config but runtime still uses old wallet" cases).

## ⌨️ Keybindings

| Key   | Action                              |
| ----- | ----------------------------------- |
| `r`   | Refresh now (manual, gamified)      |
| `p`   | Pause / resume auto-refresh         |
| space | Single-step refresh (while paused)  |
| `t`   | Cycle themes                        |
| `s`   | Save SVG snapshot                   |
| `e`   | Show CSV history path               |
| `+/-` | Faster / slower poll interval       |
| `o`   | Open AxeOS web UI in browser        |
| `?` `h` | Open / close help overlay         |
| `q`   | Quit                                |

## 📊 Panels

| Panel              | Color   | Content                                                 |
| ------------------ | ------- | ------------------------------------------------------- |
| ⚡ Hashrate        | Orange  | Live TH/s, expected, perf%, J/TH, 60s sparkline         |
| 🌡 Temperatura     | Red     | ASIC + VRM gauges, dual sparkline, fan, margin          |
| ⛏ Mining           | Gold    | Share OK/KO, reject reasons, share/min, best diff       |
| 🎰 Lotteria        | Magenta | Network share, P(block)/day, ETA, reward BTC + EUR      |
| 🔋 Alimentazione   | Cyan    | Power gauge, voltage, current, freq, headroom, €/month  |
| 🏊 Pool & Wallet   | Green   | Primary/fallback status, latency sparkline, wallet check|
| 📡 Sistema         | Blue    | Hostname, MAC, RSSI sparkline, firmware, heap, uptime   |
| 📘 Legenda         | White   | Keybindings, thresholds, quick reference                |

## 🔧 Configuration

### Environment variables

| Variable                  | Default              | Purpose                              |
| ------------------------- | -------------------- | ------------------------------------ |
| `BITAXE_HOST`             | `bitaxe.local`       | Bitaxe IP or mDNS hostname           |
| `BITAXE_REFRESH_SEC`      | `5.0`                | Poll interval in seconds             |
| `BITAXE_WALLET_PREFIX`    | (empty)              | First ~8 chars of your BTC address  |

### Data storage

- **CSV history**: `~/.local/share/bitaxe_cockpit/history.csv`
- **SVG snapshots**: `~/.local/share/bitaxe_cockpit/snapshots/`

## 🏗 Architecture

```
bitaxe_cockpit.py        ← Textual App + 11 widgets (1 file, ~1400 lines)
bitaxe_cockpit.tcss      ← Textual CSS (themes, layout, gauges)
bitaxe_ghostty_wrapper.c ← Optional macOS .app launcher (Ghostty fullscreen)
```

Polls `GET http://<host>/api/system/info` every N seconds, decodes into a `BitaxeState` dataclass, reactive watchers update each panel. Manual `r` press triggers immediate poll + gamification tracking.

## 🛠 Building the macOS .app (optional)

```bash
clang -O2 -arch arm64 -o ghostty bitaxe_ghostty_wrapper.c
# Then bundle into a standard macOS .app with:
# - ghostty (this wrapper)
# - ghostty.bin (real Ghostty binary)
# - bitaxe_cockpit.py + .tcss
# - Info.plist with CFBundleIdentifier=org.bitaxe.cockpit
```

## 🤝 Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

Ideas wanted:
- mDNS auto-discovery of Bitaxe on LAN
- Webhook alerts (Telegram / Discord / generic POST)
- Multi-device dashboard (`--hosts ip1,ip2,ip3`)
- Prometheus `/metrics` exporter
- Block height refinements (mining diary log book)
- Localization to English / Spanish / German

## 📜 License

MIT — see [LICENSE](LICENSE).

## 🐙 Credits

Forged in the wild by [Polpo OS](https://github.com/mattiacalastri) — sess.2210 (first Bitaxe acquired at Bitcare Forum Brescia, May 2026), polished sess.2214 (gamification + animated wave + Italian-first + OSS hardening).

The Bitaxe community: [@skot](https://github.com/skot/ESP-Miner) for AxeOS firmware, [bitaxeorg](https://github.com/bitaxeorg) for open hardware, [Home Mining Italia](https://homeminingitalia.org) for the pool that started it all.

🐙⚔️🎩
