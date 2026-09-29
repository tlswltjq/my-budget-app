from __future__ import annotations

from repository.json_repository import JsonRepository


class MetadataRepository:
    def __init__(self, file_path: str):
        self._storage = JsonRepository(file_path)

    def reserve_ids(self, count: int, minimum_next: int) -> list[int]:
        if count < 1:
            raise ValueError("예약할 ID 수는 1 이상이어야 합니다.")
        records = self._storage.find_all()
        counter = next((record for record in records if record.get("kind") == "counter"), None)
        next_id = max(minimum_next, int(counter["next_id"]) if counter else 1)
        if counter is None:
            records.append({"kind": "counter", "next_id": next_id + count})
        else:
            counter["next_id"] = next_id + count
        self._storage.replace_all(records)
        return list(range(next_id, next_id + count))

    def import_count(self, checksum: str) -> int | None:
        for record in self._storage.iter_records():
            if record.get("kind") == "import" and record.get("sha256") == checksum:
                return int(record["count"])
        return None

    def mark_import(self, checksum: str, count: int) -> None:
        records = self._storage.find_all()
        if any(record.get("kind") == "import" and record.get("sha256") == checksum for record in records):
            return
        records.append({"kind": "import", "sha256": checksum, "count": count})
        self._storage.replace_all(records)
