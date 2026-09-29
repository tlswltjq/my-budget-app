import argparse
from typing import Callable

from command.base_command import BaseCommand
from model.transaction import Transaction
from service.transaction_service import SearchFilters, TransactionService
from service.validation import parse_day


class SearchCommand(BaseCommand):
    def __init__(self, service: TransactionService, formatter: Callable[[Transaction], str]) -> None:
        self.service = service
        self.formatter = formatter

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--from", dest="from_day", help="시작일 YYYY-MM-DD")
        parser.add_argument("--to", dest="to_day", help="종료일 YYYY-MM-DD")
        parser.add_argument("--category", help="카테고리명")
        parser.add_argument("--type", choices=("income", "expense"), help="거래 타입")
        parser.add_argument("--q", help="메모 검색어")
        parser.add_argument("--tag", help="태그")

    def execute(self, args: argparse.Namespace) -> int:
        filters = SearchFilters(
            from_date=parse_day(args.from_day) if args.from_day else None,
            to_date=parse_day(args.to_day) if args.to_day else None,
            category=args.category,
            type=args.type,
            query=args.q,
            tag=args.tag,
        )
        found = False
        for transaction in self.service.search(filters):
            print(self.formatter(transaction))
            found = True
        if not found:
            print("검색 결과가 없습니다.")
        return 0
