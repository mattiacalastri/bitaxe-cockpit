"""
polpo_arc_gauge — shim re-export from polpo-tui-toolkit (sess.2622 dogfooding)

This module is a backward-compat shim. The canonical ArcGauge primitive now lives in
`polpo-tui-toolkit` sibling library: https://github.com/mattiacalastri/polpo-tui-toolkit

Import strategy: sibling path resolution if available, fallback to error.
Future migration: replace with `pip install polpo-tui-toolkit` then
`from polpo_tui_toolkit import ArcGauge`.

Cluster madre cicatrice: feedback_two_file_divergence_scripts_vs_repo_sess2622
(25° substrato sintattico ≠ funzionale — DRY tramite library extraction).
"""

import os
import sys

# Sibling resolution: cerca polpo-tui-toolkit nei path standard
_TOOLKIT_PATHS = [
    os.path.expanduser("~/projects/polpo-tui-toolkit"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "polpo-tui-toolkit"),
]
for _path in _TOOLKIT_PATHS:
    if os.path.isdir(_path) and _path not in sys.path:
        sys.path.insert(0, _path)
        break

try:
    from polpo_tui_toolkit import (
        ArcGauge,
        BrailleCanvas,
        PALETTE_POLPO,
        PALETTE_BITCOIN,
        PALETTE_HACKER,
        PALETTE_MONO,
    )
    _LIBRARY_MODE = "sibling"
except ImportError as _exc:
    raise ImportError(
        f"polpo-tui-toolkit non trovato ({_exc}). Install via:\n"
        f"  git clone https://github.com/mattiacalastri/polpo-tui-toolkit "
        f"~/projects/polpo-tui-toolkit\n"
        f"  oppure pip install polpo-tui-toolkit"
    ) from _exc


__all__ = [
    "ArcGauge",
    "BrailleCanvas",
    "PALETTE_POLPO",
    "PALETTE_BITCOIN",
    "PALETTE_HACKER",
    "PALETTE_MONO",
]


def _demo():
    """Demo standalone — invocato con `python3 polpo_arc_gauge.py`"""
    try:
        from rich.console import Console
        from rich.columns import Columns
        from rich.panel import Panel
    except ImportError:
        print("Install rich per demo: pip install rich")
        return
    console = Console()
    console.print(f"[bold #F7931A]🐙 polpo_arc_gauge shim · backend: {_LIBRARY_MODE}[/]")
    gauges = [
        ArcGauge(value=50, min_val=0, max_val=100, label="DEMO 1",
                 unit="%", width_px=40, height_px=18),
        ArcGauge(value=75, min_val=0, max_val=100, label="DEMO 2",
                 unit="%", width_px=40, height_px=18, palette=dict(PALETTE_BITCOIN)),
    ]
    panels = [Panel(g.render(), border_style="dim", padding=(0, 1)) for g in gauges]
    console.print(Columns(panels, expand=False))


if __name__ == "__main__":
    _demo()
