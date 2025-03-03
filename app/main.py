"""Application entry point: middleware, exception pages, and every screen's router."""

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from app.middleware import RequestLogMiddleware
from app.permissions import PermissionDenied
from app.routers import ROUTERS
from app.settings import settings
from app.templating import templates

app = FastAPI(title=f"{settings.state_name} Early Intervention", version=settings.app_version)
app.add_middleware(RequestLogMiddleware)
for router in ROUTERS:
    app.include_router(router)


@app.exception_handler(PermissionDenied)
async def permission_denied(request: Request, exc: PermissionDenied):
    context = {"title": "Access denied", "message": exc.detail, "screen": exc.screen}
    return templates.TemplateResponse(request, "error.html", context, status_code=403)


@app.get("/")
def home():
    return RedirectResponse("/children")
