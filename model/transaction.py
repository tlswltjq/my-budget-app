from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

from model.category import Category
from model.memo import Memo
from model.money import Money


class Type(Enum):
    income = 1
    expense = -1


@dataclass(frozen=True)
class Tags:
    names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.names, (tuple, list)) or any(
            not isinstance(name, str) or not name.strip() or "," in name
            for name in self.names
        ):
            raise ValueError("태그는 쉼표가 없는 문자열이어야 합니다.")
        object.__setattr__(self, "names", tuple(name.strip() for name in self.names))

    @classmethod
    def from_csv(cls, value: str) -> Tags:
        if not isinstance(value, str):
            raise ValueError("태그는 문자열이어야 합니다.")
        if not value.strip():
            return cls()
        return cls(tuple(part.strip() for part in value.split(",")))

    def to_csv(self) -> str:
        return ",".join(self.names)


@dataclass(frozen=True)
class Transaction:
    id: int
    type: Type
    date: date
    amount: Money
    category: Category
    memo: Memo = Memo()
    tags: Tags = Tags()
    source_checksum: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.id, bool) or not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("거래 ID는 양의 정수여야 합니다.")
        if not isinstance(self.type, Type) or type(self.date) is not date:
            raise ValueError("거래 타입 또는 날짜가 올바르지 않습니다.")
        if not isinstance(self.amount, Money) or not isinstance(self.category, Category):
            raise ValueError("거래 금액 또는 카테고리가 올바르지 않습니다.")
        if not isinstance(self.memo, Memo) or not isinstance(self.tags, Tags):
            raise ValueError("거래 메모 또는 태그가 올바르지 않습니다.")

    def to_dict(self) -> dict[str, Any]:
        record = {
            "id": self.id,
            "type": self.type.name,
            "date": self.date.isoformat(),
            "amount": self.amount.amount,
            "category": self.category.name,
            "memo": self.memo.content,
            "tags": list(self.tags.names),
        }
        if self.source_checksum is not None:
            record["source_checksum"] = self.source_checksum
        return record

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transaction:
        if type(data["id"]) is not int or type(data["amount"]) is not int:
            raise ValueError("저장된 거래 ID와 금액은 정수여야 합니다.")
        raw_tags = data.get("tags", [])
        tags = Tags.from_csv(raw_tags) if isinstance(raw_tags, str) else Tags(tuple(raw_tags))
        return cls(
            id=data["id"],
            type=Type[str(data["type"])],
            date=date.fromisoformat(str(data["date"])[:10]),
            amount=Money(data["amount"]),
            category=Category(data["category"]),
            memo=Memo(data.get("memo", "")),
            tags=tags,
            source_checksum=data.get("source_checksum"),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, value: str) -> Transaction:
        return cls.from_dict(json.loads(value))
