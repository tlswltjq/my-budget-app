from model.transaction import Transaction


def display_id(transaction_id: int) -> str:
    return f"TX-{transaction_id:06d}"


def format_transaction(transaction: Transaction) -> str:
    return (
        f"{display_id(transaction.id)} | {transaction.date.isoformat()} | "
        f"{transaction.type.name:<7} | {transaction.category.name} | "
        f"{transaction.amount.amount} | {transaction.memo.content}"
    )
