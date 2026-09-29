from dataclasses import dataclass
from datetime import date

from model.money import Money


@dataclass(frozen=True)
class Budget:
    month: str
    amount: Money

    def __post_init__(self) -> None:
        if len(self.month) != 7 or self.month[4] != "-":
            raise ValueError("월은 YYYY-MM 형식이어야 합니다.")
        try:
            date.fromisoformat(self.month + "-01")
        except ValueError as error:
            raise ValueError("월은 YYYY-MM 형식이어야 합니다.") from error
