"""Smoke tests for bitaxe_cockpit."""
import bitaxe_cockpit as bc


def test_module_imports():
    """Core module loads without side effects."""
    assert hasattr(bc, "BitaxeCockpit")
    assert hasattr(bc, "BitaxeState")
    assert hasattr(bc, "soft_wrap")


def test_soft_wrap_preserves_markup():
    """soft_wrap must keep [tag]...[/] balanced."""
    s = "[dim]💡 [italic]hello world this is a long string that should wrap at width 20[/][/]"
    wrapped = bc.soft_wrap(s, width=20)
    # Count opening vs closing tags
    assert wrapped.count("[dim]") == 1
    assert wrapped.count("[italic]") == 1
    assert wrapped.count("[/]") == 2
    # Should have produced at least 2 lines
    assert "\n" in wrapped


def test_soft_wrap_short_string_unchanged():
    """Short strings stay single line."""
    s = "[dim]hi[/]"
    assert bc.soft_wrap(s, width=80) == s


def test_themes_present():
    """All 4 themes registered."""
    assert "polpo" in bc.THEMES
    assert "bitcoin" in bc.THEMES
    assert "mono" in bc.THEMES
    assert "hacker" in bc.THEMES


def test_default_host_env(monkeypatch):
    """BITAXE_HOST env var honored."""
    monkeypatch.setenv("BITAXE_HOST", "192.168.99.99")
    # Need to reload the module to pick up env change
    import importlib
    importlib.reload(bc)
    assert bc.DEFAULT_HOST == "192.168.99.99"


def test_wallet_prefix_empty_by_default(monkeypatch):
    """WALLET_PREFIX defaults to empty (no hardcoded personal data)."""
    monkeypatch.delenv("BITAXE_WALLET_PREFIX", raising=False)
    import importlib
    importlib.reload(bc)
    assert bc.WALLET_PREFIX == ""


def test_bitaxe_state_from_api():
    """BitaxeState.from_api parses canonical AxeOS payload."""
    sample = {
        "hashRate": 1100.5,
        "expectedHashrate": 1071,
        "temp": 62.5,
        "vrTemp": 70.0,
        "fanspeed": 100,
        "fanrpm": 5850,
        "power": 17.9,
        "voltage": 4968.75,
        "current": 11234.375,
        "frequency": 525,
        "coreVoltage": 1150,
        "sharesAccepted": 100,
        "sharesRejected": 0,
        "bestDiff": "1.38 G",
        "stratumURL": "solo.homeminingitalia.org",
        "stratumPort": 3333,
        "stratumUser": "bc1qexample.worker",
        "hostname": "test-miner",
        "macAddr": "AA:BB:CC:DD:EE:FF",
        "ssid": "TestNet",
        "wifiRSSI": -50,
        "uptimeSeconds": 3600,
        "axeOSVersion": "v2.10.0",
        "ASICModel": "BM1370",
        "boardVersion": "601",
    }
    state = bc.BitaxeState.from_api(sample, 42.0)
    assert state.hashrate_ghs == 1100.5
    assert state.temp_asic == 62.5
    assert state.temp_vrm == 70.0
    assert state.stratum_user == "bc1qexample.worker"
    assert state.response_time_ms == 42.0
    assert state.reachable is True
