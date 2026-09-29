from dataclasses import dataclass


@dataclass(frozen=True)
class Memo:
    content: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise ValueError("메모는 문자열이어야 합니다.")
        object.__setattr__(self, "content", self.content.strip())
