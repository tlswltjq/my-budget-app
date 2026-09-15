from typing import List, Optional
from model.transaction import Transaction
from data.json_handler import JsonHandler

DATA_ROOT = "data/transaction_data.json"

class TransactionRepository:

    @classmethod
    def save(cls, transaction: Transaction) -> Transaction:
        raw_list = JsonHandler.read_json(DATA_ROOT)
        
        tx_list = [Transaction.from_dict(t) for t in raw_list]
        
        tx_list.append(transaction)
        
        data_to_save = [t.to_dict() for t in tx_list]
        JsonHandler.write_json(DATA_ROOT, data_to_save)
        
        return transaction

    @classmethod
    def find_all(cls) -> List[Transaction]:
        raw_list = JsonHandler.read_json(DATA_ROOT)
        return [Transaction.from_dict(t) for t in raw_list]