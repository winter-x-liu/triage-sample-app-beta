# State Beta Early Intervention application

Version 4.3. The web application State Beta's Early Intervention (EI) program uses to
track children from referral through evaluation, the Individualized Family Service Plan
(IFSP), service logs, and service coordinators' caseloads. FastAPI, Jinja2 templates,
Postgres through psycopg.

## Screens and routes

| Screen | Route | Module |
| --- | --- | --- |
| Child Search | `GET /children?q=` | `app/routers/children.py` |
| Child Summary | `GET /children/{child_id}/summary` | `app/routers/children.py` |
| Referral Intake | `GET,POST /referrals/new` | `app/routers/referrals.py` |
| Evaluation | `GET /children/{child_id}/evaluations` | `app/routers/evaluations.py` |
| IFSP | `GET /children/{child_id}/ifsp` | `app/routers/plans.py` |
| Service Log Entry | `GET,POST /service-logs/new` | `app/routers/service_logs.py` |
| Caseload | `GET /caseload` | `app/routers/caseloads.py` |
| Reports | `GET /reports` | `app/routers/reports.py` |
| Code Tables | `GET /code-tables` | `app/routers/code_tables.py` |
| User Admin | `GET /users` | `app/routers/users.py` |

Which roles may open a screen is data, not code: `roles.screens` holds a comma-separated
list of screen names per role, and `app/permissions.py` checks it on every request. The
signed-in user is the login name in the `X-User-Id` header, set by the reverse proxy
after single sign-on.

## Logs

Every request writes one JSON object to stdout: `ts`, `level`, `request_id`, `user_id`,
`method`, `route`, `status`, `duration_ms`, `message`, and on an error `exception_type`.
The `X-Request-Id` response header carries the same id. An unhandled exception is also
written to the `error_log` table with its stack trace, so support can look it up by
request id without the log stream.

## Policies this version implements

- A service log may not exceed 8 units of 15 minutes. The cap is read from
  `app_config.max_units_per_log`; a log over the cap is saved with status Rejected so
  the attempt is auditable.
- A child is released from the service coordinator's caseload automatically 30 days
  after the IFSP end date (`jobs/release_caseloads.py`, run nightly).

## Running

```
export DATABASE_URL=postgresql://app@db/mockapp APP_SCHEMA=app_beta
uvicorn app.main:app
```
