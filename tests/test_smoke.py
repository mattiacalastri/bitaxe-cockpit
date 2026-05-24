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


def test_bitaxe_state_from_api(axeos_system_info):
    """BitaxeState.from_api parses canonical AxeOS payload from fixture."""
    state = bc.BitaxeState.from_api(axeos_system_info, response_ms=42.0)
    assert state.hashrate_ghs == 1148.32
    assert state.expected_ghs == 1071
    assert state.temp_asic == 62.25
    assert state.temp_vrm == 70.0
    assert state.fan_perc == 100
    assert state.power_w == 17.84
    assert state.shares_accepted == 535
    assert state.shares_rejected == 0
    assert state.best_diff == "1.38 G"
    assert state.stratum_user.startswith("bc1q")
    assert state.hostname == "your-miner"
    assert state.asic_model == "BM1370"
    assert state.board_version == "601"
    assert state.uptime_sec == 4164
    assert state.response_time_ms == 42.0
    assert state.reachable is True
    assert state.using_fallback is False
    assert state.autofanspeed == 1


def test_bitaxe_state_unreachable():
    """Default BitaxeState() = unreachable state for offline scenarios."""
    state = bc.BitaxeState(reachable=False)
    assert state.reachable is False
    assert state.hashrate_ghs == 0.0
    assert state.shares_accepted == 0


def test_webhook_notifier_no_op_when_unconfigured(monkeypatch):
    """WebhookNotifier silent when no env vars set."""
    for var in ("BITAXE_TG_TOKEN", "BITAXE_TG_CHAT_ID", "BITAXE_DISCORD_URL", "BITAXE_WEBHOOK_URL"):
        monkeypatch.delenv(var, raising=False)
    n = bc.WebhookNotifier()
    assert n.is_configured() is False
