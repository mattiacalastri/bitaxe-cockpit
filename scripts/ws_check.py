#!/usr/bin/env python3
"""
Bitaxe WS mining.submit canonical wallet check.

Companion to bitaxe_cockpit — connects to your Bitaxe's WebSocket endpoint
(`ws://<host>/api/ws`) and counts how many `mining.submit` frames go to YOUR
wallet vs known vendor wallets vs unknown.

This is the GROUND TRUTH check that AxeOS's `/api/system/info` REST endpoint
cannot give you, because AxeOS caches `stratumUser` in RAM until you POST
`/api/system/restart` — the API shows the new wallet, the runtime still
streams to the old one.

## Usage

    export BITAXE_HOST=192.168.1.42                  # your Bitaxe IP or hostname
    export BITAXE_WALLET_PREFIX=bc1qxxx              # first ~10 chars of YOUR address
    export BITAXE_VENDOR_WALLET_PREFIX=bc1pl5j75axs  # optional, known vendor pattern
    python ws_check.py

## Output

    [OK ] +  3.2s mining.submit → YOU  (acc count: 1)
    [OK ] +  7.4s mining.submit → YOU  (acc count: 2)
    ...
    === WS CHECK RESULT ===
    Submits → YOU:     19
    Submits → VENDOR:  0
    Submits → unknown: 0
    ✅ PASS — runtime aligned with API config

Exit codes:
  0 — PASS (all shares to you, OR no submits captured at all)
  1 — FAIL (≥1 share to vendor pattern — runtime mismatch with API)
  2 — WS connection error
"""
import asyncio
import os
import re
import sys
import time

try:
    import websockets
except ImportError:
    print("Missing dep: `pip install websockets`", file=sys.stderr)
    sys.exit(3)


HOST = os.environ.get("BITAXE_HOST", "bitaxe.local")
EXPECTED_WALLET_PREFIX = os.environ.get("BITAXE_WALLET_PREFIX", "")
VENDOR_WALLET_PREFIX = os.environ.get("BITAXE_VENDOR_WALLET_PREFIX", "")
DURATION = int(os.environ.get("BITAXE_WS_DURATION", "60"))
WS_URL = f"ws://{HOST}/api/ws"


async def verify():
    if not EXPECTED_WALLET_PREFIX:
        print(
            "ERROR: BITAXE_WALLET_PREFIX env var is required.\n"
            "Set it to the first ~10 chars of your Bitcoin address.\n"
            "Example: export BITAXE_WALLET_PREFIX=bc1qxxx",
            file=sys.stderr,
        )
        return 3

    print(f"[WS] Connect {WS_URL} (duration: {DURATION}s) ...")
    submits_to_you = 0
    submits_to_vendor = 0
    submits_unknown = 0
    other_messages = 0
    start = time.time()
    try:
        async with websockets.connect(WS_URL, open_timeout=5) as ws:
            print(f"[WS] connected, listening for {DURATION}s ...")
            while time.time() - start < DURATION:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5)
                    msg_str = str(msg)
                    if "mining.submit" in msg_str:
                        if EXPECTED_WALLET_PREFIX in msg_str:
                            submits_to_you += 1
                            print(f"[OK ] +{time.time()-start:5.1f}s mining.submit → YOU (acc count: {submits_to_you})")
                        elif VENDOR_WALLET_PREFIX and VENDOR_WALLET_PREFIX in msg_str:
                            submits_to_vendor += 1
                            print(f"[!!!] +{time.time()-start:5.1f}s mining.submit → VENDOR (runtime mismatch with API!)")
                            print(f"      raw: {msg_str[:200]}")
                        else:
                            submits_unknown += 1
                            m = re.search(r'"params":\s*\[\s*"([^"]+)"', msg_str)
                            preview = m.group(1) if m else msg_str[:120]
                            print(f"[?  ] +{time.time()-start:5.1f}s mining.submit → unknown: {preview}")
                    else:
                        other_messages += 1
                except asyncio.TimeoutError:
                    continue
    except Exception as e:
        print(f"[ERR] WS error: {e}", file=sys.stderr)
        return 2

    print("\n=== WS CHECK RESULT ===")
    print(f"Duration:          {DURATION}s")
    print(f"Submits → YOU:     {submits_to_you}")
    print(f"Submits → VENDOR:  {submits_to_vendor}")
    print(f"Submits → unknown: {submits_unknown}")
    print(f"Other WS messages: {other_messages}")
    print()
    if submits_to_vendor > 0:
        print("❌ FAIL — runtime still streaming to vendor wallet AFTER you changed config.")
        print("   AxeOS cached the old stratumUser in RAM. Fix: POST /api/system/restart")
        return 1
    if submits_to_you == 0 and submits_unknown == 0:
        print("⚠️  WARN — no mining.submit frames captured during window.")
        print("   Increase BITAXE_WS_DURATION or verify the miner is hashing.")
        return 0
    if submits_to_you > 0:
        print("✅ PASS — runtime shares confirmed to YOUR wallet.")
        return 0
    print("⚠️  PARTIAL — submits to unknown prefix, no vendor detected. Verify config.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(verify()))
