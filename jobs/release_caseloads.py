"""Nightly: release caseload assignments 30 days after the IFSP end date (State Alpha policy)."""

from app import db

RELEASE_AFTER_DAYS = 30


def main() -> None:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE caseloads c SET released_at = p.end_date + %s"
                " FROM service_plans p"
                " WHERE p.child_id = c.child_id AND p.coordinator_user_id = c.user_id"
                " AND p.status = 'Ended' AND c.released_at IS NULL"
                " AND p.end_date + %s <= CURRENT_DATE",
                (RELEASE_AFTER_DAYS, RELEASE_AFTER_DAYS),
            )
            print(f"released {cur.rowcount} caseload assignment(s)")
        conn.commit()


if __name__ == "__main__":
    main()
