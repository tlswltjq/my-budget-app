from datetime import datetime, date
from typing import Optional

from model.transaction import Transaction, Type, Memo, Tags
from model.category import Category
from model.money import Money
from model.transaction_repository import TransactionRepository


def get_next_id() -> int:
    """기존 거래 내역을 조회하여 다음 Auto Increment ID를 생성합니다."""
    transactions = TransactionRepository.find_all()
    if not transactions:
        return 1
    return max(tx.id for tx in transactions) + 1


def add_transaction(
    type_str: str,
    amount: int,
    category: str,
    memo: str,
    tag: str,
    date_val: Optional[date] = None
) -> Transaction:
    """CLI에서 전달받은 인자를 도메인 객체로 변환하여 저장합니다."""
    
    # 1. date 인자 처리 (date 타입인 경우 datetime으로 변환)
    if date_val is None:
        tx_datetime = datetime.now()
    elif isinstance(date_val, date) and not isinstance(date_val, datetime):
        tx_datetime = datetime.combine(date_val, datetime.min.time())
    else:
        tx_datetime = date_val

    # 2. 값 객체 및 엔티티 생성 (생성 시 __post_init__ 유효성 검증 자동 수행)
    transaction = Transaction(
        id=get_next_id(),
        type=Type[type_str],              # 'income' -> Type.income
        date=tx_datetime,
        amount=Money(amount=amount),
        category=Category(name=category),
        memo=Memo(content=memo),
        tags=Tags(name=tag)
    )

    # 3. 리포지토리를 통해 저장
    saved_tx = TransactionRepository.save(transaction)
    print(f"성공적으로 저장되었습니다. (ID: {saved_tx.id})")
    
    return saved_tx