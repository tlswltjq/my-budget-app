from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
from typing import Dict, Any

from model.money import Money
from model.category import Category

class Type(Enum):
    income = 1
    expense = -1

@dataclass
class Memo:
    content: str

    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("내용을 입력해주세요.")
        self.content = self.content.strip()

@dataclass
class Tags:
    name: str

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("내용을 입력해주세요.")
        self.name = self.name.strip()

@dataclass
class Transaction:
    id: int
    type: Type
    date: datetime
    amount: Money
    category: Category
    memo: Memo
    tags: Tags

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.name,
            "date": self.date.isoformat(),
            "amount": self.amount.amount,
            "category": self.category.name,
            "memo": self.memo.content,      
            "tags": self.tags.name          
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        return cls(
            id=int(data["id"]),
            type=Type[data["type"]],
            date=datetime.fromisoformat(data["date"]),
            amount=Money(data["amount"]),
            category=Category(data["category"]),
            memo=Memo(content=data["memo"]),
            tags=Tags(name=data["tags"])
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "Transaction":
        data = json.loads(json_str)
        return cls.from_dict(data)