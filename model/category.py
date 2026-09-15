from dataclasses import dataclass

@dataclass
class Category :
    name : str

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("카테고리 이름은 비워둘 수 없습니다.")
        
        self.name = self.name.strip()