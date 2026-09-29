import argparse

from command.base_command import BaseCommand
from command.common import display_id
from service.transaction_service import TransactionService
from service.validation import parse_id


class DeleteCommand(BaseCommand):
    def __init__(self, service: TransactionService) -> None:
        self.service = service

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", required=True, help="거래 ID (숫자 또는 TX-000001)")

    def execute(self, args: argparse.Namespace) -> int:
        transaction_id = parse_id(args.id)
        if self.service.delete(transaction_id):
            print(f"[삭제 완료] id={display_id(transaction_id)}")
        else:
            print(f"[없는 데이터] id={display_id(transaction_id)}")
            return 1
        return 0
