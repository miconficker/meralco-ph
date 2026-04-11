"""Tests for the add-on configuration loader."""

import json
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


def test_read_addon_config_loads_from_options_file(
    clean_env: None, tmp_path: Path
) -> None:
    """When options.json exists, its values override defaults."""
    from src.addon_main import read_addon_config

    options_file = tmp_path / "options.json"
    options_file.write_text(
        json.dumps(
            {
                "mode": "rest",
                "log_level": "debug",
                "scan_interval": 7200,
                "kwh_levels": [200, 300],
                "mqtt_topic_prefix": "custom_prefix",
                "mqtt_discovery_prefix": "homeassistant_test",
            }
        )
    )

    config = read_addon_config(options_path=options_file)

    assert config["mode"] == "rest"
    assert config["log_level"] == "debug"
    assert config["scan_interval"] == 7200
    assert config["kwh_levels"] == [200, 300]
    assert config["mqtt_topic_prefix"] == "custom_prefix"
    assert config["mqtt_discovery_prefix"] == "homeassistant_test"


def test_read_addon_config_falls_back_to_env_vars(
    clean_env: None, tmp_path: Path
) -> None:
    """Standalone Docker users set env vars; they override defaults."""
    from src.addon_main import read_addon_config

    os.environ["MODE"] = "rest"
    os.environ["LOG_LEVEL"] = "warning"
    os.environ["SCAN_INTERVAL"] = "10800"
    os.environ["KWH_LEVELS"] = "100,200,300"
    os.environ["MQTT_TOPIC_PREFIX"] = "env_prefix"
    os.environ["MQTT_DISCOVERY_PREFIX"] = "env_disco"

    config = read_addon_config(options_path=tmp_path / "missing.json")

    assert config["mode"] == "rest"
    assert config["log_level"] == "warning"
    assert config["scan_interval"] == 10800
    assert config["kwh_levels"] == [100, 200, 300]
    assert config["mqtt_topic_prefix"] == "env_prefix"
    assert config["mqtt_discovery_prefix"] == "env_disco"


def test_options_file_takes_precedence_over_env_vars(
    clean_env: None, tmp_path: Path
) -> None:
    """When both are set, /data/options.json wins (HA add-on path is canonical)."""
    from src.addon_main import read_addon_config

    os.environ["MODE"] = "rest"
    options_file = tmp_path / "options.json"
    options_file.write_text(json.dumps({"mode": "mqtt"}))

    config = read_addon_config(options_path=options_file)

    assert config["mode"] == "mqtt"
