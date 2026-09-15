from typing import List, Optional

from model.category_repository import CategoryRepository
from model.category import Category

def get_categories(limit: int) -> List[Category]:
    return CategoryRepository.get(limit)
