"""
Shared Flask-Limiter instance.
Imported by routes to apply per-route limits and by app.py to bind it to the app.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],          # No blanket limit; each route sets its own.
    storage_uri="memory://",    # In-process memory — swap for Redis in production.
)
