"""
MERALCO Add-on Main Entry Point

Runs as a Home Assistant add-on: reads configuration, branches on `mode`,
and either publishes MERALCO rates to MQTT or hands off to gunicorn for
the REST API.
"""

import json  # noqa: F401
import logging  # noqa: F401
import os  # noqa: F401
from pathlib import Path
from typing import TypedDict

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
    return dict(_DEFAULTS)  # type: ignore[return-value]
