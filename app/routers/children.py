"""Child Search and Child Summary screens."""

from fastapi import APIRouter, HTTPException, Request

from app import db
from app.models import Child, Referral, ServicePlan
from app.permissions import current_user, require_screen
from app.templating import templates

router = APIRouter()


@router.get("/children")
def child_search(request: Request, q: str = ""):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "Child Search")
        rows = []
        if q.isdigit():
            rows = db.query(
                conn,
                "SELECT child_id, first_name, last_name, dob, status FROM children WHERE child_id = %s",
                (int(q),),
            )
        elif q:
            rows = db.query(
                conn,
                "SELECT child_id, first_name, last_name, dob, status FROM children"
                " WHERE last_name ILIKE %s ORDER BY last_name, first_name LIMIT 50",
                (q + "%",),
            )
        return templates.TemplateResponse(
            request, "children_search.html", {"user": user, "q": q, "rows": rows}
        )


@router.get("/children/{child_id}/summary")
def child_summary(child_id: int, request: Request):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "Child Summary")
        child = Child.get(conn, child_id)
        if child is None:
            raise HTTPException(status_code=404, detail=f"no child {child_id}")
        plan = ServicePlan.current(conn, child_id)
        referral = Referral.latest(conn, child_id)
        caseload = db.query(
            conn,
            "SELECT user_id, assigned_at, released_at FROM caseloads WHERE child_id = %s"
            " ORDER BY assigned_at DESC",
            (child_id,),
        )
        context = {
            "user": user,
            "child": child,
            "plan": plan,
            "referral_source": referral.source if referral else None,
            "referral_received": referral.received_at if referral else None,
            "caseload": caseload,
        }
        return templates.TemplateResponse(request, "child_summary.html", context)
