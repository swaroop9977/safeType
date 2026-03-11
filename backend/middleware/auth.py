"""
API key authentication middleware for SafeType+.

Accepted header formats (in priority order):
  X-API-Key: <key>
  Authorization: Bearer <key>

When API_KEY_ENABLED is False (development default) the decorator is a no-op
so existing local workflows and the evaluation script keep working unchanged.
When enabled, a missing key returns 401 and a wrong key returns 403.
"""

import hmac
import logging
from functools import wraps
from flask import request, jsonify
from config import Config

logger = logging.getLogger(__name__)


def _extract_key_from_request() -> str | None:
    """Return the raw API key string from the incoming request, or None."""
    # Prefer the dedicated header
    key = request.headers.get("X-API-Key", "").strip()
    if key:
        return key

    # Fall back to Authorization: Bearer <key>
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    return None


def require_api_key(f):
    """
    Decorator that enforces API key authentication on a route.

    Usage::

        @bp.route('/scan/text', methods=['POST'])
        @require_api_key
        def scan_text():
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not Config.API_KEY_ENABLED:
            # Auth disabled (development mode) — pass through.
            return f(*args, **kwargs)

        provided_key = _extract_key_from_request()

        if not provided_key:
            logger.warning(
                "Rejected unauthenticated request to %s from %s",
                request.path,
                request.remote_addr,
            )
            return jsonify({
                "error": "API key required",
                "hint": "Provide it via the X-API-Key header or Authorization: Bearer <key>",
            }), 401

        # Constant-time comparison to prevent timing attacks.
        expected_key = Config.API_KEY or ""
        if not hmac.compare_digest(provided_key, expected_key):
            logger.warning(
                "Rejected invalid API key for %s from %s",
                request.path,
                request.remote_addr,
            )
            return jsonify({"error": "Invalid API key"}), 403

        return f(*args, **kwargs)

    return decorated
