#!/usr/bin/env python3
"""
Bitaxe Cockpit — Polpo OS sess.2210
Live TUI monitor for Bitaxe Gamma 601 via AxeOS REST API
Stack: Textual + httpx
Path canonical: ~/scripts/bitaxe_cockpit.py
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import time
import webbrowser
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Static


# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_HOST = os.environ.get("BITAXE_HOST", "bitaxe.local")
DEFAULT_REFRESH_SEC = float(os.environ.get("BITAXE_REFRESH_SEC", "5.0"))
HISTORY_SIZE = 60
# Set BITAXE_WALLET_PREFIX env var to enable wallet-integrity tamper check.
# Example: export BITAXE_WALLET_PREFIX="bc1qxxx" (first ~8 chars of your address).
# If empty, wallet check is skipped (vendor pre-config trap NOT detected).
WALLET_PREFIX = os.environ.get("BITAXE_WALLET_PREFIX", "")

DATA_DIR = Path.home() / ".local" / "share" / "bitaxe_cockpit"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CSV_LOG_PATH = DATA_DIR / "history.csv"

THEMES = ["polpo", "bitcoin", "mono", "hacker"]


# ──────────────────────────────────────────────────────────────────────────────
# Data model
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class BitaxeState:
    """Snapshot Bitaxe state from /api/system/info"""
    hashrate_ghs: float = 0.0
    expected_ghs: float = 0.0
    temp_asic: float = 0.0
    temp_vrm: float = 0.0
    fan_perc: int = 0
    fan_rpm: int = 0
    autofanspeed: int = 1
    temp_target: int = 60
    power_w: float = 0.0
    max_power_w: float = 40.0
    voltage_v: float = 0.0
    current_a: float = 0.0
    frequency_mhz: int = 0
    core_voltage_mv: int = 0
    core_voltage_actual_mv: int = 0
    shares_accepted: int = 0
    shares_rejected: int = 0
    shares_rejected_reasons: list = field(default_factory=list)
    best_diff: str = ""
    best_session_diff: str = ""
    pool_diff: int = 0
    stratum_url: str = ""
    stratum_port: int = 0
    stratum_user: str = ""
    fallback_url: str = ""
    fallback_port: int = 0
    fallback_user: str = ""
    using_fallback: bool = False
    hostname: str = ""
    mac_addr: str = ""
    ssid: str = ""
    wifi_rssi: int = 0
    wifi_status: str = ""
    uptime_sec: int = 0
    free_heap: int = 0
    axeos_version: str = ""
    idf_version: str = ""
    asic_model: str = ""
    board_version: str = ""
    small_core_count: int = 0
    overheat_mode: int = 0
    overclock_enabled: int = 0
    response_time_ms: float = 0.0
    last_update: Optional[datetime] = None
    reachable: bool = True

    @classmethod
    def from_api(cls, d: dict, response_ms: float) -> "BitaxeState":
        return cls(
            hashrate_ghs=float(d.get("hashRate", 0)),
            expected_ghs=float(d.get("expectedHashrate", 0)),
            temp_asic=float(d.get("temp", 0)),
            temp_vrm=float(d.get("vrTemp", 0)),
            fan_perc=int(d.get("fanspeed", 0)),
            fan_rpm=int(d.get("fanrpm", 0)),
            autofanspeed=int(d.get("autofanspeed", 1)),
            temp_target=int(d.get("temptarget", 60)),
            power_w=float(d.get("power", 0)),
            max_power_w=float(d.get("maxPower", 40)),
            voltage_v=float(d.get("voltage", 0)) / 1000,
            current_a=float(d.get("current", 0)) / 1000,
            frequency_mhz=int(d.get("frequency", 0)),
            core_voltage_mv=int(d.get("coreVoltage", 0)),
            core_voltage_actual_mv=int(d.get("coreVoltageActual", 0)),
            shares_accepted=int(d.get("sharesAccepted", 0)),
            shares_rejected=int(d.get("sharesRejected", 0)),
            shares_rejected_reasons=list(d.get("sharesRejectedReasons", []) or []),
            best_diff=str(d.get("bestDiff", "")),
            best_session_diff=str(d.get("bestSessionDiff", "")),
            pool_diff=int(d.get("poolDifficulty", 0)),
            stratum_url=str(d.get("stratumURL", "")),
            stratum_port=int(d.get("stratumPort", 0)),
            stratum_user=str(d.get("stratumUser", "")),
            fallback_url=str(d.get("fallbackStratumURL", "")),
            fallback_port=int(d.get("fallbackStratumPort", 0)),
            fallback_user=str(d.get("fallbackStratumUser", "")),
            using_fallback=bool(d.get("isUsingFallbackStratum", 0)),
            hostname=str(d.get("hostname", "")),
            mac_addr=str(d.get("macAddr", "")),
            ssid=str(d.get("ssid", "")),
            wifi_rssi=int(d.get("wifiRSSI", 0)),
            wifi_status=str(d.get("wifiStatus", "")),
            uptime_sec=int(d.get("uptimeSeconds", 0)),
            free_heap=int(d.get("freeHeap", 0)),
            axeos_version=str(d.get("axeOSVersion", "")),
            idf_version=str(d.get("idfVersion", "")),
            asic_model=str(d.get("ASICModel", "")),
            board_version=str(d.get("boardVersion", "")),
            small_core_count=int(d.get("smallCoreCount", 0)),
            overheat_mode=int(d.get("overheat_mode", 0)),
            overclock_enabled=int(d.get("overclockEnabled", 0)),
            response_time_ms=response_ms,
            last_update=datetime.now(),
            reachable=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Webhook Notifier (sess.2214 — alert push)
# ──────────────────────────────────────────────────────────────────────────────

class WebhookNotifier:
    """Async fire-and-forget alert push to Telegram, Discord, generic POST.

    Configured via environment variables (opt-in, all unset = no-op):
      BITAXE_TG_TOKEN + BITAXE_TG_CHAT_ID  → Telegram bot
      BITAXE_DISCORD_URL                   → Discord webhook URL
      BITAXE_WEBHOOK_URL                   → Generic POST JSON

    Anti-spam: per-event cooldown (default 5min).
    """

    DEFAULT_COOLDOWN_SEC = 300

    def __init__(self):
        self.tg_token = os.environ.get("BITAXE_TG_TOKEN", "")
        self.tg_chat_id = os.environ.get("BITAXE_TG_CHAT_ID", "")
        self.discord_url = os.environ.get("BITAXE_DISCORD_URL", "")
        self.webhook_url = os.environ.get("BITAXE_WEBHOOK_URL", "")
        self._last_fired: dict[str, float] = {}
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.tg_token and self.tg_chat_id) or bool(self.discord_url) or bool(self.webhook_url)

    def _can_fire(self, event_key: str, cooldown: float = DEFAULT_COOLDOWN_SEC) -> bool:
        now = time.time()
        last = self._last_fired.get(event_key, 0)
        if now - last < cooldown:
            return False
        self._last_fired[event_key] = now
        return True

    async def _client_get(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    async def fire(self, event_key: str, title: str, message: str, severity: str = "info", cooldown: float = DEFAULT_COOLDOWN_SEC):
        """Send alert to all configured channels. Silent on per-channel failure."""
        if not self.is_configured():
            return
        if not self._can_fire(event_key, cooldown):
            return
        client = await self._client_get()
        emoji = {"info": "🐙", "warn": "⚠️", "crit": "🚨"}.get(severity, "🔔")
        full_msg = f"{emoji} *{title}*\n{message}"

        # Telegram
        if self.tg_token and self.tg_chat_id:
            try:
                await client.post(
                    f"https://api.telegram.org/bot{self.tg_token}/sendMessage",
                    json={"chat_id": self.tg_chat_id, "text": full_msg, "parse_mode": "Markdown"},
                )
            except Exception:
                pass

        # Discord
        if self.discord_url:
            try:
                color = {"info": 0xF7931A, "warn": 0xFFB000, "crit": 0xFF4444}.get(severity, 0x888888)
                await client.post(self.discord_url, json={
                    "embeds": [{"title": f"{emoji} {title}", "description": message, "color": color}]
                })
            except Exception:
                pass

        # Generic JSON POST
        if self.webhook_url:
            try:
                await client.post(self.webhook_url, json={
                    "event": event_key,
                    "severity": severity,
                    "title": title,
                    "message": message,
                    "ts": time.time(),
                })
            except Exception:
                pass

    async def close(self):
        if self._client is not None:
            await self._client.aclose()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

SPARK_CHARS = " ▁▂▃▄▅▆▇█"

def sparkline(values: list[float], width: int = 30) -> str:
    """Generate unicode sparkline from values."""
    if not values:
        return "[dim]· collecting data...[/]".ljust(width + 25)
    vals = list(values)[-width:]
    lo = min(vals)
    hi = max(vals)
    rng = hi - lo if hi > lo else max(abs(hi), 1)
    chars = []
    for v in vals:
        if rng == 0:
            idx = len(SPARK_CHARS) // 2  # middle char if all same
        else:
            idx = int(((v - lo) / rng) * (len(SPARK_CHARS) - 1))
        chars.append(SPARK_CHARS[max(1, min(idx, len(SPARK_CHARS) - 1))])
    return "".join(chars).rjust(width)


def bar(value: float, max_val: float, width: int = 20) -> str:
    """Solid bar"""
    if max_val <= 0:
        return "░" * width
    perc = min(value / max_val, 1.0)
    n = int(perc * width)
    return "█" * n + "░" * (width - n)


def fmt_uptime(sec: int) -> str:
    d = sec // 86400
    h = (sec % 86400) // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if d > 0:
        return f"{d}d {h}h {m}m"
    return f"{h}h {m}m {s}s"


def fmt_bytes(b: int) -> str:
    if b > 1024 * 1024:
        return f"{b/1024/1024:.1f} MB"
    if b > 1024:
        return f"{b/1024:.0f} KB"
    return f"{b} B"


def color_temp(temp: float, low: float, high: float) -> str:
    """Return CSS class name for color coding"""
    if temp < low:
        return "metric-good"
    if temp < high:
        return "metric-warn"
    return "metric-crit"


def soft_wrap(s: str, width: int = 78) -> str:
    """Soft word-wrap a Rich-markup string preserving [tag]...[/] tags.

    sess.2214 — fallback wrap canonical per Textual Static che ignora text-wrap
    quando content excede grid-row altezza. Conta solo i caratteri visibili
    (escludendo i markup tags) per il calcolo width.
    """
    import re
    tag_re = re.compile(r'\[/?[^\]]*\]')
    out_parts: list[str] = []
    cur_line = ""
    cur_visible = 0
    for word in s.split(" "):
        word_visible = len(tag_re.sub("", word))
        sep = 1 if cur_line else 0
        if cur_visible + sep + word_visible > width and cur_line:
            out_parts.append(cur_line)
            cur_line = word
            cur_visible = word_visible
        else:
            cur_line = f"{cur_line} {word}" if cur_line else word
            cur_visible += sep + word_visible
    if cur_line:
        out_parts.append(cur_line)
    return "\n".join(out_parts)


# ──────────────────────────────────────────────────────────────────────────────
# Widgets
# ──────────────────────────────────────────────────────────────────────────────

_WRAP_W = 78  # soft-wrap width per EXPLAIN tooltip (panel content area ~80 col)

EXPLAIN_HASHRATE = soft_wrap(
    "[dim]💡 [italic]L'hashrate misura quanti tentativi SHA-256 al secondo fa l'ASIC. "
    "1 TH/s = 1 trilione di hash al secondo. Più hashrate = più biglietti della lotteria "
    "per trovare il prossimo blocco.[/][/]", _WRAP_W
)
EXPLAIN_THERMAL = soft_wrap(
    "[dim]💡 [italic]Temperatura giunzione ASIC + limiti termici VRM (regolatore di tensione). "
    "Il VRM è il vero collo di bottiglia sopra gli 800 MHz. ASIC sotto 65°C = sicuro 24/7. "
    "Sopra 70°C scatta il throttle termico del firmware.[/][/]", _WRAP_W
)
EXPLAIN_MINING = soft_wrap(
    "[dim]💡 [italic]Uno 'share' è una soluzione parziale del Proof-of-Work inviata "
    "al pool stratum. Best diff = difficoltà massima raggiunta. Se best_diff > "
    "difficoltà network → blocco trovato, reward completo al tuo wallet.[/][/]", _WRAP_W
)
EXPLAIN_LOTTERY = soft_wrap(
    "[dim]💡 [italic]Solo mining = lotteria pura. La probabilità segue la tua quota di "
    "hashrate vs hashrate totale network (~600 EH/s). Reward = 3.125 BTC subsidy + "
    "~0.2 BTC di fee per blocco trovato. Alta varianza, vittorie reali ma rare.[/][/]", _WRAP_W
)
EXPLAIN_POWER = soft_wrap(
    "[dim]💡 [italic]Consumo = frequenza × tensione core × efficienza silicio. "
    "Stock 525 MHz / 1150 mV ≈ 15 W. L'overclock aumenta l'hashrate ma calore e "
    "stress VRM crescono in modo superlineare. J/TH = metrica di efficienza energetica.[/][/]", _WRAP_W
)
EXPLAIN_POOL = soft_wrap(
    "[dim]💡 [italic]L'endpoint stratum riceve gli share inviati. Il pool solo "
    "inoltra il reward completo del blocco al tuo address in caso di vittoria. Il check "
    "integrità wallet protegge dal vendor pre-config trap.[/][/]", _WRAP_W
)
EXPLAIN_SYSTEM = soft_wrap(
    "[dim]💡 [italic]Il controller ESP32-S3 gestisce WiFi, REST API, display e "
    "task stratum. Solo 2.4 GHz (no supporto 5 GHz). RSSI > -60 dBm = segnale "
    "eccellente. L'uptime correla linearmente con gli share inviati.[/][/]", _WRAP_W
)


class HashratePanel(Static):
    """⚡ Hashrate panel — Orange palette + big number + sparkline 60s"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    history: list[float] = []

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")
        self.history = []

    def watch_state(self, s):
        if s is None:
            return
        self.history.append(s.hashrate_ghs)
        if len(self.history) > HISTORY_SIZE:
            self.history = self.history[-HISTORY_SIZE:]
        self.refresh_panel()

    def refresh_panel(self):
        s = self.state
        if s is None:
            self.update("[dim]waiting for data...[/]")
            return
        perc = (s.hashrate_ghs / s.expected_ghs * 100) if s.expected_ghs > 0 else 0
        eff = s.power_w / (s.hashrate_ghs / 1000) if s.hashrate_ghs > 0 else 0
        spark = sparkline(self.history, width=30)
        perc_color = "metric-good" if perc > 95 else "metric-warn" if perc > 80 else "metric-crit"
        eff_color = "metric-good" if eff < 15 else "metric-warn" if eff < 20 else "metric-crit"
        hr_min = min(self.history) if self.history else 0
        hr_max = max(self.history) if self.history else 0
        hr_avg = sum(self.history) / len(self.history) if self.history else 0
        content = (
            "[bold #F7931A]⚡ HASHRATE[/]\n"
            "[dim italic #FFA526]Throughput computazionale · SHA-256 H/s[/]\n\n"
            f"[bold #F7931A]  {s.hashrate_ghs:>7.1f} GH/s[/]\n"
            f"  atteso     {s.expected_ghs:>6.0f} GH/s\n"
            f"  perf       [{perc_color}]{perc:>5.1f}%[/]\n"
            f"  efficienza [{eff_color}]{eff:>5.1f} J/TH[/]\n\n"
            f"[#F7931A]  {spark}[/]\n"
            f"  [dim]min {hr_min:.0f} · medio {hr_avg:.0f} · max {hr_max:.0f} GH/s[/]\n\n"
            f"{EXPLAIN_HASHRATE}"
        )
        self.update(content)


