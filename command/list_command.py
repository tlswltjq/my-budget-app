import argparse

from command.base_command import BaseCommand
from command.common import format_transaction
from service.transaction_service import TransactionService


class ListCommand(BaseCommand):
    def __init__(self, service: TransactionService) -> None:
        self.service = service

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=50, help="출력할 최대 거래 수 (기본값: 50)")

    def execute(self, args: argparse.Namespace) -> int:
        found = False
        for transaction in self.service.list_recent(args.limit):
            print(format_transaction(transaction))
            found = True
        if not found:
            print("거래 내역이 없습니다.")
        return 0
