"""Request ids, one JSON log line per request, and unhandled exceptions written to error_log."""

import json
import logging
import sys
import time
import traceback
import uuid
from datetime import UTC, datetime

from starlette.middleware.base import BaseHTTPMiddleware

from app import db

logger = logging.getLogger("ei")
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_handler)
logger.setLevel(logging.INFO)


def log_event(level, request_id, user_id, method, route, status, duration_ms, message, **extra):
    record = {
        "ts": datetime.now(UTC).isoformat(),
        "level": level,
        "request_id": request_id,
        "user_id": user_id,
        "method": method,
        "route": route,
        "status": status,
        "duration_ms": duration_ms,
        "message": message,
        **extra,
    }
    logger.info(json.dumps(record))


def record_error(request_id, user_id, page, exc):
    """Write the exception to error_log so support can find it by request id."""
    with db.connect() as conn:
        next_id = db.query_one(conn, "SELECT COALESCE(MAX(error_id), 0) + 1 AS n FROM error_log")["n"]
        conn.execute(
            "INSERT INTO error_log (error_id, logged_at, request_id, user_id, page, exception_type,"
            " message, stack_trace) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (next_id, datetime.now(), request_id, user_id, page, type(exc).__name__, str(exc),
             "".join(traceback.format_exception(exc))),
        )
        conn.commit()


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        user_id = request.headers.get("X-User-Id")
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - started) * 1000)
            log_event("ERROR", request_id, user_id, request.method, request.url.path, 500,
                      duration_ms, str(exc), exception_type=type(exc).__name__)
            record_error(request_id, user_id, request.url.path, exc)
            raise
        duration_ms = round((time.perf_counter() - started) * 1000)
        log_event("INFO", request_id, user_id, request.method, request.url.path,
                  response.status_code, duration_ms, "ok")
        response.headers["X-Request-Id"] = request_id
        return response
