"""Tests for the add-on configuration loader."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def clean_env() -> Iterator[None]:
    """Strip add-on env vars so each test starts from a known state."""
    keys = [
        "MODE",
        "LOG_LEVEL",
        "SCAN_INTERVAL",
        "KWH_LEVELS",
        "MQTT_TOPIC_PREFIX",
        "MQTT_DISCOVERY_PREFIX",
        "MQTT_HOST",
        "MQTT_PORT",
        "MQTT_USERNAME",
        "MQTT_PASSWORD",
        "SUPERVISOR_TOKEN",
    ]
    saved = {k: os.environ.pop(k, None) for k in keys}
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_read_addon_config_returns_documented_defaults(
    clean_env: None, tmp_path: Path
) -> None:
    """When no options.json and no env vars, returns documented defaults."""
    from src.addon_main import read_addon_config

    config = read_addon_config(options_path=tmp_path / "missing.json")

    assert config["mode"] == "mqtt"
    assert config["log_level"] == "info"
    assert config["scan_interval"] == 86400
    assert config["kwh_levels"] == [200]
    assert config["mqtt_topic_prefix"] == "meralco"
    assert config["mqtt_discovery_prefix"] == "homeassistant"
