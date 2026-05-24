"""Shared pytest fixtures for bitaxe-cockpit tests."""
import json
from pathlib import Path

import pytest


@pytest.fixture
def axeos_system_info():
    """Canonical AxeOS /api/system/info payload (sanitized sample)."""
    fixture_path = Path(__file__).parent / "fixtures" / "api" / "system" / "info.json"
    with open(fixture_path) as f:
        return json.load(f)
