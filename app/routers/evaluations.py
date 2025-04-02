"""Evaluation screen: a child's evaluations and their outcomes."""

from fastapi import APIRouter, Request

from app import db
from app.models import Child
from app.permissions import current_user, require_screen
from app.templating import templates

router = APIRouter()


@router.get("/children/{child_id}/evaluations")
def evaluations(child_id: int, request: Request):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "Evaluation")
        child = Child.get(conn, child_id)
        rows = db.query(
            conn,
            "SELECT e.evaluation_id, e.evaluator_user_id, e.scheduled_at, e.completed_at,"
            " e.outcome_code, o.description FROM evaluations e"
            " LEFT JOIN outcome_codes o ON o.outcome_code = e.outcome_code"
            " WHERE e.child_id = %s ORDER BY e.scheduled_at",
            (child_id,),
        )
        context = {"user": user, "child": child, "rows": rows}
        return templates.TemplateResponse(request, "evaluations.html", context)
