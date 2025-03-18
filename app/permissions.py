"""Screen permissions: a role may open the screens listed in roles.screens."""

from fastapi import HTTPException, Request

from app.db import query_one


class PermissionDenied(HTTPException):
    def __init__(self, user_id: str, screen: str) -> None:
        super().__init__(status_code=403, detail=f"role of {user_id} may not open {screen}")
        self.user_id = user_id
        self.screen = screen


def current_user(request: Request, conn):
    """The signed-in user, from the X-User-Id header the reverse proxy sets after SSO."""
    login = request.headers.get("X-User-Id")
    if not login:
        raise HTTPException(status_code=401, detail="not signed in")
    user = query_one(conn, "SELECT user_id, role, active FROM users WHERE user_id = %s", (login,))
    if user is None or not user["active"]:
        raise HTTPException(status_code=401, detail=f"unknown or inactive user {login}")
    return user


def screens_for(conn, role: str) -> list[str]:
    row = query_one(conn, "SELECT screens FROM roles WHERE role = %s", (role,))
    return [screen.strip() for screen in row["screens"].split(",")] if row else []


def require_screen(conn, user, screen: str) -> None:
    if screen not in screens_for(conn, user["role"]):
        raise PermissionDenied(user["user_id"], screen)
