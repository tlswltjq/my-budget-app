import argparse
from typing import Callable

from command.base_command import BaseCommand
from model.transaction import Transaction
from service.transaction_service import TransactionService


class ListCommand(BaseCommand):
    def __init__(self, service: TransactionService, formatter: Callable[[Transaction], str]) -> None:
        self.service = service
        self.formatter = formatter

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=50, help="출력할 최대 거래 수 (기본값: 50)")

    def execute(self, args: argparse.Namespace) -> int:
        # list: 최근 거래를 지정한 개수까지 출력함
        found = False
        for transaction in self.service.list_recent(args.limit):
            print(self.formatter(transaction))
            found = True
        if not found:
            print("거래 내역이 없습니다.")
        return 0
