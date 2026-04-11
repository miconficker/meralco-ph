"""
MERALCO Add-on Main Entry Point

Runs as a Home Assistant add-on: reads configuration, branches on `mode`,
and either publishes MERALCO rates to MQTT or hands off to gunicorn for
the REST API.
"""

import json
import logging
import os  # noqa: F401
from pathlib import Path
from typing import TypedDict, cast

logger = logging.getLogger(__name__)

DEFAULT_OPTIONS_PATH = Path("/data/options.json")


class AddonConfig(TypedDict):
    mode: str
    log_level: str
    scan_interval: int
    kwh_levels: list[int]
    mqtt_topic_prefix: str
    mqtt_discovery_prefix: str


_DEFAULTS: AddonConfig = {
    "mode": "mqtt",
    "log_level": "info",
    "scan_interval": 86400,
    "kwh_levels": [200],
    "mqtt_topic_prefix": "meralco",
    "mqtt_discovery_prefix": "homeassistant",
}


def read_addon_config(options_path: Path = DEFAULT_OPTIONS_PATH) -> AddonConfig:
    """Load add-on options from /data/options.json with env var fallback."""
    config: AddonConfig = cast(AddonConfig, dict(_DEFAULTS))

    if options_path.is_file():
        try:
            options = json.loads(options_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to read add-on options at %s: %s", options_path, exc)
        else:
            for key in _DEFAULTS:
                if key in options:
                    config[key] = options[key]  # type: ignore[literal-required]
            logger.info("Loaded add-on options from %s", options_path)

    return config
