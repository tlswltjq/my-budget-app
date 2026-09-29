from __future__ import annotations

from model.budget import Budget
from model.money import Money
from repository.budget_repository import BudgetRepository
from service.validation import parse_month, parse_positive_int


class BudgetService:
    def __init__(self, budgets: BudgetRepository) -> None:
        self.budgets = budgets

    def set(self, month: str, amount: str | int) -> Budget:
        budget = Budget(parse_month(month), Money(parse_positive_int(amount, "예산")))
        self.budgets.save(budget)
        return budget

    def get(self, month: str) -> Budget | None:
        return self.budgets.find_by_month(parse_month(month))
