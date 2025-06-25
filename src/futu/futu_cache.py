class FutuCache:
    """In-memory cache for API responses."""

    def __init__(self):

        self._get_market_snapshot_cache: dict[str, list[dict[str, any]]] = {}

    def _merge_data(self, existing: list[dict] | None, new_data: list[dict], key_field: str) -> list[dict]:
        """Merge existing and new data, avoiding duplicates based on a key field."""
        if not existing:
            return new_data

        # Create a set of existing keys for O(1) lookup
        existing_keys = {item[key_field] for item in existing}

        # Only add items that don't exist yet
        merged = existing.copy()
        merged.extend([item for item in new_data if item[key_field] not in existing_keys])
        return merged

    def get_market_snapshot(self, ticker_list: str) -> list[dict[str, any]]:
        """Get cached market snapshot if available."""
        return self._get_market_snapshot_cache.get(ticker_list)



# Global cache instance
_futuCache = FutuCache()


def get_futu_cache() -> FutuCache:
    """Get the global cache instance."""
    return _futuCache
