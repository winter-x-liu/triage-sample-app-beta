"""User Admin screen: staff accounts and their roles."""

from fastapi import APIRouter, Request

from app import db
from app.permissions import current_user, require_screen
from app.templating import templates

router = APIRouter()


@router.get("/users")
def users(request: Request):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "User Admin")
        rows = db.query(
            conn,
            "SELECT u.user_id, u.role, u.active, u.created_at, r.screens FROM users u"
            " JOIN roles r ON r.role = u.role ORDER BY u.user_id",
        )
        return templates.TemplateResponse(request, "users.html", {"user": user, "rows": rows})
