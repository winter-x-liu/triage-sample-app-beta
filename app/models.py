"""Row models mirroring the EI schema. Lookups return None when no row exists."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.db import query, query_one


@dataclass
class Child:
    child_id: int
    first_name: str
    last_name: str
    dob: date
    state_id_number: str | None
    status: str
    county_code: str
    created_at: datetime

    @classmethod
    def get(cls, conn, child_id: int) -> Child | None:
        row = query_one(conn, "SELECT * FROM children WHERE child_id = %s", (child_id,))
        return cls(**row) if row else None


@dataclass
class Referral:
    referral_id: int
    child_id: int
    source: str
    received_at: date
    status: str

    @classmethod
    def latest(cls, conn, child_id: int) -> Referral | None:
        row = query_one(
            conn,
            "SELECT * FROM referrals WHERE child_id = %s ORDER BY received_at DESC LIMIT 1",
            (child_id,),
        )
        return cls(**row) if row else None


@dataclass
class ServicePlan:
    plan_id: int
    child_id: int
    status: str
    start_date: date
    end_date: date | None
    coordinator_user_id: str

    @classmethod
    def current(cls, conn, child_id: int) -> ServicePlan | None:
        row = query_one(
            conn,
            "SELECT * FROM service_plans WHERE child_id = %s ORDER BY start_date DESC LIMIT 1",
            (child_id,),
        )
        return cls(**row) if row else None


@dataclass
class ServiceLog:
    child_id: int
    plan_id: int
    log_id: int
    provider_user_id: str
    service_type_code: str
    service_date: date
    units: int
    status: str
    notes: str | None

    @classmethod
    def for_plan(cls, conn, child_id: int, plan_id: int) -> list[ServiceLog]:
        rows = query(
            conn,
            "SELECT * FROM service_logs WHERE child_id = %s AND plan_id = %s ORDER BY log_id",
            (child_id, plan_id),
        )
        return [cls(**row) for row in rows]


@dataclass
class User:
    user_id: str
    role: str
    email: str
    active: bool
    created_at: datetime

    @classmethod
    def get(cls, conn, user_id: str) -> User | None:
        row = query_one(conn, "SELECT * FROM users WHERE user_id = %s", (user_id,))
        return cls(**row) if row else None