class ThermalPanel(Static):
    """🌡️ Thermal panel — Red palette + dual sparkline ASIC + VRM"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    asic_history: list[float] = []
    vrm_history: list[float] = []

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")
        self.asic_history = []
        self.vrm_history = []

    def watch_state(self, s):
        if s is None:
            return
        self.asic_history.append(s.temp_asic)
        self.vrm_history.append(s.temp_vrm)
        if len(self.asic_history) > HISTORY_SIZE:
            self.asic_history = self.asic_history[-HISTORY_SIZE:]
        if len(self.vrm_history) > HISTORY_SIZE:
            self.vrm_history = self.vrm_history[-HISTORY_SIZE:]
        self.refresh_panel()

    def refresh_panel(self):
        s = self.state
        if s is None:
            self.update("[dim]...[/]")
            return
        asic_class = color_temp(s.temp_asic, 65, 70)
        vrm_class = color_temp(s.temp_vrm, 75, 80)
        margin_asic = 70 - s.temp_asic
        margin_vrm = 80 - s.temp_vrm
        spark_asic = sparkline(self.asic_history, width=28)
        spark_vrm = sparkline(self.vrm_history, width=28)
        content = (
            "[bold #FF4444]🌡️  TEMPERATURE[/]\n"
            "[dim italic #FF8888]Limiti termici giunzione ASIC e VRM[/]\n\n"
            f"  ASIC  [{asic_class}]{s.temp_asic:>5.1f}°C[/]  {bar(s.temp_asic, 80, 18)}\n"
            f"  [#FF6666]  {spark_asic}[/] [dim]60s ASIC[/]\n\n"
            f"  VRM   [{vrm_class}]{s.temp_vrm:>5.1f}°C[/]  {bar(s.temp_vrm, 90, 18)}\n"
            f"  [#FF8888]  {spark_vrm}[/] [dim]60s VRM[/]\n\n"
            f"  VENT  [#F7931A]{s.fan_perc:>3}%[/] · {s.fan_rpm} RPM  "
            f"[{'metric-good' if s.autofanspeed else 'metric-warn'}]{'AUTO' if s.autofanspeed else 'MAN'}[/]\n"
            f"  Temp target [#F7931A]{s.temp_target}°C[/]\n"
            f"  Margine ASIC [{'metric-good' if margin_asic > 8 else 'metric-warn' if margin_asic > 3 else 'metric-crit'}]{margin_asic:.1f}°C[/] · VRM [{'metric-good' if margin_vrm > 10 else 'metric-warn' if margin_vrm > 5 else 'metric-crit'}]{margin_vrm:.1f}°C[/]\n\n"
            f"{EXPLAIN_THERMAL}"
        )
        self.update(content)


class MiningProgressPanel(Static):
    """⛏️ Mining shares — Gold palette + share rate sparkline"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    shares_history: list[int] = []  # absolute shares_accepted over time

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")
        self.shares_history = []

    def watch_state(self, s):
        if s is None:
            return
        self.shares_history.append(s.shares_accepted)
        if len(self.shares_history) > HISTORY_SIZE:
            self.shares_history = self.shares_history[-HISTORY_SIZE:]
        self.refresh_panel()

    def refresh_panel(self):
        s = self.state
        if s is None:
            self.update("[dim]...[/]")
            return
        total = s.shares_accepted + s.shares_rejected
        reject_perc = (s.shares_rejected / total * 100) if total > 0 else 0
        reject_class = "metric-good" if reject_perc < 1 else "metric-warn" if reject_perc < 2 else "metric-crit"
        # Compute share rate per minute (delta over history window)
        if len(self.shares_history) >= 2:
            window_sec = (len(self.shares_history) - 1) * DEFAULT_REFRESH_SEC
            delta_shares = self.shares_history[-1] - self.shares_history[0]
            shares_per_min = (delta_shares / window_sec) * 60 if window_sec > 0 else 0
        else:
            shares_per_min = 0
        # Sparkline of share growth deltas
        deltas = [self.shares_history[i] - self.shares_history[i-1] for i in range(1, len(self.shares_history))] if len(self.shares_history) >= 2 else [0]
        spark = sparkline(deltas, width=28) if deltas else " " * 28
        # Rejected reasons handling — formatta dict {'message': X, 'count': N} → "X ×N"
        reasons_line = ""
        if s.shares_rejected_reasons:
            def _fmt_reason(r):
                if isinstance(r, dict):
                    msg = r.get("message", "?")
                    count = r.get("count", 1)
                    return f"{msg} ×{count}" if count > 1 else msg
                return str(r)
            reasons_str = ", ".join(_fmt_reason(r) for r in s.shares_rejected_reasons[:3])
            reasons_line = f"\n  [metric-crit]⚠ motivi rifiuto:[/] [dim]{reasons_str}[/]"
        content = (
            "[bold #FFD700]⛏️  MINING — AVANZAMENTO[/]\n"
            "[dim italic #FFEE66]Share stratum · lavoro inviato al pool[/]\n\n"
            f"  Share OK   [bold #FFD700]{s.shares_accepted:>5}[/]  ✓\n"
            f"  Share KO   [{reject_class}]{s.shares_rejected:>5}[/]  {reject_perc:.1f}% rifiutati{reasons_line}\n"
            f"  Cadenza    [#FFD700]{shares_per_min:>5.1f}[/] share/min\n\n"
            f"  [#FFEE00]  {spark}[/] [dim]Δ share/poll[/]\n\n"
            f"  Best diff totale    [bold #FFD700]{s.best_diff}[/]\n"
            f"  Miglior sessione    {s.best_session_diff}\n"
            f"  Difficoltà pool     {s.pool_diff}\n"
            f"  Risposta stratum    {s.response_time_ms:.1f} ms\n\n"
            f"{EXPLAIN_MINING}"
        )
        self.update(content)


