from __future__ import annotations

from model.category import Category
from repository.json_repository import JsonRepository


class CategoryRepository:
    def __init__(self, file_path: str = "category.jsonl"):
        self._storage = JsonRepository(file_path)

    def save(self, category: Category) -> None:
        records = self._storage.find_all()
        if any(record["name"] == category.name for record in records):
            return
        records.append({"name": category.name})
        self._storage.replace_all(records)

    def find_all(self) -> list[Category]:
        return [Category(record["name"]) for record in self._storage.find_all()]

    def find_by_name(self, name: str) -> Category | None:
        normalized_name = Category(name).name
        for category in self.find_all():
            if category.name == normalized_name:
                return category
        return None

    def delete(self, name: str) -> bool:
        return self._storage.delete(Category(name).name, key_field="name")
