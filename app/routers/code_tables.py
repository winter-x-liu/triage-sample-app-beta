"""Code Tables screen: the lookup tables administrators maintain."""

from fastapi import APIRouter, Request

from app import db
from app.permissions import current_user, require_screen
from app.templating import templates

router = APIRouter()


@router.get("/code-tables")
def code_tables(request: Request):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "Code Tables")
        context = {
            "user": user,
            "service_types": db.query(conn, "SELECT * FROM service_types ORDER BY service_type_code"),
            "outcome_codes": db.query(conn, "SELECT * FROM outcome_codes ORDER BY outcome_code"),
            "counties": db.query(conn, "SELECT * FROM counties ORDER BY county_code"),
            "app_config": db.query(conn, "SELECT * FROM app_config ORDER BY key"),
        }
        return templates.TemplateResponse(request, "code_tables.html", context)