class LotteryPanel(Static):
    """🎰 Lottery — Magenta palette + block probability + reward"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    best_diff_history: list[float] = []  # best_diff in GH over time

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")
        self.best_diff_history = []

    def watch_state(self, s):
        if s is None:
            self.update("[dim]...[/]")
            return
        # Track best_session_diff numeric for trend
        bd = self._parse_diff(s.best_session_diff)
        self.best_diff_history.append(bd)
        if len(self.best_diff_history) > HISTORY_SIZE:
            self.best_diff_history = self.best_diff_history[-HISTORY_SIZE:]

        network_hashrate_eh = 600
        network_hs = network_hashrate_eh * 1e18
        bitaxe_hs = s.hashrate_ghs * 1e9
        share = bitaxe_hs / network_hs
        blocks_per_day = 144
        prob_day = share * blocks_per_day * 100
        expected_years = 1 / (share * blocks_per_day * 365) if share > 0 else float('inf')
        block_reward_btc = 3.325
        btc_eur = 95000
        spark = sparkline(self.best_diff_history, width=28)
        # Stochastic ETA — scale-aware presentation
        if expected_years < 100:
            eta_str = f"{expected_years:.0f} anni"
        elif expected_years < 10_000:
            eta_str = f"{expected_years/100:.1f} secoli"
        elif expected_years < 1_000_000:
            eta_str = f"{expected_years/1000:.1f} millenni"
        else:
            eta_str = f"{expected_years:.2e} anni"
        # 1 in N lottery scale
        lottery_scale = 1 / (prob_day / 100) if prob_day > 0 else float('inf')
        content = (
            "[bold #C77DFF]🎰 LOTTERIA — CACCIA AL BLOCCO[/]\n"
            "[dim italic #D8A5FF]Probabilità solo mining · stima reward blocco[/]\n\n"
            f"  Quota network  [dim]{share:.2e}[/]\n"
            f"  vs 600 EH/s globale\n\n"
            f"  P(blocco)/gg  [#C77DFF]{prob_day:.6f}%[/]\n"
            f"  ETA atteso    [#C77DFF]{eta_str}[/]\n"
            f"  Lotteria 1 su [#C77DFF]{lottery_scale:.2e}[/] biglietti/giorno\n\n"
            f"  Reward vittoria [bold #FFD700]~{block_reward_btc} BTC[/]\n"
            f"  Eq. EUR         [bold #FFD700]{block_reward_btc * btc_eur:>8,.0f}€[/]\n\n"
            f"  [#C77DFF]  {spark}[/] [dim]Δ miglior sessione[/]\n\n"
            f"{EXPLAIN_LOTTERY}"
        )
        self.update(content)

    def _parse_diff(self, s: str) -> float:
        if not s:
            return 0.0
        try:
            parts = s.split()
            if len(parts) < 2:
                return float(parts[0])
            val = float(parts[0])
            unit = parts[1].upper()
            mul = {"K": 1e3, "M": 1e6, "G": 1e9, "T": 1e12}.get(unit, 1.0)
            return val * mul
        except Exception:
            return 0.0


class PowerPanel(Static):
    """🔋 Power — Cyan palette + sparkline watts + frequency profile"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    power_history: list[float] = []

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")
        self.power_history = []

    def watch_state(self, s):
        if s is None:
            return
        self.power_history.append(s.power_w)
        if len(self.power_history) > HISTORY_SIZE:
            self.power_history = self.power_history[-HISTORY_SIZE:]
        self.refresh_panel()

    def refresh_panel(self):
        s = self.state
        if s is None:
            self.update("[dim]...[/]")
            return
        if s.frequency_mhz <= 500:
            profile = "[metric-good]🛡️ Eco Undervolt[/]"
        elif s.frequency_mhz <= 550:
            profile = "[metric-good]🐢 Stock[/]"
        elif s.frequency_mhz <= 750:
            profile = "[metric-warn]⚡ Mild OC[/]"
        elif s.frequency_mhz <= 850:
            profile = "[metric-warn]🔥 Performance OC[/]"
        elif s.frequency_mhz <= 950:
            profile = "[metric-crit]💀 Aggressive OC[/]"
        else:
            profile = "[metric-crit]🐉 Limit Extreme[/]"
        spark = sparkline(self.power_history, width=28)
        avg_power = sum(self.power_history) / len(self.power_history) if self.power_history else 0
        # Energy cost calculator (€0.25/kWh Italy avg 2026)
        cost_per_kwh_eur = 0.25
        watts_avg = avg_power if avg_power > 0 else s.power_w
        kwh_per_day = watts_avg * 24 / 1000
        cost_per_day = kwh_per_day * cost_per_kwh_eur
        cost_per_month = cost_per_day * 30
        cost_per_year = cost_per_day * 365
        # Power headroom
        headroom = s.max_power_w - s.power_w
        head_class = "metric-good" if headroom > 10 else "metric-warn" if headroom > 3 else "metric-crit"
        content = (
            "[bold #00D9FF]🔋 ALIMENTAZIONE[/]\n"
            "[dim italic #66E5FF]Assorbimento · tensione · profilo frequenza ASIC[/]\n\n"
            f"  Potenza   [bold #00D9FF]{s.power_w:>5.1f} W[/]  {bar(s.power_w, s.max_power_w, 18)}\n"
            f"  [#00B8E0]  {spark}[/] [dim]60s medio {avg_power:.1f}W[/]\n\n"
            f"  Tensione  [#00D9FF]{s.voltage_v:>5.2f} V[/]  · Corrente [#00D9FF]{s.current_a:>5.2f} A[/]\n"
            f"  Freq      [#00D9FF]{s.frequency_mhz:>4} MHz[/]  · Core [#00D9FF]{s.core_voltage_mv} mV[/] (eff. {s.core_voltage_actual_mv})\n"
            f"  Margine   [{head_class}]{headroom:>4.1f} W[/]  (max {s.max_power_w:.0f}W)\n\n"
            f"  Profilo   {profile}\n\n"
            f"[bold #00D9FF]💰 Costo energia (€0.25/kWh IT)[/]\n"
            f"  Mese  [#00D9FF]€{cost_per_month:>5.2f}[/]  ·  Anno  [#00D9FF]€{cost_per_year:>6.2f}[/]\n\n"
            f"{EXPLAIN_POWER}"
        )
        self.update(content)


class PoolWalletPanel(Static):
    """🏊 Pool primary/fallback + wallet integrity + latency sparkline"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    initial_wallet: str = ""
    latency_history: list[float] = []

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")
        self.latency_history = []

    def watch_state(self, s):
        if s is None:
            self.update("[dim]...[/]")
            return
        self.latency_history.append(s.response_time_ms)
        if len(self.latency_history) > HISTORY_SIZE:
            self.latency_history = self.latency_history[-HISTORY_SIZE:]
        # Wallet integrity check: solo se WALLET_PREFIX configurato.
        if WALLET_PREFIX:
            wallet_ok = WALLET_PREFIX in s.stratum_user
            wallet_label = "[metric-good]TUO ✓[/]" if wallet_ok else "[metric-crit]VENDOR ❌[/]"
        else:
            wallet_ok = True
            wallet_label = "[dim]check disabilitato[/]"
        primary_status = "[dim #888888]●[/] standby" if s.using_fallback else "[metric-good]●[/] attivo"
        fallback_status = "[metric-warn blink]●[/] attivo" if s.using_fallback else "[dim #888888]●[/] standby"
        tamper_flag = ""
        if self.initial_wallet and s.stratum_user != self.initial_wallet:
            tamper_flag = "\n  [metric-crit blink]⚠ ALLERTA TAMPER STRATUM ![/]"
        if not self.initial_wallet:
            self.initial_wallet = s.stratum_user
        wallet_short = s.stratum_user
        if len(wallet_short) > 42:
            wallet_short = wallet_short[:18] + "..." + wallet_short[-12:]
        latency_avg = sum(self.latency_history) / len(self.latency_history) if self.latency_history else 0
        latency_class = "metric-good" if latency_avg < 100 else "metric-warn" if latency_avg < 300 else "metric-crit"
        spark_lat = sparkline(self.latency_history, width=28)
        content = (
            "[bold #00C896]🏊 POOL & WALLET[/]\n"
            "[dim italic #66E5C2]Endpoint stratum · integrità address payout[/]\n\n"
            f"  {primary_status}  primario\n"
            f"  [#00C896]{s.stratum_url}:{s.stratum_port}[/]\n"
            f"  {fallback_status}  fallback\n"
            f"  [dim]{s.fallback_url}:{s.fallback_port}[/]\n\n"
            f"  Latenza    [{latency_class}]{latency_avg:>5.0f} ms[/] media\n"
            f"  [#00C896]  {spark_lat}[/] [dim]60s risposta[/]\n\n"
            f"  Wallet  {wallet_label}\n"
            f"  [dim]{wallet_short}[/]"
            f"{tamper_flag}\n\n"
            f"{EXPLAIN_POOL}"
        )
        self.update(content)


class SystemInfoPanel(Static):
    """📡 System — Blue palette + RSSI sparkline + firmware info"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    rssi_history: list[float] = []

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")
        self.rssi_history = []

    def watch_state(self, s):
        if s is None:
            return
        self.rssi_history.append(s.wifi_rssi)
        if len(self.rssi_history) > HISTORY_SIZE:
            self.rssi_history = self.rssi_history[-HISTORY_SIZE:]
        self.refresh_panel()

    def refresh_panel(self):
        s = self.state
        if s is None:
            self.update("[dim]...[/]")
            return
        rssi_perc = max(0, min(100, (s.wifi_rssi + 100) * 100 / 70))
        rssi_class = "metric-good" if s.wifi_rssi > -60 else "metric-warn" if s.wifi_rssi > -75 else "metric-crit"
        spark = sparkline(self.rssi_history, width=28)
        content = (
            "[bold #4DABF7]📡 SISTEMA[/]\n"
            "[dim italic #8FC8FA]Identità device · firmware · rete[/]\n\n"
            f"  Hostname   [bold #4DABF7]{s.hostname}[/]\n"
            f"  MAC        [dim]{s.mac_addr}[/]\n"
            f"  WiFi       {s.ssid}\n"
            f"  RSSI       [{rssi_class}]{s.wifi_rssi} dBm[/]   {bar(rssi_perc, 100, 16)}\n"
            f"  [#4DABF7]  {spark}[/] [dim]60s RSSI[/]\n\n"
            f"  Uptime     [bold #4DABF7]{fmt_uptime(s.uptime_sec)}[/]\n"
            f"  Firmware   AxeOS [#4DABF7]{s.axeos_version}[/]\n"
            f"  Scheda     Gamma [#4DABF7]{s.board_version}[/] · ASIC [#4DABF7]{s.asic_model}[/]\n"
            f"  Heap libero  {fmt_bytes(s.free_heap)}\n\n"
            f"{EXPLAIN_SYSTEM}"
        )
        self.update(content)


