from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from model.budget import Budget
from repository.transaction_repository import TransactionRepository
from service.budget_service import BudgetService
from service.validation import parse_month


@dataclass(frozen=True)
class MonthlySummary:
    month: str
    count: int
    income: int
    expense: int
    top_categories: list[tuple[str, int]]
    budget: Budget | None

    @property
    def balance(self) -> int:
        return self.income - self.expense

    @property
    def usage_percent(self) -> float | None:
        return self.expense / self.budget.amount.amount * 100 if self.budget else None


class SummaryService:
    def __init__(self, transactions: TransactionRepository, budgets: BudgetService) -> None:
        self.transactions = transactions
        self.budgets = budgets

    def monthly(self, month: str, top: int) -> MonthlySummary:
        parse_month(month)
        if top <= 0:
            raise ValueError("--top은 양의 정수여야 합니다.")
        income = expense = count = 0
        by_category: dict[str, int] = defaultdict(int)
        for transaction in self.transactions.iter_latest():
            if transaction.date.strftime("%Y-%m") != month:
                continue
            count += 1
            if transaction.type.name == "income":
                income += transaction.amount.amount
            else:
                expense += transaction.amount.amount
                by_category[transaction.category.name] += transaction.amount.amount
        top_categories = sorted(by_category.items(), key=lambda item: (-item[1], item[0]))[:top]
        return MonthlySummary(month, count, income, expense, top_categories, self.budgets.get(month))
