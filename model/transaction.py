from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from money import Money
from category import Category

@dataclass
class Transaction :
    id : int
    type : Type
    date : datetime
    amount : Money
    category : Category
    memo : Memo
    tags : Tags

@dataclass
class Memo :
    content : str

    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("내용을 입력해주세요.")
        
        self.name = self.name.strip()

@dataclass
class Tags :
    name : str

    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("내용을 입력해주세요.")
        
        self.name = self.name.strip()

class Type(Enum):
    income = 1
    expense = -1

