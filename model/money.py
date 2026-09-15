from dataclasses import dataclass

@dataclass
class Money :
    amount : int

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("금액은 0 보다 커야 합니다.")