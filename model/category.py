from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("카테고리 이름을 입력하세요.")
        object.__setattr__(self, "name", self.name.strip())

    def __str__(self) -> str:
        return self.name
