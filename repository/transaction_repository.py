from __future__ import annotations

from typing import Iterable, Iterator

from model.transaction import Transaction
from repository.json_repository import JsonRepository


class TransactionRepository:
    """거래 파일을 날짜·ID 내림차순으로 유지합니다."""

    def __init__(self, file_path: str = "transaction.jsonl"):
        self._storage = JsonRepository(file_path)

    def iter_latest(self) -> Iterator[Transaction]:
        for record in self._storage.iter_records():
            yield Transaction.from_dict(record)

    def find_all(self) -> list[Transaction]:
        return list(self.iter_latest())

    def find_by_id(self, transaction_id: int) -> Transaction | None:
        return next((tx for tx in self.iter_latest() if tx.id == transaction_id), None)

    def max_id(self) -> int:
        return max((tx.id for tx in self.iter_latest()), default=0)

    def count_by_source(self, checksum: str) -> int:
        return sum(tx.source_checksum == checksum for tx in self.iter_latest())

    def save(self, transaction: Transaction) -> None:
        records = self._storage.find_all()
        for index, record in enumerate(records):
            if int(record["id"]) == transaction.id:
                records[index] = transaction.to_dict()
                break
        else:
            records.append(transaction.to_dict())
        self._replace_sorted(records)

    def add_many(self, transactions: Iterable[Transaction]) -> None:
        records = self._storage.find_all()
        existing_ids = {int(record["id"]) for record in records}
        for transaction in transactions:
            if transaction.id in existing_ids:
                raise ValueError(f"중복 거래 ID: {transaction.id}")
            existing_ids.add(transaction.id)
            records.append(transaction.to_dict())
        self._replace_sorted(records)

    def delete(self, transaction_id: int) -> bool:
        records = self._storage.find_all()
        remaining = [record for record in records if int(record["id"]) != transaction_id]
        if len(remaining) == len(records):
            return False
        self._storage.replace_all(remaining)
        return True

    def _replace_sorted(self, records: list[dict]) -> None:
        records.sort(key=lambda record: (str(record["date"])[:10], int(record["id"])), reverse=True)
        self._storage.replace_all(records)
