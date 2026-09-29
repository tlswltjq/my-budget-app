from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from itertools import islice
from typing import Iterator

from model.category import Category
from model.memo import Memo
from model.money import Money
from model.transaction import Tags, Transaction
from repository.category_repository import CategoryRepository
from repository.metadata_repository import MetadataRepository
from repository.transaction_repository import TransactionRepository
from service.validation import parse_day, parse_positive_int, parse_type


@dataclass(frozen=True)
class SearchFilters:
    from_date: date | None = None
    to_date: date | None = None
    category: str | None = None
    type: str | None = None
    query: str | None = None
    tag: str | None = None


class TransactionService:
    def __init__(
        self,
        transactions: TransactionRepository,
        categories: CategoryRepository,
        metadata: MetadataRepository,
    ) -> None:
        self.transactions = transactions
        self.categories = categories
        self.metadata = metadata

    def _category(self, name: str) -> Category:
        category = self.categories.find_by_name(name)
        if category is None:
            raise ValueError(f"미등록 카테고리 '{name}'입니다. category add로 먼저 등록하세요.")
        return category

    def add(
        self, day: str, type_name: str, category_name: str,
        amount: str | int, memo: str = "", tags: str = "",
    ) -> Transaction:
        parsed_day = parse_day(day)
        parsed_type = parse_type(type_name)
        category = self._category(category_name)
        money = Money(parse_positive_int(amount, "금액"))
        parsed_tags = Tags.from_csv(tags)
        transaction_id = self.metadata.reserve_ids(1, self.transactions.max_id() + 1)[0]
        transaction = Transaction(transaction_id, parsed_type, parsed_day, money, category, Memo(memo), parsed_tags)
        self.transactions.save(transaction)
        return transaction

    def list_recent(self, limit: int) -> Iterator[Transaction]:
        if limit <= 0:
            raise ValueError("--limit는 양의 정수여야 합니다.")
        return islice(self.transactions.iter_latest(), limit)

    def search(self, filters: SearchFilters) -> Iterator[Transaction]:
        if filters.from_date and filters.to_date and filters.from_date > filters.to_date:
            raise ValueError("--from은 --to보다 늦을 수 없습니다.")
        parse_type(filters.type) if filters.type else None
        for transaction in self.transactions.iter_latest():
            if filters.from_date and transaction.date < filters.from_date:
                continue
            if filters.to_date and transaction.date > filters.to_date:
                continue
            if filters.category and transaction.category.name != filters.category.strip():
                continue
            if filters.type and transaction.type.name != filters.type:
                continue
            if filters.query and filters.query.casefold() not in transaction.memo.content.casefold():
                continue
            if filters.tag and filters.tag not in transaction.tags.names:
                continue
            yield transaction

    def update(self, transaction_id: int, changes: dict[str, str]) -> Transaction | None:
        original = self.transactions.find_by_id(transaction_id)
        if original is None:
            return None
        fields = {}
        if "date" in changes:
            fields["date"] = parse_day(changes["date"])
        if "type" in changes:
            fields["type"] = parse_type(changes["type"])
        if "category" in changes:
            fields["category"] = self._category(changes["category"])
        if "amount" in changes:
            fields["amount"] = Money(parse_positive_int(changes["amount"], "금액"))
        if "memo" in changes:
            fields["memo"] = Memo(changes["memo"])
        if "tags" in changes:
            fields["tags"] = Tags.from_csv(changes["tags"])
        if not fields:
            raise ValueError("수정할 필드를 하나 이상 지정하세요.")
        updated = replace(original, **fields)
        self.transactions.save(updated)
        return updated

    def delete(self, transaction_id: int) -> bool:
        return self.transactions.delete(transaction_id)