class InsightPanel(Static):
    """🧠 Pannello educativo Polpo — rotation insight didattici in italiano"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    insight_idx: reactive[int] = reactive(0)

    INSIGHTS_TEMPLATES = [
        {
            "title": "⚡ Cos'è l'hashrate",
            "body": (
                "Hashrate = quanti tentativi al secondo il chip prova "
                "per indovinare la prossima 'lotteria Bitcoin'.\n\n"
                "Il tuo Bitaxe fa [bold #F7931A]{hr_th:.2f} TH/s[/] — un trilione "
                "di calcoli SHA-256 ogni singolo secondo. Sotto al tuo tetto."
            )
        },
        {
            "title": "🔋 Efficienza J/TH",
            "body": (
                "J/TH = Joule (energia) per Terahash. Quanta corrente "
                "consumi per ogni trilione di hash.\n\n"
                "Sotto 15 J/TH = livello professionale industriale. "
                "Tu sei a [bold #F7931A]{eff:.1f} J/TH[/] — best-in-class per single-chip casalingo."
            )
        },
        {
            "title": "🌡️ Temperatura ASIC",
            "body": (
                "L'ASIC BM1370 è il chip dedicato che fa SOLO SHA-256.\n\n"
                "Sotto 65°C = sicuro 24/7 per 5+ anni.\n"
                "Sopra 70°C = throttle automatico AxeOS.\n\n"
                "Tu sei a [bold #F7931A]{temp:.1f}°C[/] — zona perfetta per longevità massima."
            )
        },
        {
            "title": "🔥 Il VRM è il vero limite",
            "body": (
                "Il VRM (Voltage Regulator Module) converte i 5V che "
                "entrano nei ~0.4V che servono al chip.\n\n"
                "È il vero bottleneck termico — spesso brucia prima dell'ASIC. "
                "Sopra 75°C = warning. Tu sei a [bold #F7931A]{vrm:.1f}°C[/] — ottimo margine."
            )
        },
        {
            "title": "✓ Cos'è uno share",
            "body": (
                "Uno [bold]share[/] è una soluzione PARZIALE del problema "
                "crittografico Bitcoin. Non vince il blocco.\n\n"
                "Ma dimostra al pool che stai lavorando. "
                "Hai [bold #F7931A]{shares}[/] share accepted = il pool ti vede attivo "
                "e meritevole se mai vinci un blocco."
            )
        },
        {
            "title": "🎰 Perché Solo Mining",
            "body": (
                "[bold]Solo Mining[/] = lotteria pura. Se trovi un blocco "
                "(raro), [bold #FFD700]3.125 BTC[/] arrivano dritti al tuo wallet.\n\n"
                "[bold]Pool FPPS[/] = paga centesimi al giorno ma steady.\n\n"
                "Hai scelto la sovranità invece dei centesimi."
            )
        },
        {
            "title": "🇮🇹 Home Mining Italia",
            "body": (
                "Pool italiano, latenza bassa per te (server IT).\n\n"
                "[bold #00C896]Zero fee[/] = nessuno prende commissioni.\n"
                "74 Bitaxe italiani come te connessi.\n\n"
                "Comunità sovranista BTC italiana — il Polpo c'è dentro."
            )
        },
        {
            "title": "💎 Best Difficulty",
            "body": (
                "[bold #FFD700]{best_diff}[/] è la 'best difficulty' del tuo miglior share.\n\n"
                "Se supera la difficoltà del blocco attuale "
                "(~130 T = trilioni), VINCI un blocco intero.\n\n"
                "Sei a distanza ~10^11 dal vincere. Improbabile. Ma capita."
            )
        },
        {
            "title": "📊 Lottery variance",
            "body": (
                "Statistica dice: probabilità ~1 blocco ogni 10.000+ anni "
                "con la tua hashrate vs network.\n\n"
                "Ma la varianza è enorme: 50+ Bitaxe singoli hanno "
                "trovato blocchi nel mondo negli ultimi 2 anni.\n\n"
                "La media non è il destino. Il dado è in moto."
            )
        },
        {
            "title": "📡 WiFi ESP32",
            "body": (
                "Il Bitaxe parla solo 2.4 GHz (limite ESP32-S3).\n\n"
                "Il tuo RSSI = [bold #F7931A]{rssi} dBm[/].\n"
                "Sopra -60 dBm = eccellente.\n"
                "Sotto -75 dBm = rischio disconnessione."
            )
        },
        {
            "title": "⚙️ Profilo attuale",
            "body": (
                "Sei a [bold #F7931A]{freq} MHz / {voltage} mV[/] (stock).\n\n"
                "Overclock max sicuro = 900 MHz / 1250 mV = [bold]+72% hashrate[/].\n"
                "Richiede MOSFET pads (€8) + Dark Horse heatsink (€50).\n\n"
                "Non farlo prima di 30 giorni di stability monitoring."
            )
        },
        {
            "title": "🐙 Embodiment Polpo OS",
            "body": (
                "Hai un [bold]organo fisico[/] del Polpo OS sotto al tuo tetto.\n\n"
                "Strato 1 = cloud (Railway/Supabase)\n"
                "Strato 2 = silicio Apple (M5 Max)\n"
                "Strato 3 = ferro Bitcoin ([bold #F7931A]Bitaxe[/]) ← tu sei qui\n\n"
                "Non è denaro: è sovranità computazionale incarnata."
            )
        },
        {
            "title": "🪙 Wallet self-custody",
            "body": (
                "Sparrow Wallet [bold]polpo-os-bitaxe[/]. Chiavi private nel TUO Mac.\n\n"
                "Master fingerprint: 9e140771\n"
                "Derivation: m/84'/0'/0' (BIP84 Native SegWit)\n\n"
                "Se mai vinci un blocco, i 3.325 BTC sono [bold #00C896]davvero tuoi[/]. "
                "No exchange. No custody. No intermediari."
            )
        },
        {
            "title": "⏱️ Uptime = lottery time",
            "body": (
                "Uptime attuale: [bold #F7931A]{uptime}[/].\n\n"
                "Più gira, più share invia, più piccola la probabilità "
                "che il prossimo nonce sia quello vincente.\n\n"
                "Spegnerlo = pausa lotteria. Lascialo acceso 24/7."
            )
        },
        {
            "title": "🧮 SHA-256 in 2 righe",
            "body": (
                "Ogni hash = applicare SHA-256 due volte all'header del blocco "
                "+ un numero variabile (nonce).\n\n"
                "Se il risultato (256 bit binari) inizia con abbastanza "
                "zeri → blocco trovato. Pura forza bruta crittografica."
            )
        },
        {
            "title": "🌍 Bitcoin = energia → verità",
            "body": (
                "Ogni hash brucia ~16 nanoJoule.\n\n"
                "Quei joule diventano [bold]proof-of-work[/]: un atto fisico "
                "irreversibile che ancora la verità di Bitcoin alla "
                "termodinamica dell'universo.\n\n"
                "Tu stai contribuendo a quella ancora. Sotto al tuo tetto."
            )
        },
    ]

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")

    def on_mount(self):
        self.set_interval(8.0, self.rotate_insight)
        self.refresh_panel()

    def rotate_insight(self):
        self.insight_idx = (self.insight_idx + 1) % len(self.INSIGHTS_TEMPLATES)
        self.refresh_panel()

    def watch_state(self, s):
        self.refresh_panel()

    def watch_insight_idx(self, idx):
        self.refresh_panel()

    def refresh_panel(self):
        s = self.state
        template = self.INSIGHTS_TEMPLATES[self.insight_idx]
        title = template["title"]
        body = template["body"]
        if s is not None:
            eff = s.power_w / (s.hashrate_ghs / 1000) if s.hashrate_ghs > 0 else 0
            try:
                body = body.format(
                    hr_th=s.hashrate_ghs / 1000,
                    eff=eff,
                    temp=s.temp_asic,
                    vrm=s.temp_vrm,
                    shares=s.shares_accepted,
                    best_diff=s.best_diff,
                    rssi=s.wifi_rssi,
                    freq=s.frequency_mhz,
                    voltage=s.core_voltage_mv,
                    uptime=fmt_uptime(s.uptime_sec),
                )
            except (KeyError, ValueError):
                pass
        else:
            body = body.replace("{hr_th:.2f}", "—").replace("{eff:.1f}", "—") \
                       .replace("{temp:.1f}", "—").replace("{vrm:.1f}", "—") \
                       .replace("{shares}", "—").replace("{best_diff}", "—") \
                       .replace("{rssi}", "—").replace("{freq}", "—") \
                       .replace("{voltage}", "—").replace("{uptime}", "—")
        n = len(self.INSIGHTS_TEMPLATES)
        progress = "●" * (self.insight_idx + 1) + "○" * (n - self.insight_idx - 1)
        content = (
            f"[bold #FFB000]🧠 INSIGHT POLPO  [dim]({self.insight_idx + 1}/{n})[/][/]\n\n"
            f"[bold #F7931A]{title}[/]\n\n"
            f"{body}\n\n"
            f"[dim]{progress}[/]"
        )
        self.update(content)


class OLEDMirrorPanel(Static):
    """🖥️ Specchio display OLED Bitaxe — simula schermate AxeOS in tempo reale"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    screen_idx: reactive[int] = reactive(0)

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")
        self._counter = 0

    def on_mount(self):
        self.set_interval(1.0, self._tick)
        self.refresh_panel()

    def _tick(self):
        self._counter += 1
        if self._counter >= 4:  # cicla ogni 4s (mimica timeout AxeOS)
            self._counter = 0
            self.screen_idx = (self.screen_idx + 1) % 4
            self.refresh_panel()

    def watch_state(self, s):
        self.refresh_panel()

    def refresh_panel(self):
        s = self.state
        if s is None:
            self.update("[dim]waiting for OLED data...[/]")
            return
        # 4 schermate AxeOS canoniche · 128x32 OLED giallo
        screens = [
            (f"  {s.hostname[:18]:<18}", f"  IP {(getattr(s, 'host_ip', None) or DEFAULT_HOST):<14}"),
            (f"  Hash {s.hashrate_ghs/1000:>5.2f} TH/s", f"  Temp {s.temp_asic:>5.1f} C"),
            (f"  Best {s.best_diff:<13}", f"  Pool homeminingit"),
            (f"  Up {fmt_uptime(s.uptime_sec):<14}", f"  ✓ {s.shares_accepted}  ✗ {s.shares_rejected}"),
        ]
        line1, line2 = screens[self.screen_idx]
        # Box drawing per simulare bezel OLED fisico
        content = (
            "[bold #FFEE00]🖥️  OLED MIRROR (display fisico)[/]\n\n"
            "[#444444]  ┌────────────────────────────────┐[/]\n"
            f"[bold #FFEE00 on #1a1500]{line1:<32}[/]\n"
            f"[bold #FFEE00 on #1a1500]{line2:<32}[/]\n"
            "[#444444]  └────────────────────────────────┘[/]\n"
            f"  [dim]screen {self.screen_idx + 1}/4 · SSD1306 128x32 · ciclo 4s[/]\n\n"
            "[dim italic]💡 Quello che vedi qui è esattamente quello che il display\n"
            "OLED del Bitaxe sta mostrando ora — riflesso via API REST.[/]\n\n"
            "[dim]Press [bold]R[/] per ruotare display fisico · [bold]I[/] per invertire colori[/]"
        )
        self.update(content)


