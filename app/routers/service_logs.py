"""Service Log Entry screen."""

from datetime import date

from fastapi import APIRouter, Form, Request

from app import db
from app.models import ServicePlan
from app.permissions import current_user, require_screen
from app.templating import templates
from app.validators import DEFAULT_MAX_UNITS, ValidationError, validate_service_date, validate_units

router = APIRouter()
SCREEN = "Service Log Entry"


def max_units(conn) -> int:
    return int(db.app_config(conn, "max_units_per_log", DEFAULT_MAX_UNITS))


def _form(request, conn, user, child_id=None, message=None):
    service_types = db.query(conn, "SELECT service_type_code, name FROM service_types ORDER BY name")
    context = {
        "user": user,
        "child_id": child_id,
        "service_types": service_types,
        "max_units": max_units(conn),
        "message": message,
    }
    return templates.TemplateResponse(request, "service_log_form.html", context)


@router.get("/service-logs/new")
def new_form(request: Request, child_id: int | None = None):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, SCREEN)
        return _form(request, conn, user, child_id)


@router.post("/service-logs/new")
def create(
    request: Request,
    child_id: int = Form(),
    service_type_code: str = Form(),
    service_date: date = Form(),
    units: int = Form(),
    notes: str = Form(""),
):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, SCREEN)
        plan = ServicePlan.current(conn, child_id)
        if plan is None or plan.status != "Active":
            return _form(request, conn, user, child_id, "no active IFSP for this child")
        status, message = "Entered", None
        try:
            validate_units(units, max_units(conn))
            validate_service_date(service_date, plan)
        except ValidationError as error:
            status, message = "Rejected", str(error)  # kept for audit, flagged Rejected
        log_id = db.query_one(
            conn,
            "SELECT COALESCE(MAX(log_id), 0) + 1 AS n FROM service_logs"
            " WHERE child_id = %s AND plan_id = %s",
            (child_id, plan.plan_id),
        )["n"]
        conn.execute(
            "INSERT INTO service_logs (child_id, plan_id, log_id, provider_user_id,"
            " service_type_code, service_date, units, status, notes)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (child_id, plan.plan_id, log_id, user["user_id"], service_type_code, service_date,
             units, status, notes or None),
        )
        conn.commit()
        return _form(request, conn, user, child_id, message or f"saved log {log_id} as {status}")
