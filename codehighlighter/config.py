"""This module handles the JSON add-on config."""

from typing import Any

import aqt

# A config is a dictionary.
Config = dict[str, Any]


def config() -> Config:
    """Returns the add-on's config.

    Returns:
        The add-on's config.

    Raises:
        RuntimeError: If the Anki main window is not available.
    """
    if not aqt.mw:
        # This should never happen, so should be OK to raise an exception.
        raise RuntimeError("Anki main window is not available.")
    file_config = aqt.mw.addonManager.getConfig(__name__)
    if not file_config:
        return dict()
    return file_config


def get(key: str, default: Any = None) -> Any:
    """Returns the value for the given configuration key.

    Args:
        key: The configuration key to retrieve.
        default: The default value to return if the key is not found
            or the configuration is unavailable.

    Returns:
        The configuration value, or the default value.

    Raises:
        RuntimeError: If the Anki main window is not available.
    """
    config_snapshot = config()
    return config_snapshot.get(key, default)
