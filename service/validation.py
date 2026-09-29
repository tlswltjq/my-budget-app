from __future__ import annotations

import re
from datetime import date

from model.transaction import Type


def parse_day(value: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("날짜는 YYYY-MM-DD 형식으로 입력하세요.")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("존재하지 않는 날짜입니다. YYYY-MM-DD를 확인하세요.") from error


def parse_month(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}", value):
        raise ValueError("월은 YYYY-MM 형식으로 입력하세요.")
    parse_day(value + "-01")
    return value


def parse_positive_int(value: str | int, label: str) -> int:
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)) or int(value) <= 0:
        raise ValueError(f"{label}은(는) 양의 정수여야 합니다.")
    return int(value)


def parse_type(value: str) -> Type:
    try:
        return Type[value]
    except KeyError as error:
        raise ValueError("타입은 income 또는 expense여야 합니다.") from error


def parse_id(value: str | int) -> int:
    text = str(value)
    if text.startswith("TX-"):
        text = text[3:]
    return parse_positive_int(text, "거래 ID")