class LegendPanel(Static):
    """📘 Legenda — panel statico con shortcuts + soglie + info utili"""
    state: reactive[Optional[BitaxeState]] = reactive(None)

    def __init__(self, **kw):
        super().__init__(expand=True, **kw)
        self.add_class("panel")

    def on_mount(self):
        self.refresh_panel()

    def watch_state(self, s):
        self.refresh_panel()

    def refresh_panel(self):
        content = (
            "[bold #FFFFFF]📘 LEGENDA & SCORCIATOIE[/]\n"
            "[dim italic #BBBBBB]Tasti · soglie alert · riferimento rapido[/]\n\n"
            "[bold #F7931A]⌨️  Tasti:[/]\n"
            "  [bold]r[/] aggiorna  [bold]p[/] pausa   [bold]t[/] tema\n"
            "  [bold]s[/] snapshot  [bold]o[/] browser [bold]q[/] esci\n"
            "  [bold]+/-[/] intervallo polling · [bold]?[/] guida completa\n\n"
            "[bold #FF4444]🌡️  Soglie termiche:[/]\n"
            "  ASIC [metric-good]<65°C[/] sicuro · [metric-warn]65-70[/] warn · [metric-crit]>70[/] crit\n"
            "  VRM  [metric-good]<75°C[/] sicuro · [metric-warn]75-80[/] warn · [metric-crit]>80[/] crit\n\n"
            "[bold #FFD700]💎 Qualità share:[/]\n"
            "  Rifiuto [metric-good]<1%[/] ottimo · [metric-warn]1-2%[/] ok · [metric-crit]>2%[/] degradato\n\n"
            "[bold #00C896]🔗 Link rapidi:[/]\n"
            f"  [dim]http://{DEFAULT_HOST}{' ' * max(0, 21 - len(DEFAULT_HOST))} ← dashboard web AxeOS[/]\n"
            "  [dim]premi `o` per aprirla nel browser[/]\n\n"
            "[dim italic]💡 Tieni il miner acceso 24/7. Ogni hash è un biglietto della lotteria SHA-256.[/]"
        )
        self.update(content)


