"""Reports screen: counts by county and status."""

from fastapi import APIRouter, Request

from app import db
from app.permissions import current_user, require_screen
from app.templating import templates

router = APIRouter()


@router.get("/reports")
def reports(request: Request):
    with db.connect() as conn:
        user = current_user(request, conn)
        require_screen(conn, user, "Reports")
        by_county = db.query(
            conn,
            "SELECT co.name AS county, ch.status, count(*) AS children FROM children ch"
            " JOIN counties co ON co.county_code = ch.county_code"
            " GROUP BY co.name, ch.status ORDER BY co.name, ch.status",
        )
        units = db.query(
            conn,
            "SELECT service_type_code, status, sum(units) AS units FROM service_logs"
            " WHERE service_date >= CURRENT_DATE - 30 GROUP BY service_type_code, status"
            " ORDER BY service_type_code, status",
        )
        context = {"user": user, "by_county": by_county, "units": units}
        return templates.TemplateResponse(request, "reports.html", context)
