<div align="center">

```
 ██████╗ ██╗████████╗ █████╗ ██╗  ██╗███████╗     ██████╗ ██████╗  ██████╗██╗  ██╗██████╗ ██╗████████╗
 ██╔══██╗██║╚══██╔══╝██╔══██╗╚██╗██╔╝██╔════╝    ██╔════╝██╔═══██╗██╔════╝██║ ██╔╝██╔══██╗██║╚══██╔══╝
 ██████╔╝██║   ██║   ███████║ ╚███╔╝ █████╗      ██║     ██║   ██║██║     █████╔╝ ██████╔╝██║   ██║
 ██╔══██╗██║   ██║   ██╔══██║ ██╔██╗ ██╔══╝      ██║     ██║   ██║██║     ██╔═██╗ ██╔═══╝ ██║   ██║
 ██████╔╝██║   ██║   ██║  ██║██╔╝ ██╗███████╗    ╚██████╗╚██████╔╝╚██████╗██║  ██╗██║     ██║   ██║
 ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝     ╚═════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝

           ◆  L I V E   T E R M I N A L   C O C K P I T   F O R   S O L O   B T C   M I N E R S  ◆
```

**See every share. Sniff the vendor trap. Celebrate every milestone.**

A terminal-native flight deck for [Bitaxe](https://bitaxe.org) solo Bitcoin miners — animated, gamified, Italian-first, and paranoid in all the right places.

![Bitaxe Cockpit live TUI dashboard — Gamma 601 BM1370 solo Bitcoin miner monitor with animated traveling-wave BITAXE header, hashrate + thermal + share + block-find panels, dark Polpo theme](docs/cockpit-onda-hero.gif)

<sub>*14 s loop · live capture on a Gamma 601 BM1370 ASIC at 1.07 TH/s, hashing solo to `homeminingitalia.org:3333` · animated header travels in real time, all 8 panels reactive on 5 s poll. Full static capture below.*</sub>

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Version v0.3.0](https://img.shields.io/badge/version-v0.3.0-F7931A?style=flat-square)](CHANGELOG.md)
[![CI](https://img.shields.io/github/actions/workflow/status/mattiacalastri/bitaxe-cockpit/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/mattiacalastri/bitaxe-cockpit/actions)
[![Built with Textual](https://img.shields.io/badge/built%20with-Textual-7B2CBF?style=flat-square)](https://textual.textualize.io)
[![Bitaxe Compatible](https://img.shields.io/badge/Bitaxe-401%20%7C%20Gamma%20601%20%7C%20Ultra%20701-F7931A?style=flat-square)](https://bitaxe.org)
[![Forged by Polpo OS](https://img.shields.io/badge/forged%20by-%F0%9F%90%99%20Polpo%20OS-1a1a2e?style=flat-square)](https://github.com/mattiacalastri)
[![Dogfooding polpo-tui-toolkit](https://img.shields.io/badge/dogfooding-polpo--tui--toolkit-00C896?style=flat-square)](https://github.com/mattiacalastri/polpo-tui-toolkit)

**[Demo](#-the-cockpit-at-a-glance)** · **[Quick Start](#-quick-start)** · **[Why](#-why-this-exists-the-vendor-trap)** · **[Features](#-features)** · **[FAQ](#-faq)** · **[Tip Jar](#-tip-jar-mine-a-share-to-the-author)**

</div>

---

## 🆕 What's New in v0.3.0 — Arc Gauge braille + Story Mode

![Bitaxe Cockpit v0.3.0 hero — cyberpunk octopus tentacles holding ASCII braille dial gauges, dark teal NOC dashboard aesthetic with Bitcoin orange accents](assets/hero.jpg)

**Four Arc Gauge braille dials** inline 1×4 hero row + **Story Mode narrative panel** for non-crypto-savvy viewers. Made your Bitaxe finally readable by anyone who walks into your home.

![Bitaxe Cockpit v0.3.0 live screenshot — 4 ArcGauge braille semicircular dials HASHRATE/ASIC/VRM/POWER inline + Story Mode panel with probability earnings scale tier](assets/screenshot_v030.png)

### Arc Gauge braille primitive
4 semicircular 180° dials rendered via Unicode Braille (U+2800–28FF, 2×4 sub-pixel per cell). Color cascade green/amber/red. Bresenham needle line. Zero deps shipped (pure stdlib bit-packing).

### Translator inline (3-layer UX)
Under each dial, a human-language line:
- **HASHRATE** — *"Il chip prova 233.000.000.000 password al secondo · lavoro di ~233 MacBook Pro M3 in parallelo"*
- **ASIC** — *"Il silicio è acqua quasi bollente"* (cascade tisana/doccia/tè/acqua bollente/pasta scolata)
- **VRM** — *"Il VRM converte 5V→0.4V — fan al massimo, ventola urla"*
- **POWER** — *"Consuma come una lampadina LED · Costo €3.30/mese · €40/anno"*

### Story Mode panel narrative (Italian)
A full-width yellow panel that tells what your Bitaxe is doing in plain Italian:
- "Da 1.4 giorni cerca un blocco. Ha provato 123 quadrilioni di combinazioni."
- "🎰 Probabilità vittoria oggi: 1 su 35.000.000 · ETA 3.500 anni"
- "💰 Se vinci: €296.875 dritti nel wallet (3.125 BTC × €95.000)"
- "💸 Costo elettricità: €0.11/giorno · €40/anno"
- "🎯 Reality check: 78 Bitaxe singoli al mondo hanno trovato blocchi negli ultimi 2 anni"
- "🏆 Tier: 🥉 Hobby (€100-300) ← TU sei qui"

### Toggle key `d`
Press `d` to hide/show the drilldown text panels — leaves only Story Mode + dials for a clean "explain it to your mum" mode.

### Dogfooding [polpo-tui-toolkit](https://github.com/mattiacalastri/polpo-tui-toolkit)
ArcGauge primitive now extracted to a standalone library. `polpo_arc_gauge.py` in this repo is a backward-compat shim that imports from the sibling library. Pattern DRY ready for `m5-watcher` / `BTC-cockpit` / `MRR-cockpit` / `Health-Coach` cross-project reuse.

See [CHANGELOG.md](CHANGELOG.md#030--2026-05-28) for full sess.2622 release notes.

---

## 🎯 The Promise

Your Bitaxe is a single ESP32 sliver hashing solo against the entire Bitcoin network. AxeOS's web UI tells you **what** is happening. This cockpit tells you **why it matters**.

In one keystroke (`bitaxe-cockpit`) you get eight live panels — hashrate, thermal, share quality, block-find probability, energy cost, pool & wallet integrity, system health, and a context-aware legend — wrapped in an animated ASCII title, a refresh game with easter eggs, milestone badges every 1h/24h/7d/30d uptime, and the **only** Bitaxe-side tool that actively defends you against the vendor pre-config trap.

It runs in your terminal. It speaks Italian by default. It looks like a flight deck.

```
 ● LIVE  ·  ⚡ 1.15 TH/s ▂▃▄▅▆▇  ·  🌡 62 °C  ·  🔋 18 W  ·  ✓ 3610 share  ·  ⏱ 9h 37m  🥉 1h+
```

---

## ⚡ TL;DR

> **Bitaxe Cockpit** is an open-source terminal dashboard (TUI) for [Bitaxe](https://bitaxe.org) ESP32 solo Bitcoin miners (401, Gamma 601, Ultra 701, BM1370 ASIC). It polls `http://<bitaxe>/api/system/info` every 5 s and renders 8 live panels — hashrate, ASIC + VRM thermal, share quality, solo block-find probability, energy cost (€/day), pool & wallet integrity, system health, and educational tooltips — with mDNS auto-discovery, Telegram / Discord webhook alerts, and an **active wallet-drift check that defends you against the reseller "vendor trap"** where pre-configured Bitaxes mine to the seller's BTC address. One command: `pip install -e . && bitaxe-cockpit --discover`. MIT licensed, single-file Python 3.10+, Italian-first UI with English roadmap, zero telemetry, runs over SSH on a Raspberry Pi.

<!--
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Bitaxe Cockpit",
  "operatingSystem": "Linux, macOS, Windows (Python 3.10+)",
  "applicationCategory": "DeveloperApplication",
  "applicationSubCategory": "Bitcoin Mining Monitor",
  "description": "Open-source terminal dashboard (TUI) for Bitaxe ESP32 solo Bitcoin miners. Live hashrate, thermal, share quality, solo block-find probability, energy cost, and active wallet-drift detection against the reseller vendor trap.",
  "softwareVersion": "0.2.0",
  "license": "https://opensource.org/licenses/MIT",
  "url": "https://github.com/mattiacalastri/bitaxe-cockpit",
  "author": { "@type": "Organization", "name": "Polpo OS" },
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  "keywords": "bitaxe, solo bitcoin mining, axeos monitor, bm1370 dashboard, esp32 miner, textual tui, terminal dashboard, vendor wallet trap, mempool.space, homeminingitalia, italian bitcoin"
}
-->

---

## 📑 Table of Contents

- [The cockpit at a glance](#-the-cockpit-at-a-glance)
- [Why this exists — the vendor trap](#-why-this-exists-the-vendor-trap)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Keybindings](#%EF%B8%8F-keybindings)
- [Panels](#-panels)
- [Webhook alerts](#-webhook-alerts-v020)
- [mDNS auto-discovery](#-mdns-auto-discovery-v020)
- [Comparison](#-comparison-with-other-tools)
- [Architecture](#-architecture)
- [Tip jar — mine a share to the author](#-tip-jar-mine-a-share-to-the-author)
- [FAQ](#-faq)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Credits](#-credits)

---

## 🖼 The Cockpit at a Glance

![Bitaxe Cockpit live screenshot 2026-05-24 — Bitaxe Gamma 601 BM1370 ASIC at 1.13 TH/s mining solo on homeminingitalia.org, showing animated BITAXE header, LIVE status pill, 4855 accepted shares, 66°C ASIC temp, P(block) calculator and reward estimate](docs/screenshots/cockpit-live-2026-05-24-sess2231.png)

*Live capture 2026-05-24 12:34 CEST on a Gamma 601 BM1370 · **1.13 TH/s** · 66 °C ASIC · 75 °C VRM · **4 855 shares accepted, 4 rejected (0.08 % reject ratio)** · 12 h 38 m uptime 🥉 · solo pool `solo.homeminingitalia.org:3333` · Polpo dark theme · post-sess.2231 failure-classifier patch.*

What you're looking at, top to bottom:

- **Header strip** — animated **BITAXE** ASCII logo with traveling-wave gradient, COCKPIT badge, hostname, IP, clock, current block height, live status pill, and the inline summary line (`⚡ TH/s · 🌡 °C · 🔋 W · ✓ share · ⏱ uptime · 🥉 milestone`).
- **⚡ HASHRATE** (orange) — live GH/s + expected vs measured + perf% + J/TH efficiency + 60 s sparkline + min/avg/max + educational tooltip.
- **🌡 TEMPERATURE** (red) — ASIC + VRM gauges side by side, dual sparklines, fan RPM + auto/manual, target temp, thermal margins both rails.
- **⛏ MINING** (gold) — Share OK / KO with reject-reason cluster, share/min cadence, best diff (lifetime + session), pool difficulty, stratum response time.
- **🎯 BLOCK HUNT** (magenta) — your share of total network hashrate, P(block)/day, expected ETA, block-find chances/day equivalent, reward in BTC + EUR conversion.

Below this fold (scroll the terminal): **🔋 Alimentazione · 🏊 Pool & Wallet · 📡 Sistema · 📘 Legenda**. All eight panels live update on the same 5 s poll cycle (configurable). No redraws, no flicker, no jitter — Textual reactive watchers only repaint deltas.

More captures (other themes, alert states, vendor-trap warning) coming as the cockpit gets battle-tested by the community — PRs welcome under [`docs/screenshots/`](docs/screenshots/).

---

## 🛡 Why Bitaxe Cockpit Exists — *The Vendor Wallet Trap*

A brand-new Bitaxe often arrives **pre-configured with the seller's Bitcoin address** as the active `stratumUser`. Every share you mine. Every block you hit. Goes to **them**.

It's legal. It's documented in tiny print. It's also a quiet way for resellers to subsidize themselves at your expense.

```mermaid
flowchart TD
    A([📦 You unbox a new Bitaxe]) --> B[Plug it in · OLED says 'mining']
    B --> C{Did you check<br/><code>/api/system/info</code><br/>stratumUser?}
    C -->|"❌ No"| D[("💸 Your sats → reseller<br/>forever<br/>(silent failure)")]
    C -->|"✅ Yes"| E[See <code>bc1pl5j...BitaxeHMI</code><br/>= vendor wallet]
    E --> F[PATCH stratumUser<br/>with YOUR address]
    F --> G{API confirms<br/>new wallet?}
    G -->|"✅ Yes"| H{WebSocket <code>/api/ws</code><br/>shows YOUR shares?}
    G -->|"❌ No"| F
    H -->|"❌ Still vendor"| I[("🚨 AxeOS cache:<br/>API lies, runtime stale")]
    I --> J[POST <code>/api/system/restart</code>]
    J --> H
    H -->|"✅ Yes"| K([🎯 First share to YOUR wallet<br/>verified live])

    classDef trap fill:#3a0000,stroke:#FF4444,color:#FF8888,stroke-width:2px;
    classDef safe fill:#003300,stroke:#00C896,color:#88FFAA,stroke-width:2px;
    classDef check fill:#1a1a2e,stroke:#FFD700,color:#FFD700;
    class D,I trap;
    class A,K safe;
    class C,G,H check;
```

> **This actually happened to the machine that runs this cockpit.**
> Sess.2210 (2026-05-23, Bitcare Forum, Brescia): first Bitaxe acquired. Pre-flight `/api/system/info` revealed `stratumUser: bc1pl5j75axs...BitaxeHMI`. PATCH applied with the rightful owner's wallet. API confirmed new wallet. WebSocket stream `/api/ws` revealed: **14 of 14 subsequent shares still flowing to the vendor**.
>
> AxeOS caches the stratumUser in runtime memory until you POST `/api/system/restart`. The HTTP API lies politely. The WebSocket tells the truth.

This cockpit ships with that scar built in:

- ✅ **`BITAXE_WALLET_PREFIX` env var** — set it to the first ~8 chars of your address. The Pool & Wallet panel screams `Wallet VENDOR ❌` in red the moment a drift is detected.
- ✅ **Reference WebSocket check** documented (`scripts/ws_check.py`) — catches the "API shows the new config, runtime is still using the old one" failure mode.
- ✅ **Telegram / Discord / generic webhook alert** (opt-in) — drift fires `wallet_mismatch` and reaches your phone in seconds.
- ✅ **Post-restart verification** — once you POST `/api/system/restart`, the next 5 consecutive shares are tagged and confirmed in the share log.

If you bought your Bitaxe from anyone other than the official store: **run this cockpit at least once before you go to bed tonight.**

---

## ✨ Features

### Live telemetry
- **Animated BITAXE ASCII title** with traveling-wave gradient (4 Hz refresh, GPU-free)
- **Live hashrate sparkline** + 60s rolling history + J/TH efficiency rating
- **Dual-channel thermal monitor** — ASIC junction + VRM regulator, side-by-side sparklines, configurable guard rails
- **Mining quality panel** — accepted / rejected shares, reject-reason clustering, share/min, lifetime best difficulty
- **Power & energy** — Watt gauge, voltage, current, frequency, ASIC core voltage, headroom percentage, and €/day · €/month · €/year at your configurable kWh rate
- **Bitcoin network awareness** — live block height from `mempool.space` polled every 60 s

### Solo-mining intelligence
- **Block probability calculator** — your share of total network hashrate, P(block) per day, ETA in human-readable form, expected reward in BTC and EUR
- **Pool & wallet integrity panel** — primary + fallback pool status, latency sparkline, stratumUser wallet check (anti vendor trap)
- **Uptime milestone badges** 🥉 1h+ · 🥈 24h+ · 🥇 7d+ · 🏆 30d+ — because solo mining is a long game and small wins matter

### Operator UX
- **Gamified manual refresh** — press `r`, see counter / streak (sub-60 ms = combo) / personal best response time. Easter eggs at 21, 100, and 333 refreshes.
- **4 selectable themes** — Polpo (default) · Bitcoin · Mono · Hacker. Cycle with `t`.
- **Rotating educational tooltips** — every 30 s a contextual tip explains J/TH, solo mining math, VRM bottlenecks, RSSI signal floors, etc.
- **CSV history export** — every poll appended to `~/.local/share/bitaxe_cockpit/history.csv` for post-hoc analysis in Pandas / DuckDB / Excel
- **SVG snapshot** with `s` — instant, vector-quality terminal capture
- **Italian-first UI** — labels, tooltips, alerts in Italian; English contributions warmly welcomed (see [Roadmap](#-roadmap))

### Network & alerts (v0.2.0+)
- **mDNS auto-discovery** — `bitaxe-cockpit --discover` scans your LAN and finds the device, no IP guessing
- **Telegram / Discord / generic JSON webhook alerts** — opt-in, async, with per-event cooldowns so it never spams

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10+**
- A Bitaxe miner on your LAN (401 · Gamma 601 · Ultra 701 · all compatible)
- Any modern terminal with Unicode + truecolor (Ghostty, iTerm2, WezTerm, Alacritty, Kitty, Windows Terminal — all tested)

### One-liner install + auto-discovery
```bash
git clone https://github.com/mattiacalastri/bitaxe-cockpit.git
cd bitaxe-cockpit
pip install -e ".[discovery]"
bitaxe-cockpit --discover
```

That's it. If exactly one Bitaxe is on your LAN it auto-selects. If more than one, you get an interactive picker.

### Other launch modes
```bash
# Explicit host
bitaxe-cockpit --host 192.168.1.X

# Custom poll interval
bitaxe-cockpit --host 192.168.1.X --interval 2.0

# Print discovered devices and exit (no TUI)
bitaxe-cockpit --list

# Via uvx (no install)
uvx --from . bitaxe-cockpit
```

### Wallet-safe launch (recommended)
```bash
export BITAXE_HOST=192.168.1.X
export BITAXE_WALLET_PREFIX=bc1qxxxxxxx   # first ~8 chars of YOUR BTC address
bitaxe-cockpit
```

The cockpit will now actively scream if the device's `stratumUser` ever drifts away from your prefix. See [§ Vendor Trap](#-why-this-exists-the-vendor-trap).

---

## 🔧 Configuration

### Environment variables

| Variable               | Default          | Purpose                                       |
| ---------------------- | ---------------- | --------------------------------------------- |
| `BITAXE_HOST`          | `bitaxe.local`   | Bitaxe IP or mDNS hostname                    |
| `BITAXE_REFRESH_SEC`   | `5.0`            | Poll interval in seconds                      |
| `BITAXE_WALLET_PREFIX` | (empty)          | First ~8 chars of your BTC address — **set this** |
| `BITAXE_KWH_RATE`      | `0.25`           | Electricity cost €/kWh for energy panel       |
| `BITAXE_TG_TOKEN`      | (empty)          | Telegram bot token for alerts (opt-in)        |
| `BITAXE_TG_CHAT_ID`    | (empty)          | Telegram chat/channel ID                      |
| `BITAXE_DISCORD_URL`   | (empty)          | Discord webhook URL                           |
| `BITAXE_WEBHOOK_URL`   | (empty)          | Generic POST endpoint for JSON alerts         |

### Data storage
- **CSV history** — `~/.local/share/bitaxe_cockpit/history.csv` (append-only, one row per poll)
- **SVG snapshots** — `~/.local/share/bitaxe_cockpit/snapshots/snapshot-YYYYMMDD-HHMMSS.svg`

---

## ⌨️ Keybindings

| Key       | Action                                     |
| --------- | ------------------------------------------ |
| `r`       | Refresh now (manual, gamified — try it)    |
| `p`       | Pause / resume auto-refresh                |
| `space`   | Single-step refresh (while paused)         |
| `t`       | Cycle theme (Polpo → Bitcoin → Mono → Hacker) |
| `s`       | Save SVG snapshot                          |
| `e`       | Echo CSV history file path                 |
| `+` / `-` | Faster / slower poll interval              |
| `o`       | Open AxeOS web UI in browser               |
| `?` / `h` | Open / close help overlay                  |
| `q`       | Quit                                       |

---

## 📊 Panels

| #   | Panel              | Color    | Content                                                        |
| --- | ------------------ | -------- | -------------------------------------------------------------- |
| 1   | ⚡ Hashrate        | Orange   | Live TH/s, expected, perf %, J/TH efficiency, 60 s sparkline   |
| 2   | 🌡 Temperatura     | Red      | ASIC + VRM gauges, dual sparkline, fan %, thermal margin       |
| 3   | ⛏ Mining           | Gold     | Share OK / KO, reject-reason cluster, share/min, best diff     |
| 4   | 🎯 Block Hunt        | Magenta  | Network share, P(block)/day, ETA, expected reward (BTC + EUR)  |
| 5   | 🔋 Alimentazione   | Cyan     | W gauge, V, A, freq, core V, headroom, €/day · €/month · €/year |
| 6   | 🏊 Pool & Wallet   | Green    | Primary/fallback status, latency sparkline, **wallet integrity check** |
| 7   | 📡 Sistema         | Blue     | Hostname, MAC, RSSI sparkline, firmware, free heap, uptime     |
| 8   | 📘 Legenda         | White    | Keybindings, thresholds, rotating educational tooltips         |

---

## 🔔 Webhook Alerts (v0.2.0+)

Push notifications when thresholds are crossed. Opt-in. Per-event 5–15 min cooldown — no spam, ever.

```bash
# Telegram (create the bot via @BotFather)
export BITAXE_TG_TOKEN="123456:ABC..."
export BITAXE_TG_CHAT_ID="987654"

# Discord (channel → Edit Channel → Integrations → Webhooks → New)
export BITAXE_DISCORD_URL="https://discord.com/api/webhooks/..."

# Generic JSON POST to your own server
export BITAXE_WEBHOOK_URL="https://your-server.example.com/bitaxe-alerts"
```

### Event catalog

| Event                         | Severity | Trigger                                       |
| ----------------------------- | -------- | --------------------------------------------- |
| `asic_temp_crit`              | **crit** | ASIC > 70 °C (throttle imminent)              |
| `vrm_temp_crit`               | **crit** | VRM > 80 °C                                   |
| `overheat_mode`               | **crit** | Firmware overheat throttle engaged            |
| `unreachable`                 | **crit** | API silent 3 consecutive polls                |
| `wallet_mismatch`             | **crit** | `stratumUser` drifted away from your prefix   |
| `best_diff_break`             | info     | New lifetime best share difficulty            |
| `uptime_milestone_{3600,...}` | info     | Crossed 1 h / 24 h / 7 d / 30 d uptime        |

Generic webhook receives:
```json
{ "event": "asic_temp_crit", "severity": "crit", "title": "🔥 ASIC overheat", "message": "...", "ts": 1716552934 }
```

---

## 🔍 mDNS Auto-Discovery (v0.2.0+)

Don't know your Bitaxe IP? Don't care.

```bash
pip install "bitaxe-cockpit[discovery]"   # adds zeroconf
bitaxe-cockpit --discover                  # interactive picker
bitaxe-cockpit --list                      # print + exit, no TUI
```

The discovery layer scans `_http._tcp.local.` for 3 seconds and matches services with `bitaxe`, `axe`, or `esp32` in the name. One match → auto-select. Multiple → interactive prompt. Zero matches → friendly error with troubleshooting hints (firewall, mDNS reflector, VLAN segmentation).

---

## ⚖️ Comparison with Other Tools

|                                 | **Bitaxe Cockpit**     | AxeOS Web UI         | Prometheus/Grafana stack | Custom JSON polling |
| ------------------------------- | ---------------------- | -------------------- | ------------------------ | ------------------- |
| Runtime                         | Terminal (Textual)     | Browser              | Browser (Grafana)        | Whatever you write  |
| Install effort                  | `pip install -e .`     | Built-in             | Docker + 2 configs       | Bring your own      |
| Resource footprint              | ~25 MB RAM, <1% CPU    | Negligible (device)  | 200+ MB RAM              | Varies              |
| Live sparklines                 | ✅ all panels          | ❌                   | ✅ (configurable)         | If you build them   |
| Solo block-find probability               | ✅                     | ❌                   | ❌ (calculator missing)   | Possible            |
| **Wallet integrity check**      | ✅ **active alerts**   | ❌ display only      | Possible w/ alertmanager | Possible            |
| Energy cost in €/month·year     | ✅                     | ❌                   | Possible                 | Possible            |
| Uptime gamification             | ✅ milestone badges    | ❌                   | ❌                       | ❌                  |
| CSV historical export           | ✅ auto                | ❌                   | ✅ via Prometheus TSDB    | Manual              |
| Works offline / no cloud        | ✅                     | ✅                   | ✅                       | ✅                  |
| Italian-first UI                | ✅                     | ❌ (EN only)         | ❌                       | ❌                  |

Use the cockpit when you want **immediate operator awareness** at the terminal. Use Prometheus/Grafana when you have **N>3 miners and historical alerting needs**. They're complementary — the cockpit happily exports CSV that Grafana can ingest.

---

## 🏗 Architecture — Data Flow and Failure Modes

```mermaid
flowchart LR
    subgraph LAN[" Your LAN "]
        BTX[("🔌 Bitaxe<br/>ESP32 + ASIC<br/>AxeOS firmware")]
    end
    subgraph Cockpit[" bitaxe-cockpit (your terminal) "]
        POLL["⚙️ httpx async poll<br/>every 5 s"]
        STATE["📦 BitaxeState<br/>dataclass<br/>(60-sample history)"]
        TUI["🖥 Textual App<br/>8 reactive panels<br/>+ animated header"]
        CSV["💾 history.csv<br/>append-only"]
        WS["🛡 ws_check.py<br/>vendor-trap defender"]
        ALERT["📡 Webhook fanout<br/>Telegram · Discord · JSON"]
    end
    subgraph Cloud[" Internet (optional, opt-in) "]
        MP[("⛓ mempool.space<br/>block height")]
        TG[/"📱 Telegram bot"/]
        DC[/"🎮 Discord webhook"/]
        WH[/"🌐 Your endpoint"/]
    end

    BTX -- "GET /api/system/info<br/>(JSON, ~1.7 KB)" --> POLL
    POLL --> STATE
    STATE --> TUI
    STATE --> CSV
    BTX -. "WebSocket /api/ws<br/>(ground-truth share stream)" .-> WS
    WS -. "drift detected" .-> ALERT
    STATE -. "threshold crossed" .-> ALERT
    MP -. "block height (60 s)" -.-> TUI
    ALERT --> TG
    ALERT --> DC
    ALERT --> WH

    classDef bitaxe fill:#F7931A,stroke:#000,color:#000,stroke-width:2px;
    classDef cockpit fill:#1a1a2e,stroke:#FFD700,color:#FFD700;
    classDef cloud fill:#0f0f1a,stroke:#888,color:#aaa;
    class BTX bitaxe;
    class POLL,STATE,TUI,CSV,WS,ALERT cockpit;
    class MP,TG,DC,WH cloud;
```

```
bitaxe-cockpit/
├── bitaxe_cockpit.py        ← Textual App + 11 widgets (~1900 lines, single file by design)
├── bitaxe_cockpit.tcss      ← Textual CSS (4 themes, 8 panel layouts, gauge styling)
├── bitaxe_ghostty_wrapper.c ← Optional macOS .app launcher (Ghostty fullscreen)
├── pyproject.toml           ← Standard PEP-621 project file
├── docs/
│   └── screenshots/         ← PNG + SVG renderings
├── tests/                   ← Smoke tests + thermal threshold tests
└── .github/workflows/ci.yml ← Matrix Python 3.10 / 3.11 / 3.12
```

### Failure classification (v0.2.1 — sess.2231)

The cockpit distinguishes **five** failure modes instead of a single OFFLINE — because "Bitaxe down" and "you're on the wrong WiFi" are not the same problem:

| Label (header pill) | Color | Trigger | What you should do |
| ------------------- | ----- | ------- | ------------------ |
| `LIVE` | 🟢 green | API responded, JSON valid | Watch sats accumulate |
| `UNREACHABLE` | 🟡 yellow | Host on different /24 subnet | Reconnect to your home WiFi (hotspot?) |
| `OFFLINE` | 🔴 red | Connect timeout on same subnet | Check cable, PSU, Bitaxe WiFi config |
| `DEVICE DOWN` | 🔴 red | TCP RST (ECONNREFUSED) | Bitaxe powered but AxeOS unresponsive — restart |
| `HTTP ERR` | 🔴 red | 4xx / 5xx from AxeOS | Firmware glitch — reflash or restart |
| `BAD DATA` | 🔴 red | Non-JSON response | Possible corrupted firmware |

This matters because the **same screen of zeros** can mean five completely different real-world problems. The classifier is the operator's first sanity layer.

### Polling internals

The core polls `GET http://<host>/api/system/info` every N seconds, decodes into a `BitaxeState` dataclass, and Textual's reactive watchers update each panel only when a delta is detected. Manual `r` triggers an out-of-band poll plus gamification tracking (streak, NEW BEST, easter eggs at 21/100/333). The streak counter only increments when the device is **reachable** *and* response time < 60 ms — fail-fast errors no longer falsely "win" a streak (sess.2231 patch).

No threads, no asyncio shenanigans beyond Textual's own loop — boring and stable.

Why a single file? Because you should be able to `wget` it onto a Pi and run it. Modularization only happens when an external contributor asks (it hasn't, yet).

---

## 💸 Tip Jar — Mine a Share to the Author

> **No PayPal. No GitHub Sponsors button. We're on Bitcoin — let's act like it.**

If this tool saved your block (or your wallet from a vendor trap), point your Bitaxe's `stratumUser` at the author's address for an afternoon. Use the `.tip` worker tag so it stays separate from your main hashing:

```
stratumUser:  bc1q905k0qzhtckpss2xucpuayy8sgwpncjquj4vfg.tip
stratumPass:  x
pool:         solo.homeminingitalia.org:3333
```

A few hours of TH/s costs you nothing and tells the author *"this thing matters."* If your Bitaxe hits a block while tagged `.tip`, well — you've made friends for life. Lightning support coming soon.

Prefer fiat? ⭐ a star at the top of this page. Discoverability is worth more than coffee.

---

## ❓ FAQ

<!--
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type":"Question","name":"What is Bitaxe?","acceptedAnswer":{"@type":"Answer","text":"Bitaxe is an open-source single-ASIC solo Bitcoin miner built around an ESP32 controller and a Bitmain BM1370 (Gamma 601) / BM1366 (Ultra 701) ASIC. It runs the AxeOS firmware and exposes a JSON API at /api/system/info on port 80. It hashes solo against the entire Bitcoin network — the upside is a full block reward (~3.125 BTC + fees) if you win, the downside is statistical insignificance unless thousands of operators run them collectively."}},
    {"@type":"Question","name":"What does Bitaxe Cockpit do?","acceptedAnswer":{"@type":"Answer","text":"Bitaxe Cockpit is a terminal-native dashboard (TUI) written in Python and Textual that polls a Bitaxe's HTTP API every 5 seconds and renders 8 live panels: hashrate, ASIC + VRM temperature, share quality, solo block-find probability, energy cost, pool & wallet integrity, system health, and a context-aware legend. Its distinctive feature is an active wallet-drift check that detects the 'vendor wallet trap' where resellers ship Bitaxes pre-configured with their own BTC address."}},
    {"@type":"Question","name":"What is the Bitaxe vendor wallet trap?","acceptedAnswer":{"@type":"Answer","text":"The vendor wallet trap is a practice where Bitaxe resellers ship the device with their own Bitcoin address pre-configured as the stratumUser. Without explicit verification via /api/system/info, the new owner unknowingly mines Bitcoin to the reseller. Even after patching the config via the web UI, AxeOS caches the old stratumUser in runtime memory until a full /api/system/restart — so the HTTP API can show the new wallet while the WebSocket stream still emits shares to the old one. Bitaxe Cockpit defends against this with the BITAXE_WALLET_PREFIX env var and a post-restart verification routine."}},
    {"@type":"Question","name":"Will Bitaxe Cockpit work with my Bitaxe 401?","acceptedAnswer":{"@type":"Answer","text":"Yes. Any Bitaxe with AxeOS firmware 2.0 or newer that exposes the standard /api/system/info JSON endpoint is supported. Tested live on Bitaxe 401, Gamma 601 (BM1370), and Ultra 701 (BM1366)."}},
    {"@type":"Question","name":"Does Bitaxe Cockpit collect telemetry?","acceptedAnswer":{"@type":"Answer","text":"No. Zero telemetry. The only outbound HTTP calls are: (1) your Bitaxe on the LAN, (2) mempool.space for Bitcoin block height, (3) the webhook endpoints you explicitly configure. Source code is a single Python file — auditable in one read."}}
  ]
}
-->

**Q: What is Bitaxe?**
Bitaxe is an open-source single-ASIC solo Bitcoin miner built around an **ESP32** controller and a **Bitmain BM1370** (Gamma 601) or **BM1366** (Ultra 701) ASIC. It runs the [AxeOS firmware](https://github.com/skot/ESP-Miner) and exposes a JSON API at `/api/system/info` on port 80. Each unit hashes **~1 TH/s solo** against the entire Bitcoin network — the upside is a full block reward (~3.125 BTC + fees) if you find one, the downside is statistical insignificance unless thousands of operators run them collectively. Roughly the per-day odds of a single 1 TH/s device hitting a block are `1 / (3.0 × 10⁸)` at current difficulty.

**Q: What does Bitaxe Cockpit actually do?**
It's a terminal-native dashboard that polls your Bitaxe's HTTP API every 5 s and renders 8 live panels: hashrate, ASIC + VRM thermal, share quality, **solo block-find probability**, energy cost in €, pool & wallet integrity, system health, and an educational legend. Distinctive features: animated wave header, gamified manual refresh, uptime milestone badges, **active wallet-drift defense against the vendor trap**, mDNS auto-discovery, opt-in Telegram/Discord/JSON webhook alerts.

**Q: Will this work with my Bitaxe 401 from 2024?**
Yes. Any Bitaxe with AxeOS ≥ 2.0 exposing the standard `/api/system/info` endpoint. Tested on 401, Gamma 601, Ultra 701.

**Q: Does it work outside Italy?**
Yes — the UI is Italian-first but every label is short and self-explanatory. English localization is the #1 roadmap item and PRs are welcome. EUR symbol assumes EU electricity rate; override via `BITAXE_KWH_RATE` and your currency is set by your locale.

**Q: Can I run this on a Raspberry Pi headless and view it over SSH?**
Yes. Textual renders perfectly over SSH. Recommended: `tmux` + `mosh` for survivable sessions.

**Q: How accurate is the block-find probability calculation?**
It uses the standard solo-mining formula `P(block/day) = hashrate / network_hashrate × 144`, with network hashrate refreshed every 60 s from `mempool.space`. Accurate to within ~3% — the inherent variance of difficulty re-targeting dominates any model error.

**Q: Why a TUI and not a web dashboard?**
Because solo mining is a long-running ambient process and a terminal panel that lives in a corner of your screen is the right surface for it. Also: terminals are tactile, fast, scriptable, and survive `tmux` reboots gracefully. Web UIs forget you exist.

**Q: Does it phone home / collect analytics?**
**No.** Zero telemetry. The only outbound HTTP calls are: (1) your Bitaxe on the LAN, (2) `mempool.space` for block height, (3) the webhook endpoints **you** explicitly configure. Source code is one file — read it.

**Q: Is the gamification just gimmick?**
It started as one. Then I noticed I was checking the cockpit more often, catching issues earlier, and feeling actively present with my miner. The dopamine of a sub-60 ms refresh streak is a low cost / high engagement loop. Keep it.

**Q: What's "Polpo OS"?**
A long story. Short version: this cockpit is one tentacle of a larger personal operating system. See [Credits](#-credits).

---

## 🗺 Roadmap

- [x] **v0.1.0** — Initial release, 8 panels, animated title, gamified refresh, wallet check
- [x] **v0.2.0** — mDNS auto-discovery, webhook alerts (Telegram / Discord / generic)
- [ ] **v0.3.0** — Multi-device dashboard (`--hosts ip1,ip2,ip3` with per-device sub-cockpits)
- [ ] **v0.3.0** — English localization toggle (`LANG=en` switches all strings)
- [ ] **v0.4.0** — Prometheus `/metrics` exporter (drop-in for Grafana stacks)
- [ ] **v0.4.0** — Block-hit celebration mode (full-screen takeover + Lightning tip-out)
- [ ] **v0.5.0** — Mining diary / logbook view (annotate why hashrate dipped, why you re-flashed firmware, etc.)
- [ ] **v0.5.0** — Localization to Spanish, German, Portuguese (community-driven)
- [ ] **future** — WebSocket-native poll mode (lower latency than REST, catches the AxeOS runtime-vs-API drift live)

Have an idea? Open an issue with the label `enhancement`.

---

## 🤝 Contributing

PRs welcome and read carefully. See [CONTRIBUTING.md](CONTRIBUTING.md) for the short version (be kind, run `ruff format`, add a test if you touch math, update CHANGELOG.md).

This project follows the [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). For security vulnerabilities, please use the private channel described in [SECURITY.md](SECURITY.md) — **do not open public issues for security bugs**.

**Specifically wanted:**
- 🌐 English / Spanish / German / Portuguese localization
- 📊 Prometheus metrics exporter
- 🖥 Multi-device mode
- 🧪 Tests for thermal / block-find math edge cases
- 📚 Screenshots from your own Bitaxe (any model, any theme)

Brand new to open source? Open an issue tagged `good-first-issue` and I'll walk you through it.

---

## 📜 License

MIT — see [LICENSE](LICENSE).

Use it, fork it, sell it, embed it in your commercial mining-monitoring SaaS. Just don't strip the credits header from `bitaxe_cockpit.py` — the easter eggs reference it.

---

## 🐙 Credits

Forged in the wild by **[Polpo OS](https://github.com/mattiacalastri)** — a personal operating system woven from skills, agents, hooks, and a vault of ~5,600 connected notes. The cockpit is *tentacolo #25*: the first **physical** neuron of the system, born when a Bitaxe Gamma 601 walked into the home at Bitcare Forum Brescia on **2026-05-23** (sess.2210) and immediately tried to mine to someone else's wallet. The Polpo took offense.

Polished sess.2214 (gamification + animated wave + Italian-first + OSS hardening) and weaponized sess.2218 (this README).

**Standing on the shoulders of:**
- **[@skot](https://github.com/skot/ESP-Miner)** — the legend who started ESP-Miner / AxeOS firmware
- **[bitaxeorg](https://github.com/bitaxeorg)** — open hardware steward, Gamma 601 boards
- **[Home Mining Italia](https://homeminingitalia.org)** — the solo pool that catches the block-find wins
- **[Textual](https://textual.textualize.io)** by Textualize — the framework that makes terminals feel like apps
- **[mempool.space](https://mempool.space)** — open, free, no-key block height API

If solo mining is a probabilistic hunt, this cockpit is the room where you sit and watch the entropy.
Good luck out there.

```
🐙⚔️🎩
```

</div>
