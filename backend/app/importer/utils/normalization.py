from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def norm_str(value) -> str | None:
    if is_empty(value):
        return None
    text = str(value).strip()
    text = " ".join(text.split())
    return text or None


def norm_email(value) -> str | None:
    text = norm_str(value)
    if text is None:
        return None
    return text.lower()


def norm_decimal(value) -> Decimal | None:
    if is_empty(value):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip().replace("R$", "").replace(" ", "")
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned and "." not in cleaned:
            cleaned = cleaned.replace(",", ".")
        return Decimal(cleaned)
    raise InvalidOperation("Invalid decimal value.")


def norm_int(value) -> int | None:
    if is_empty(value):
        return None
    if isinstance(value, bool):
        raise ValueError("Invalid int value.")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise ValueError("Invalid int value.")
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        return int(cleaned)
    raise ValueError("Invalid int value.")


def norm_date(value) -> date | None:
    if is_empty(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        try:
            return datetime.fromisoformat(cleaned).date()
        except ValueError:
            for fmt in ("%d/%m/%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(cleaned, fmt).date()
                except ValueError:
                    continue
    raise ValueError("Invalid date value.")
