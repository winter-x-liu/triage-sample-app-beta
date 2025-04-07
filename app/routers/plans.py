"""IFSP screen: the child's current plan and the services logged against it."""

from fastapi import APIRouter, Request

from app import db
from app.models import Child, ServiceLog, ServicePlan
from app.permissions import current_user, require_screen
from app.templating import templates

router = APIRouter()


@router.get("/children/{child_id}/ifsp")
def ifsp(child_id: int, request: Request):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "IFSP")
        child = Child.get(conn, child_id)
        plan = ServicePlan.current(conn, child_id)
        logs = ServiceLog.for_plan(conn, child_id, plan.plan_id) if plan else []
        context = {"user": user, "child": child, "plan": plan, "logs": logs}
        return templates.TemplateResponse(request, "ifsp.html", context)
