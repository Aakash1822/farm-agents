from typing import Any

async def track_event(event_name: str, properties: dict[str, Any]) -> None:
    """No-op analytics event tracker."""
    # This is intentionally minimal. Add real analytics integration later.
    return
