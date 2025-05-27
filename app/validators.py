"""Business rules checked before a row is written."""

DEFAULT_MAX_UNITS = 16  # 15-minute units per service log; app_config.max_units_per_log overrides


class ValidationError(ValueError):
    pass


def validate_units(units: int, max_units: int = DEFAULT_MAX_UNITS) -> None:
    if units < 1:
        raise ValidationError("units must be at least 1")
    if units > max_units:
        raise ValidationError(f"a service log may not exceed {max_units} units")


def validate_service_date(service_date, plan) -> None:
    if service_date < plan.start_date:
        raise ValidationError("service date is before the IFSP start date")
    if plan.end_date is not None and service_date > plan.end_date:
        raise ValidationError("service date is after the IFSP end date")
