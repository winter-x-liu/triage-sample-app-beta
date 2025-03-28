"""Referral Intake screen: a new child and the referral that brought them."""

from datetime import date, datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app import db
from app.permissions import current_user, require_screen
from app.templating import templates

router = APIRouter()
SCREEN = "Referral Intake"
SOURCES = ["Physician", "Parent", "Hospital", "Child Care", "Other"]


@router.get("/referrals/new")
def new_form(request: Request):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, SCREEN)
        counties = db.query(conn, "SELECT county_code, name FROM counties ORDER BY name")
        context = {"user": user, "counties": counties, "sources": SOURCES}
        return templates.TemplateResponse(request, "referral_form.html", context)


@router.post("/referrals/new")
def create(
    request: Request,
    first_name: str = Form(),
    last_name: str = Form(),
    dob: date = Form(),
    county_code: str = Form(),
    source: str = Form(),
    received_at: date = Form(),
):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, SCREEN)
        child_id = db.query_one(conn, "SELECT COALESCE(MAX(child_id), 0) + 1 AS n FROM children")["n"]
        conn.execute(
            "INSERT INTO children (child_id, first_name, last_name, dob, status, county_code, created_at)"
            " VALUES (%s, %s, %s, %s, 'Referred', %s, %s)",
            (child_id, first_name, last_name, dob, county_code, datetime.now()),
        )
        referral_id = db.query_one(conn, "SELECT COALESCE(MAX(referral_id), 0) + 1 AS n FROM referrals")["n"]
        conn.execute(
            "INSERT INTO referrals (referral_id, child_id, source, received_at, status)"
            " VALUES (%s, %s, %s, %s, 'Open')",
            (referral_id, child_id, source, received_at),
        )
        conn.commit()
    return RedirectResponse(f"/children/{child_id}/summary", status_code=303)
