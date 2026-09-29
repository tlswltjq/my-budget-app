from __future__ import annotations

from model.budget import Budget
from model.money import Money
from repository.json_repository import JsonRepository


class BudgetRepository:
    def __init__(self, file_path: str):
        self._storage = JsonRepository(file_path)

    def find_by_month(self, month: str) -> Budget | None:
        for record in self._storage.iter_records():
            if record["month"] == month:
                if type(record["amount"]) is not int:
                    raise ValueError("저장된 예산 금액은 정수여야 합니다.")
                return Budget(month, Money(record["amount"]))
        return None

    def save(self, budget: Budget) -> None:
        records = [record for record in self._storage.iter_records() if record["month"] != budget.month]
        records.append({"month": budget.month, "amount": budget.amount.amount})
        records.sort(key=lambda record: record["month"])
        self._storage.replace_all(records)
