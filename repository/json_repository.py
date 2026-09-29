from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable, Iterator


class JsonRepository:
    """JSONL 레코드를 로컬 파일에 저장합니다."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("a", encoding="utf-8"):
            pass

    def iter_records(self) -> Iterator[dict[str, Any]]:
        """파일을 한 줄씩 읽으며 JSON 객체를 반환합니다."""
        with self.file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"{self.file_path}:{line_number}: 잘못된 JSON 레코드"
                    ) from error
                if not isinstance(record, dict):
                    raise ValueError(
                        f"{self.file_path}:{line_number}: JSON 객체가 필요합니다"
                    )
                yield record

    def _read_records(self) -> list[dict[str, Any]]:
        return list(self.iter_records())

    def _write_records(self, records: Iterable[dict[str, Any]]) -> None:
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                prefix=f".{self.file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                for record in records:
                    if not isinstance(record, dict):
                        raise ValueError("JSONL 레코드는 JSON 객체여야 합니다.")
                    file.write(json.dumps(record, ensure_ascii=False) + "\n")
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_path, self.file_path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def save(self, item: dict[str, Any]) -> None:
        records = self._read_records()
        records.append(item)
        self._write_records(records)

    def find_all(self) -> list[dict[str, Any]]:
        return self._read_records()

    def replace_all(self, records: Iterable[dict[str, Any]]) -> None:
        self._write_records(records)

    def delete(self, item_id: str | int, key_field: str = "id") -> bool:
        records = self._read_records()
        remaining = [record for record in records if record.get(key_field) != item_id]
        if len(remaining) == len(records):
            return False
        self._write_records(remaining)
        return True
