from model.category import Category
from repository.category_repository import CategoryRepository
from repository.transaction_repository import TransactionRepository


class CategoryService:
    def __init__(self, categories: CategoryRepository, transactions: TransactionRepository) -> None:
        self.categories = categories
        self.transactions = transactions

    def add(self, name: str) -> Category:
        category = Category(name)
        if self.categories.find_by_name(category.name) is not None:
            raise ValueError(f"카테고리 '{category.name}'은(는) 이미 등록되어 있습니다.")
        self.categories.save(category)
        return category

    def list(self) -> list[Category]:
        return self.categories.find_all()

    def remove(self, name: str) -> bool:
        category = self.categories.find_by_name(name)
        if category is None:
            return False
        if any(tx.category.name == category.name for tx in self.transactions.iter_latest()):
            raise ValueError(f"카테고리 '{category.name}'은(는) 거래에서 사용 중입니다.")
        return self.categories.delete(category.name)
