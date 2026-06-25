from typing import Any, Dict, Optional


class InMemoryConfig:
    """An in-memory dictionary-backed implementation of the config module for testing."""

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self.data = data or {}

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Returns the value for the given configuration key.

        Args:
            key: The configuration key to retrieve.
            default: The default value to return if the key is not found
                or the configuration is unavailable.

        Returns:
            The configuration value, or the default value.
        """
        return self.data.get(key, default)

    def config(self) -> Dict[str, Any]:
        """Returns the config dictionary."""
        return self.data
