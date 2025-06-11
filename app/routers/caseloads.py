"""Caseload screen: the children assigned to the signed-in service coordinator."""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app import db
from app.permissions import current_user, require_screen
from app.templating import templates

router = APIRouter()


@router.get("/caseload")
def caseload(request: Request):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "Caseload")
        rows = db.query(
            conn,
            "SELECT c.child_id, ch.last_name, ch.first_name, c.assigned_at,"
            " p.plan_id, p.status AS plan_status, p.start_date, p.end_date"
            " FROM caseloads c"
            " JOIN children ch ON ch.child_id = c.child_id"
            " LEFT JOIN service_plans p ON p.child_id = c.child_id"
            " AND p.coordinator_user_id = c.user_id"
            " WHERE c.user_id = %s AND c.released_at IS NULL"
            " ORDER BY ch.last_name, ch.first_name",
            (user["user_id"],),
        )
        # Long caseloads: show the children with an active IFSP only.
        rows = [row for row in rows if row["plan_status"] == "Active"]
        return templates.TemplateResponse(request, "caseload.html", {"user": user, "rows": rows})


@router.post("/caseload/{child_id}/release")
def release(child_id: int, request: Request):
    """Release a child from the signed-in coordinator's caseload; State Beta releases by hand."""
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "Caseload")
        conn.execute(
            "UPDATE caseloads SET released_at = CURRENT_DATE"
            " WHERE user_id = %s AND child_id = %s AND released_at IS NULL",
            (user["user_id"], child_id),
        )
        conn.commit()
    return RedirectResponse("/caseload", status_code=303)
