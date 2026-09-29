from __future__ import annotations

import csv
import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from model.memo import Memo
from model.money import Money
from model.transaction import Tags, Transaction
from repository.category_repository import CategoryRepository
from repository.metadata_repository import MetadataRepository
from repository.transaction_repository import TransactionRepository
from service.validation import parse_day, parse_month, parse_positive_int, parse_type


CSV_COLUMNS = ("date", "type", "category", "amount", "memo", "tags")
REQUIRED_COLUMNS = set(CSV_COLUMNS[:4])


def file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class ImportResult:
    imported: int
    skipped: int
    duplicate_file: bool = False


class ImportService:
    def __init__(
        self,
        transactions: TransactionRepository,
        categories: CategoryRepository,
        metadata: MetadataRepository,
    ) -> None:
        self.transactions = transactions
        self.categories = categories
        self.metadata = metadata

    def import_csv(self, path_value: str) -> ImportResult:
        path = Path(path_value)
        checksum = file_checksum(path)
        previous_count = self.metadata.import_count(checksum)
        if previous_count is not None:
            return ImportResult(0, previous_count, True)

        recovered_count = self.transactions.count_by_source(checksum)
        if recovered_count:
            self.metadata.mark_import(checksum, recovered_count)
            return ImportResult(0, recovered_count, True)

        parsed = []
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
                raise ValueError("CSV 헤더에 date,type,category,amount가 필요합니다.")
            for row in reader:
                line_number = reader.line_num
                try:
                    if None in row:
                        raise ValueError("열 개수가 헤더와 다릅니다.")
                    day = parse_day(row["date"] or "")
                    type_value = parse_type(row["type"] or "")
                    category = self.categories.find_by_name(row["category"] or "")
                    if category is None:
                        raise ValueError("미등록 카테고리입니다. category add로 등록하세요.")
                    amount = Money(parse_positive_int(row["amount"] or "", "금액"))
                    memo = Memo(row.get("memo") or "")
                    tags = Tags.from_csv(row.get("tags") or "")
                except (ValueError, TypeError) as error:
                    raise ValueError(f"CSV {line_number}행: {error}") from error
                parsed.append((day, type_value, category, amount, memo, tags))

        if file_checksum(path) != checksum:
            raise ValueError("가져오는 동안 CSV 파일이 변경되었습니다. 다시 시도하세요.")
        if parsed:
            ids = self.metadata.reserve_ids(len(parsed), self.transactions.max_id() + 1)
            transactions = [
                Transaction(id_value, type_value, day, amount, category, memo, tags, checksum)
                for id_value, (day, type_value, category, amount, memo, tags) in zip(ids, parsed)
            ]
            self.transactions.add_many(transactions)
        self.metadata.mark_import(checksum, len(parsed))
        return ImportResult(len(parsed), 0)


class ExportService:
    def __init__(self, transactions: TransactionRepository, protected_paths: list[Path]) -> None:
        self.transactions = transactions
        self.protected_paths = protected_paths

    def export_csv(
        self, path_value: str, month: str | None = None,
        from_day: str | None = None, to_day: str | None = None,
    ) -> int:
        if bool(month) == bool(from_day or to_day):
            raise ValueError("--month 또는 --from과 --to를 지정하세요.")
        if month:
            parse_month(month)
        elif not from_day or not to_day:
            raise ValueError("기간 내보내기에는 --from과 --to가 모두 필요합니다.")
        start = parse_day(from_day) if from_day else None
        end = parse_day(to_day) if to_day else None
        if start and end and start > end:
            raise ValueError("--from은 --to보다 늦을 수 없습니다.")

        path = Path(path_value)
        if path.resolve() in {protected.resolve() for protected in self.protected_paths}:
            raise ValueError("저장 파일을 CSV 출력 경로로 사용할 수 없습니다.")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        count = 0
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="", dir=path.parent,
                prefix=f".{path.name}.", suffix=".tmp", delete=False,
            ) as file:
                temporary_path = Path(file.name)
                writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                for transaction in self.transactions.iter_latest():
                    if month and transaction.date.strftime("%Y-%m") != month:
                        continue
                    if start and transaction.date < start:
                        continue
                    if end and transaction.date > end:
                        continue
                    writer.writerow({
                        "date": transaction.date.isoformat(),
                        "type": transaction.type.name,
                        "category": transaction.category.name,
                        "amount": transaction.amount.amount,
                        "memo": transaction.memo.content,
                        "tags": transaction.tags.to_csv(),
                    })
                    count += 1
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_path, path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        return count
