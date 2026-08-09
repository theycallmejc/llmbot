"""Minimal structured logging without sensitive prompt or key data."""
import json, logging, time
from uuid import uuid4
from fastapi import Request

logger = logging.getLogger("chatbot")
if not logger.handlers:
    handler = logging.StreamHandler(); handler.setFormatter(logging.Formatter("%(message)s")); logger.addHandler(handler); logger.setLevel(logging.INFO)

async def request_log(request: Request, call_next):
    request_id = str(uuid4()); start = time.perf_counter()
    response = await call_next(request); response.headers["X-Request-ID"] = request_id
    logger.info(json.dumps({"event":"request", "request_id":request_id, "method":request.method, "path":request.url.path, "status":response.status_code, "latency_ms":round((time.perf_counter()-start)*1000)}))
    return response
