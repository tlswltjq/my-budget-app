from dataclasses import dataclass

@dataclass
class Memo :
    content : str

    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("내용을 입력해주세요.")
        
        self.name = self.name.strip()