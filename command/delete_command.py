import argparse
from typing import Callable

from command.base_command import BaseCommand
from service.transaction_service import TransactionService
from service.validation import parse_id


class DeleteCommand(BaseCommand):
    def __init__(self, service: TransactionService, display_id: Callable[[int], str]) -> None:
        self.service = service
        self.display_id = display_id

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", required=True, help="거래 ID (숫자 또는 TX-000001)")

    def execute(self, args: argparse.Namespace) -> int:
        # delete: ID에 해당하는 거래를 삭제함
        transaction_id = parse_id(args.id)
        if self.service.delete(transaction_id):
            print(f"[삭제 완료] id={self.display_id(transaction_id)}")
        else:
            print(f"[없는 데이터] id={self.display_id(transaction_id)}")
            return 1
        return 0