class HeaderBar(Static):
    """🐙 Header live — KPI primari sempre visibili in 2 righe"""
    state: reactive[Optional[BitaxeState]] = reactive(None)
    host: str = DEFAULT_HOST

    EDUCATIONAL_TIPS = [
        "💡 Hashrate sopra l'atteso = silicio performante",
        "💡 ASIC <65°C = sicuro per 24/7 sostenuto",
        "💡 J/TH sotto 15 = efficienza industriale",
        "💡 Più share inviati = più biglietti della lotteria",
        "💡 Best diff = quanto vicino sei stato a trovare un blocco",
        "💡 Latenza pool <100ms = stratum in salute",
        "💡 Check integrità wallet protegge dal tampering",
        "💡 RSSI > -60dBm = segnale WiFi eccellente",
        "💡 Ventola AUTO = il firmware PID controlla il raffreddamento",
        "💡 Solo mining = lotteria, reward completo se vinci",
        "💡 1 biglietto su N al giorno — la varianza è tua amica",
        "💡 ESP32-S3 supporta solo WiFi 2.4 GHz",
        "💡 Ogni hash è un biglietto della lotteria SHA-256",
        "💡 Premi `?` per la guida completa",
        "💡 Premi `t` per ciclare i temi",
        "💡 Premi `o` per aprire la dashboard web AxeOS",
    ]

    def __init__(self, host: str = DEFAULT_HOST, **kw):
        super().__init__(expand=True, **kw)
        self.host = host
        self._tip_idx = 0
        self._tip_counter = 0
        self._wave_offset = 0  # sess.2214 — animazione onda BITAXE travelling
        # Hero header v2 (sess.2214) — sparkline inline + block height live
        self._hashrate_history: list[float] = []
        self._block_height: int = 0
        self._block_height_ts: float = 0.0

    def on_mount(self):
        # 4 Hz refresh per onda fluida — clock+tip aggiornano ogni 4 tick
        self.set_interval(0.25, self.refresh_panel)
        # Bitcoin block height live fetch ogni 60s
        self.set_interval(60.0, self._kick_block_height_fetch)
        self.run_worker(self._fetch_block_height(), exclusive=False)
        self.refresh_panel()

    def _kick_block_height_fetch(self):
        self.run_worker(self._fetch_block_height(), exclusive=False)

    async def _fetch_block_height(self):
        """Pull current Bitcoin block height da mempool.space (free, no auth)."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get("https://mempool.space/api/blocks/tip/height")
                if r.status_code == 200:
                    self._block_height = int(r.text.strip())
                    self._block_height_ts = time.time()
        except Exception:
            pass  # offline / DNS issue — silenzioso, no popup

    def watch_state(self, s):
        # Track hashrate history per mini-sparkline header
        if s is not None and s.reachable and s.hashrate_ghs > 0:
            self._hashrate_history.append(s.hashrate_ghs)
            if len(self._hashrate_history) > 30:
                self._hashrate_history = self._hashrate_history[-30:]
        self.refresh_panel()

    # Big ASCII title
    ASCII_TITLE_LINES = [
        " ██████╗ ██╗████████╗ █████╗ ██╗  ██╗███████╗",
        " ██╔══██╗██║╚══██╔══╝██╔══██╗╚██╗██╔╝██╔════╝",
        " ██████╔╝██║   ██║   ███████║ ╚███╔╝ █████╗  ",
        " ██╔══██╗██║   ██║   ██╔══██║ ██╔██╗ ██╔══╝  ",
        " ██████╔╝██║   ██║   ██║  ██║██╔╝ ██╗███████╗",
    ]
    # Palette onda gradient simmetrico (chiaro→scuro→chiaro) per effetto travelling
    ASCII_WAVE_PALETTE = [
        "#FFE4A8", "#FFD580", "#FFC04D", "#FFA526", "#F7931A",
        "#E68515", "#D27510", "#A6580B", "#8B4A05", "#A6580B",
        "#D27510", "#E68515", "#F7931A", "#FFA526", "#FFC04D",
        "#FFD580",
    ]
    ASCII_SHADOW = "#3a1500"

    def refresh_panel(self):
        ts = datetime.now().strftime("%H:%M:%S")
        # Wave offset incrementa ogni tick (4Hz → onda travella ~1 cell ogni 0.25s)
        self._wave_offset = (self._wave_offset + 1) % len(self.ASCII_WAVE_PALETTE)
        # Rotate tip ogni 8s (= 32 tick a 4Hz)
        self._tip_counter += 1
        if self._tip_counter >= 32:
            self._tip_counter = 0
            self._tip_idx = (self._tip_idx + 1) % len(self.EDUCATIONAL_TIPS)
        tip = self.EDUCATIONAL_TIPS[self._tip_idx]
        s = self.state
        if s is None or not s.reachable:
            status_dot = "[metric-crit]●[/]"
            status_label = "[metric-crit]OFFLINE[/]"
            hashrate = "—"
            temp = "—"
            power = "—"
            shares = "—"
            uptime = "—"
            hostname = "—"
        else:
            status_dot = "[metric-good blink]●[/]"
            status_label = "[metric-good]LIVE[/]"
            hashrate = f"[bold #F7931A]{s.hashrate_ghs/1000:.2f} TH/s[/]"
            temp_class = "metric-good" if s.temp_asic < 65 else "metric-warn" if s.temp_asic < 70 else "metric-crit"
            temp = f"[{temp_class}]{s.temp_asic:.0f}°C[/]"
            power = f"[#00D9FF]{s.power_w:.1f}W[/]"
            shares = f"[#FFD700]{s.shares_accepted}[/]"
            uptime = fmt_uptime(s.uptime_sec)
            hostname = s.hostname or "—"

        # ASCII title con effetto ONDA travelling — color per char position (sess.2214)
        palette = self.ASCII_WAVE_PALETTE
        plen = len(palette)
        ascii_lines = []
        for row_idx, line in enumerate(self.ASCII_TITLE_LINES):
            parts: list[str] = []
            cur_color = None
            cur_buf = ""
            for col_idx, ch in enumerate(line):
                if ch == " ":
                    # flush + space neutro
                    if cur_buf:
                        parts.append(f"[bold {cur_color}]{cur_buf}[/]")
                        cur_buf = ""
                        cur_color = None
                    parts.append(" ")
                    continue
                # offset per char + row shift (onda diagonale)
                color_idx = (col_idx + self._wave_offset + row_idx * 2) % plen
                ch_color = palette[color_idx]
                if ch_color == cur_color:
                    cur_buf += ch
                else:
                    if cur_buf:
                        parts.append(f"[bold {cur_color}]{cur_buf}[/]")
                    cur_buf = ch
                    cur_color = ch_color
            if cur_buf:
                parts.append(f"[bold {cur_color}]{cur_buf}[/]")
            ascii_lines.append("".join(parts))
        ascii_block = "\n".join(ascii_lines)

        # Hero v2 sess.2214 — mini sparkline hashrate inline
        mini_spark = sparkline(self._hashrate_history, width=10) if self._hashrate_history else ""
        # Uptime milestone badge — pietra miliare visivo
        def _uptime_badge(secs: int) -> str:
            if secs >= 30 * 86400: return "  [bold #FFD700]🏆 30g+[/]"
            if secs >= 7 * 86400: return "  [bold #FFB000]🥇 7g+[/]"
            if secs >= 86400: return "  [bold #F7931A]🥈 24h+[/]"
            if secs >= 3600: return "  [bold #D27510]🥉 1h+[/]"
            return ""
        uptime_badge = _uptime_badge(s.uptime_sec) if (s and s.reachable) else ""
        # Block height live (mempool.space tip)
        block_str = ""
        if self._block_height > 0:
            block_str = f"   [#666666]•[/]   [dim #FFB000]⛏ blocco #{self._block_height:,}[/]"

        # Subtitle — separatori + block height + ts
        subtitle = (
            f"[bold #FFD700]◆ COCKPIT ◆[/]   [#FFB000]Monitor Live · Bitcoin Solo Miner[/]   "
            f"[#888888]{hostname}  ·  {self.host}[/]   "
            f"[bold #F7931A]⏱ {ts}[/]"
            f"{block_str}"
        )
        # KPI live — separatori dot bullet + spacing ariosa + mini sparkline inline
        kpi_line = (
            f"{status_dot} {status_label}   [#666666]•[/]   "
            f"[#FFA526]⚡[/] {hashrate} [#A6580B]{mini_spark}[/]   [#666666]•[/]   "
            f"[#FF6666]🌡[/] {temp}   [#666666]•[/]   "
            f"[#00D9FF]🔋[/] {power}   [#666666]•[/]   "
            f"[#FFD700]✓[/] {shares} share   [#666666]•[/]   "
            f"[#4DABF7]⏱[/] {uptime}{uptime_badge}"
        )
        # Tip educativo — Bitcoin gold + bullet
        tip_line = f"[#666666]→[/]  [italic #FFD700]{tip}[/]"
        self.update(f"{ascii_block}\n{subtitle}\n{kpi_line}\n{tip_line}")


class AlertsBar(Static):
    """⚠ Threshold alerts flash bar"""
    state: reactive[Optional[BitaxeState]] = reactive(None)

    def watch_state(self, s):
        if s is None:
            self.update("")
            return
        alerts = []
        cls = "safe"
        if s.temp_asic > 70:
            alerts.append(f"TEMP ASIC CRITICA {s.temp_asic:.1f}°C")
            cls = "critical"
        elif s.temp_asic > 65:
            alerts.append(f"TEMP ASIC ALTA {s.temp_asic:.1f}°C")
            cls = "warning"
        if s.temp_vrm > 80:
            alerts.append(f"TEMP VRM CRITICA {s.temp_vrm:.1f}°C")
            cls = "critical"
        elif s.temp_vrm > 75:
            alerts.append(f"TEMP VRM ALTA {s.temp_vrm:.1f}°C")
            cls = "warning"
        total = s.shares_accepted + s.shares_rejected
        if total > 10:
            reject_perc = s.shares_rejected / total * 100
            if reject_perc > 2:
                alerts.append(f"TASSO RIFIUTO {reject_perc:.1f}%")
                cls = "warning" if cls == "safe" else cls
        if s.overheat_mode:
            alerts.append("MODALITÀ SURRISCALDAMENTO ATTIVA")
            cls = "critical"
        if not s.reachable:
            alerts.append("BITAXE NON RAGGIUNGIBILE")
            cls = "critical"
        # Update CSS classes
        for c in ["safe", "warning", "critical"]:
            self.remove_class(c)
        self.add_class(cls)
        if alerts:
            self.update("  ⚠  " + "  ·  ".join(alerts))
        else:
            self.update("  ✓  Tutti i sistemi nominali · hashing regolare · nessun alert")


# ──────────────────────────────────────────────────────────────────────────────
# Main App
# ──────────────────────────────────────────────────────────────────────────────

class HelpModal(ModalScreen):
    """📘 Guida completa cockpit — premi ? o h per aprire"""

    BINDINGS = [
        Binding("escape,q,h,question_mark", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold #F7931A]╔══════════════════════════════════════════════════════════════════╗[/]\n"
            "[bold #F7931A]║[/]   [bold #FFB000]BITAXE COCKPIT — GUIDA COMPLETA[/]                              [bold #F7931A]║[/]\n"
            "[bold #F7931A]╚══════════════════════════════════════════════════════════════════╝[/]\n\n"
            "[bold #FFB000]⌨️  TASTI[/]\n\n"
            "  [bold #F7931A]r[/]            Aggiorna ora\n"
            "  [bold #F7931A]p[/]            Pausa / riprendi auto-refresh\n"
            "  [bold #F7931A]space[/]        Refresh single-step (in pausa)\n"
            "  [bold #F7931A]t[/]            Cicla tema (Polpo → Bitcoin → Mono → Hacker)\n"
            "  [bold #F7931A]s[/]            Salva screenshot SVG\n"
            "  [bold #F7931A]e[/]            Mostra path CSV history\n"
            "  [bold #F7931A]+ / -[/]        Veloce / lento intervallo polling (1-30s)\n"
            "  [bold #F7931A]o[/]            Apri dashboard web AxeOS nel browser\n"
            "  [bold #F7931A]? / h[/]        Apri / chiudi questa guida\n"
            "  [bold #F7931A]q / Ctrl+C[/]   Esci dal cockpit\n\n"
            "[bold #FFB000]📊 PANNELLI[/]\n\n"
            "  [bold #F7931A]⚡ HASHRATE[/]   Live TH/s · sparkline · efficienza J/TH\n"
            "  [bold #FF4444]🌡 TEMP[/]       Gauge ASIC + VRM · ventola · autofan · margini\n"
            "  [bold #FFD700]⛏ MINING[/]     Share accettati/rifiutati · share/min · best diff\n"
            "  [bold #C77DFF]🎰 LOTTERIA[/]   Probabilità blocco · ETA · stima reward\n"
            "  [bold #00D9FF]🔋 POTENZA[/]    Watt · tensione · margine · costo energia\n"
            "  [bold #00C896]🏊 POOL[/]       Primario/fallback · check tamper wallet · latenza\n"
            "  [bold #4DABF7]📡 SISTEMA[/]    RSSI WiFi · firmware · heap · uptime\n"
            "  [bold]📘 LEGENDA[/]   Riferimento rapido · soglie · tip\n\n"
            "[bold #FFB000]🚨 SOGLIE ALERT[/]\n\n"
            "  ASIC  [metric-good]<65°C[/] sicuro · [metric-warn]65-70[/] warn · [metric-crit]>70[/] critico\n"
            "  VRM   [metric-good]<75°C[/] sicuro · [metric-warn]75-80[/] warn · [metric-crit]>80[/] critico\n"
            "  Rifiuto [metric-good]<1%[/] ottimo · [metric-warn]1-2%[/] ok · [metric-crit]>2%[/] degradato\n"
            "  Latenza [metric-good]<100ms[/] · [metric-warn]100-300[/] · [metric-crit]>300[/] degradata\n\n"
            "[bold #FFB000]🪙 NOTA SOLO MINING[/]\n\n"
            "  Solo mining = payout a lotteria. Il reward del blocco (~3.125 BTC)\n"
            "  va al tuo wallet se vinci. Tieni il miner acceso 24/7 per massimizzare\n"
            "  la copertura dello spazio di ricerca SHA-256.\n\n"
            "[dim]Premi [bold]Esc[/] o [bold]?[/] o [bold]q[/] per chiudere.[/]",
            id="help-content",
        )


class BitaxeCockpit(App):
    """Bitaxe Polpo OS — Live TUI Cockpit"""

    CSS_PATH = str(Path(__file__).parent / "bitaxe_cockpit.tcss")
    TITLE = "🐙 Bitaxe Polpo OS Cockpit"

    BINDINGS = [
        Binding("r", "refresh_now", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("t", "cycle_theme", "Theme", show=True),
        Binding("p", "toggle_pause", "Pause", show=True),
        Binding("space", "single_step", "Step", show=False),
        Binding("s", "screenshot", "Snap", show=True),
        Binding("e", "export_csv", "CSV", show=True),
        Binding("plus,equals,kp_plus", "faster", "Faster", show=True),
        Binding("minus,kp_minus", "slower", "Slower", show=True),
        Binding("o", "open_browser", "Open URL", show=True),
        Binding("h,question_mark", "help", "Help", show=True),
    ]

    paused: reactive[bool] = reactive(False)
    theme_idx: reactive[int] = reactive(0)
    refresh_interval: reactive[float] = reactive(DEFAULT_REFRESH_SEC)
    last_status: reactive[str] = reactive("avvio...")
    # ── Gamification refresh sess.2214 ──
    manual_refresh_count: reactive[int] = reactive(0)
    streak: reactive[int] = reactive(0)
    best_latency_ms: reactive[float] = reactive(9999.0)
    last_latency_ms: reactive[float] = reactive(0.0)
    # ── Adaptive rate sess.2214 ──
    tick_count: int = 0  # internal counter (non reactive, performance)

    def __init__(self, host: str = DEFAULT_HOST, interval: float = DEFAULT_REFRESH_SEC):
        super().__init__()
        self.host = host
        self.refresh_interval = interval
        self.client = httpx.AsyncClient(timeout=4.0)
        self._timer = None
        # sess.2214 v0.2 — webhook alerts + prev state per delta detection
        self.notifier = WebhookNotifier()
        self._prev_state: Optional[BitaxeState] = None
        self._unreachable_streak: int = 0

    def compose(self) -> ComposeResult:
        # Header live HUD-style (2 righe: branding + KPI primari + tip rotante)
        yield HeaderBar(host=self.host, id="header-bar")

        # Main grid 2x5 (4 row di panel · 8 widget · 1 alerts bar full-width)
        # sess.2214 — VerticalScroll permette scroll quando window < grid height
        with VerticalScroll(id="main-grid"):
            yield HashratePanel(id="hashrate-panel")
            yield ThermalPanel(id="thermal-panel")
            yield MiningProgressPanel(id="mining-panel")
            yield LotteryPanel(id="lottery-panel")
            yield PowerPanel(id="power-panel")
            yield PoolWalletPanel(id="pool-panel")
            yield SystemInfoPanel(id="system-panel")
            yield LegendPanel(id="legend-panel")
            yield AlertsBar(id="alerts-bar")

        # Footer
        yield Static(
            "[#888888]\\[r]aggiorna  \\[t]ema  \\[p]ausa  \\[s]nap  \\[+/-]rate  \\[o]apri  \\[h]?aiuto  \\[q]esci[/]  ·  [#F7931A]avvio...[/]",
            id="footer-bar"
        )

    async def on_mount(self):
        await self.fetch_and_update()
        self._timer = self.set_interval(self.refresh_interval, self.tick)

    async def tick(self):
        if self.paused:
            return
        self.tick_count += 1
        # Adaptive rate sess.2214 — full refresh ogni tick base + selective per panel slow
        # Panel fast (hashrate, thermal, mining, header, alerts): ogni tick
        # Panel slow (lottery 30s, system 60s, pool 10s): condizionale
        await self.fetch_and_update()

    async def fetch_and_update(self):
        state: Optional[BitaxeState] = None
        try:
            t0 = time.perf_counter()
            r = await self.client.get(f"http://{self.host}/api/system/info")
            elapsed_ms = (time.perf_counter() - t0) * 1000
            r.raise_for_status()
            data = r.json()
            state = BitaxeState.from_api(data, elapsed_ms)
            # Track latency for gamification
            self.last_latency_ms = elapsed_ms
            if elapsed_ms < self.best_latency_ms:
                self.best_latency_ms = elapsed_ms
            self.update_all_panels(state)
            self.log_to_csv(state)
            ts = datetime.now().strftime("%H:%M:%S")
            pause_marker = " [PAUSA]" if self.paused else ""
            self.last_status = f"aggiornato {ts} · {elapsed_ms:.0f}ms{pause_marker}"
            self._unreachable_streak = 0
        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
            ts = datetime.now().strftime("%H:%M:%S")
            self.last_status = f"⚠ {ts} {type(e).__name__}"
            state = BitaxeState(reachable=False, last_update=datetime.now())
            self.update_all_panels(state)
            self._unreachable_streak += 1
        # Webhook alerts (sess.2214 v0.2) — fire async post-update
        if self.notifier.is_configured() and state is not None:
            await self._maybe_alert(state, self._prev_state)
        self._prev_state = state
        self.update_footer()

    async def _maybe_alert(self, state: BitaxeState, prev: Optional[BitaxeState]):
        """Threshold-based alert firing. Cooldown per event in WebhookNotifier."""
        hn = state.hostname or self.host
        # Reachability — fire only after 3 consecutive failures (avoid blips)
        if not state.reachable and self._unreachable_streak == 3:
            await self.notifier.fire(
                "unreachable", "Bitaxe non raggiungibile",
                f"API {self.host} non risponde da 3 poll consecutivi.",
                severity="crit", cooldown=600,
            )
            return  # don't fire other alerts on offline state
        if not state.reachable:
            return
        # ASIC critical
        if state.temp_asic > 70:
            await self.notifier.fire(
                "asic_temp_crit", "ASIC sopra soglia critica",
                f"{hn} · ASIC {state.temp_asic:.1f}°C (throttle imminente sopra 70°C).",
                severity="crit", cooldown=600,
            )
        # VRM critical
        if state.temp_vrm > 80:
            await self.notifier.fire(
                "vrm_temp_crit", "VRM sopra soglia critica",
                f"{hn} · VRM {state.temp_vrm:.1f}°C — il VRM è il vero collo di bottiglia.",
                severity="crit", cooldown=600,
            )
        # Overheat mode firmware
        if state.overheat_mode:
            await self.notifier.fire(
                "overheat_mode", "Modalità surriscaldamento attiva",
                f"{hn} ha attivato il throttle termico. Verifica raffreddamento.",
                severity="crit", cooldown=900,
            )
        # New lifetime best diff
        if prev and prev.best_diff and state.best_diff != prev.best_diff:
            await self.notifier.fire(
                "best_diff_break", "🎰 Nuovo Best Diff lifetime!",
                f"{hn} · {prev.best_diff} → {state.best_diff}. Più vicino al blocco.",
                severity="info", cooldown=60,
            )
        # Uptime milestones (1h, 24h, 7d, 30d)
        if prev:
            milestones = [(3600, "1 ora"), (86400, "24 ore"), (7 * 86400, "7 giorni"), (30 * 86400, "30 giorni")]
            for sec, label in milestones:
                if prev.uptime_sec < sec <= state.uptime_sec:
                    await self.notifier.fire(
                        f"uptime_milestone_{sec}", f"🏆 Uptime milestone — {label}",
                        f"{hn} ha raggiunto {label} di uptime continuo.",
                        severity="info", cooldown=60,
                    )

    def update_all_panels(self, state: BitaxeState, full: bool = True):
        # Adaptive rate sess.2214:
        # - full=True: aggiorna tutti i panel (manual refresh + ogni N tick)
        # - full=False: aggiorna solo i panel FAST (header, hashrate, thermal, mining, alerts)
        # Panel SLOW (lottery, pool, system, legend) → solo ogni 6 tick (≈30s a 5s interval)
        fast_panels = ["header-bar", "hashrate-panel", "thermal-panel", "mining-panel", "alerts-bar"]
        slow_panels = ["lottery-panel", "power-panel", "pool-panel", "system-panel", "legend-panel"]
        targets = fast_panels + slow_panels if full else fast_panels
        for panel_id in targets:
            try:
                panel = self.query_one(f"#{panel_id}")
                panel.state = state
            except Exception:
                pass

    def update_footer(self):
        try:
            footer = self.query_one("#footer-bar")
            theme_name = THEMES[self.theme_idx]
            # Gamification stats
            best_str = f"{self.best_latency_ms:.0f}ms" if self.best_latency_ms < 9999 else "—"
            streak_color = "#FFD700" if self.streak >= 5 else "#F7931A" if self.streak >= 3 else "#888888"
            streak_icon = "⚡" if self.streak >= 5 else "✦" if self.streak >= 3 else "·"
            footer.update(
                f"[#888888]\\[r]aggiorna  \\[t]ema  \\[p]ausa  \\[s]nap  \\[+/-]rate  \\[o]apri  \\[h]?aiuto  \\[q]esci[/]  "
                f"·  [#F7931A]{self.last_status}[/]  "
                f"·  [dim]tema:{theme_name} · poll:{self.refresh_interval:.1f}s[/]  "
                f"·  [#888888]🔄[/] [#F7931A]{self.manual_refresh_count}[/] "
                f"[{streak_color}]{streak_icon} streak {self.streak}[/]  "
                f"[dim]· best [#00C896]{best_str}[/][/]"
            )
        except Exception:
            pass

    def log_to_csv(self, state: BitaxeState):
        """Append snapshot to history CSV"""
        try:
            new_file = not CSV_LOG_PATH.exists()
            with open(CSV_LOG_PATH, "a") as f:
                writer = csv.writer(f)
                if new_file:
                    writer.writerow([
                        "timestamp", "hashrate_ghs", "expected_ghs", "temp_asic",
                        "temp_vrm", "fan_perc", "power_w", "voltage_v", "frequency_mhz",
                        "core_voltage_mv", "shares_accepted", "shares_rejected",
                        "best_diff", "uptime_sec"
                    ])
                writer.writerow([
                    state.last_update.isoformat() if state.last_update else "",
                    f"{state.hashrate_ghs:.2f}",
                    f"{state.expected_ghs:.0f}",
                    f"{state.temp_asic:.1f}",
                    f"{state.temp_vrm:.1f}",
                    state.fan_perc,
                    f"{state.power_w:.2f}",
                    f"{state.voltage_v:.3f}",
                    state.frequency_mhz,
                    state.core_voltage_mv,
                    state.shares_accepted,
                    state.shares_rejected,
                    state.best_diff,
                    state.uptime_sec,
                ])
        except Exception:
            pass

    # ── Actions ──────────────────────────────────────────────────

    async def action_refresh_now(self):
        """Gamification refresh sess.2214 — counter + streak + latency best + flash visivo + easter egg."""
        self.manual_refresh_count += 1
        # Flash visivo footer
        try:
            footer = self.query_one("#footer-bar")
            footer.add_class("flash-refresh")
            self.set_timer(0.4, lambda: footer.remove_class("flash-refresh"))
        except Exception:
            pass
        # Pre-fetch latency snapshot per confronto streak
        prev_best = self.best_latency_ms
        # Notifica iniziale variabile (anti-monotonia)
        teasers = [
            "🔄 Polling Bitaxe...",
            "⚡ Aggiornamento manuale...",
            "🐙 Stratum check live...",
            "🎯 Refresh on demand...",
            "📡 Fetching API...",
        ]
        teaser = teasers[self.manual_refresh_count % len(teasers)]
        self.notify(teaser, title="Refresh", severity="information", timeout=1.2)
        await self.fetch_and_update()
        # Streak logic: sotto 60ms = streak +1, sopra = reset
        if self.last_latency_ms < 60:
            self.streak += 1
        else:
            self.streak = 0
        # Easter egg sequence
        easter_msg = None
        if self.manual_refresh_count == 21:
            easter_msg = "🐙 +1 Sigillo Polpo acquisito — 21 refresh manuali"
        elif self.manual_refresh_count == 100:
            easter_msg = "🏆 100 refresh — sei un Sentinel del Bitaxe"
        elif self.manual_refresh_count == 333:
            easter_msg = "🌌 333 refresh — passaggio frattale completo"
        elif self.streak == 10:
            easter_msg = "⚡ STREAK x10 — silicio in flow state"
        elif self.streak == 25:
            easter_msg = "🔥 STREAK x25 — stratum è seta"
        # Post notifica risultato
        improved = self.last_latency_ms < prev_best if prev_best < 9999 else True
        if easter_msg:
            self.notify(easter_msg, title="🎖️ Achievement", severity="information", timeout=4)
        elif improved and self.last_latency_ms < 60:
            self.notify(
                f"✓ Aggiornato · {self.last_latency_ms:.0f}ms · NEW BEST · streak {self.streak}",
                title="Refresh OK ⚡", severity="information", timeout=2
            )
        else:
            streak_tag = f" · streak {self.streak}" if self.streak > 0 else ""
            self.notify(
                f"✓ Aggiornato · {self.last_latency_ms:.0f}ms{streak_tag}",
                title="Refresh OK", severity="information", timeout=1.2
            )

    def action_quit(self):
        self.notify("⏏ Chiusura cockpit. A presto.", title="Esci", severity="warning", timeout=1.5)
        self.exit()

    def action_cycle_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)
        new_theme = THEMES[self.theme_idx]
        for t in THEMES:
            self.screen.remove_class(f"theme-{t}")
        if new_theme != "polpo":
            self.screen.add_class(f"theme-{new_theme}")
        emojis = {"polpo": "🐙", "bitcoin": "₿", "mono": "◐", "hacker": "👾"}
        self.notify(f"{emojis[new_theme]} Tema: {new_theme.upper()}", title="Tema", severity="information", timeout=2)
        self.update_footer()

    def action_toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.notify("⏸ Auto-refresh in PAUSA · premi 'p' per riprendere · 'space' per single step", title="Pausa", severity="warning", timeout=3)
        else:
            self.notify("▶ Auto-refresh RIPRESO", title="Ripreso", severity="information", timeout=2)
        self.update_footer()

    async def action_single_step(self):
        if self.paused:
            self.notify("⏯ Refresh single-step...", title="Step", severity="information", timeout=1.5)
            await self.fetch_and_update()
            self.notify("✓ Step completato", title="Step OK", severity="information", timeout=1)
        else:
            self.notify("⚠ Single step funziona solo in pausa (premi 'p' prima)", title="Step", severity="warning", timeout=2)

    def action_screenshot(self):
        """Salva screenshot SVG della TUI attuale"""
        path = DATA_DIR / "snapshots" / f"bitaxe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.save_screenshot(str(path))
            self.notify(f"📸 Screenshot SVG salvato: {path.name}", title="Screenshot", severity="information", timeout=3)
            self.last_status = f"📸 salvato {path.name}"
        except Exception as e:
            self.notify(f"❌ Screenshot fallito: {e}", title="Errore screenshot", severity="error", timeout=3)
        self.update_footer()

    def action_export_csv(self):
        self.notify(f"📁 Path CSV history: {CSV_LOG_PATH}\n(auto-loggato ad ogni poll)", title="Export CSV", severity="information", timeout=4)
        self.last_status = f"📁 CSV: {CSV_LOG_PATH}"
        self.update_footer()

    def action_faster(self):
        steps = [1.0, 2.0, 5.0, 10.0, 30.0]
        cur = min(steps, key=lambda x: abs(x - self.refresh_interval))
        idx = steps.index(cur)
        if idx > 0:
            self.refresh_interval = steps[idx - 1]
            if self._timer:
                self._timer.stop()
            self._timer = self.set_interval(self.refresh_interval, self.tick)
            self.notify(f"⏩ Intervallo poll → {self.refresh_interval:.0f}s", title="Più veloce", severity="information", timeout=2)
            self.update_footer()
        else:
            self.notify("⚠ Già al minimo (1s) — impossibile accelerare", title="Limite velocità", severity="warning", timeout=2)

    def action_slower(self):
        steps = [1.0, 2.0, 5.0, 10.0, 30.0]
        cur = min(steps, key=lambda x: abs(x - self.refresh_interval))
        idx = steps.index(cur)
        if idx < len(steps) - 1:
            self.refresh_interval = steps[idx + 1]
            if self._timer:
                self._timer.stop()
            self._timer = self.set_interval(self.refresh_interval, self.tick)
            self.notify(f"⏪ Intervallo poll → {self.refresh_interval:.0f}s", title="Più lento", severity="information", timeout=2)
            self.update_footer()
        else:
            self.notify("⚠ Già al massimo (30s) — impossibile rallentare", title="Limite velocità", severity="warning", timeout=2)

    def action_open_browser(self):
        webbrowser.open(f"http://{self.host}")
        self.notify(f"🌐 Apertura http://{self.host}", title="Browser", severity="information", timeout=2)
        self.last_status = f"🌐 aperto http://{self.host}"
        self.update_footer()

    def action_help(self):
        self.notify("📘 Guida aperta · Esc o ? per chiudere", title="Guida", severity="information", timeout=2)
        self.push_screen(HelpModal())

    async def on_unmount(self):
        await self.client.aclose()
        await self.notifier.close()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

async def discover_bitaxe(timeout: float = 3.0) -> list[tuple[str, str, int]]:
    """Scan LAN via mDNS for Bitaxe miners exposing `_http._tcp.local.`.

    Returns list of (hostname, ip, port). Empty if no devices found.
    Requires `zeroconf` package — graceful fallback if missing.
    """
    try:
        from zeroconf import IPVersion
        from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf
    except ImportError:
        print("[bitaxe-cockpit] mDNS discovery requires `zeroconf`. Install with: pip install zeroconf", flush=True)
        return []

    found: list[tuple[str, str, int]] = []
    seen_names: set[str] = set()

    aiozc = AsyncZeroconf(ip_version=IPVersion.V4Only)

    async def _resolve(zc, type_, name):
        if name in seen_names:
            return
        seen_names.add(name)
        info = AsyncServiceInfo(type_, name)
        await info.async_request(zc, 1500)
        if not info.addresses:
            return
        # Filter: bitaxe / axe / esp32-* in service name → likely a miner
        lname = name.lower()
        if not any(k in lname for k in ("bitaxe", "axe", "esp32")):
            return
        ip = ".".join(str(b) for b in info.addresses[0])
        hostname = info.server.rstrip(".") if info.server else name
        found.append((hostname, ip, info.port or 80))

    def _handler(zeroconf, service_type, name, state_change):
        if state_change.name == "Added":
            asyncio.ensure_future(_resolve(zeroconf, service_type, name))

    browser = AsyncServiceBrowser(
        aiozc.zeroconf,
        "_http._tcp.local.",
        handlers=[_handler],
    )
    try:
        await asyncio.sleep(timeout)
    finally:
        await browser.async_cancel()
        await aiozc.async_close()
    return found


def _select_host_interactive() -> str:
    """Run mDNS scan + show interactive selection. Returns chosen host."""
    print("🔍 Scansione mDNS in corso (3s)...", flush=True)
    found = asyncio.run(discover_bitaxe(timeout=3.0))
    if not found:
        print("⚠ Nessun Bitaxe trovato via mDNS. Uso default:", DEFAULT_HOST, flush=True)
        return DEFAULT_HOST
    if len(found) == 1:
        hn, ip, port = found[0]
        print(f"✓ Trovato 1 miner: {hn} → {ip}:{port}", flush=True)
        return ip
    print(f"✓ Trovati {len(found)} miner:", flush=True)
    for i, (hn, ip, port) in enumerate(found, 1):
        print(f"  [{i}] {hn} → {ip}:{port}", flush=True)
    try:
        choice = input("Scegli numero (default 1): ").strip() or "1"
        idx = int(choice) - 1
        return found[idx][1]
    except (ValueError, IndexError, EOFError, KeyboardInterrupt):
        return found[0][1]


def main():
    parser = argparse.ArgumentParser(description="Bitaxe Cockpit — live TUI for solo Bitcoin miners")
    parser.add_argument("--host", default=None, help="Bitaxe IP or hostname (env BITAXE_HOST or auto-discover if unset)")
    parser.add_argument("--interval", type=float, default=DEFAULT_REFRESH_SEC, help="Refresh interval seconds (env BITAXE_REFRESH_SEC)")
    parser.add_argument("--discover", action="store_true", help="Force mDNS auto-discovery + interactive selection (ignore --host)")
    parser.add_argument("--list", action="store_true", help="Scan LAN via mDNS and list found miners (no TUI)")
    args = parser.parse_args()

    if args.list:
        found = asyncio.run(discover_bitaxe(timeout=3.0))
        if not found:
            print("Nessun miner trovato.")
            return
        for hn, ip, port in found:
            print(f"{hn}\t{ip}\t{port}")
        return

    if args.discover or args.host is None:
        # Auto-discover when --discover OR --host not specified and env BITAXE_HOST not set
        if args.discover or os.environ.get("BITAXE_HOST") is None:
            host = _select_host_interactive()
        else:
            host = DEFAULT_HOST
    else:
        host = args.host

    app = BitaxeCockpit(host=host, interval=args.interval)
    app.run()


if __name__ == "__main__":
    main()
