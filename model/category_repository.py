from typing import List, Optional
from model.category import Category

class CategoryRepository:
    # TODO : 실제 파일과 연결 필요 
    mock = [Category("식비"), Category("교통비"), Category("취미")]
    @classmethod
    def save(cls, category: Category) -> None:
        pass

    @classmethod
    def get(cls, limit: Optional[int] = None) -> List[Category]:
        return cls.mock

    @classmethod
    def get_by_name(cls, name: str) -> Optional[Category]:
        all_categories = cls.get()
        return None

    @classmethod
    def delete_by_name(cls, name: str) -> bool:
        return True