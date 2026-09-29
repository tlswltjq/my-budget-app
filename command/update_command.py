import argparse
from typing import Callable

from command.base_command import BaseCommand
from service.transaction_service import TransactionService
from service.validation import parse_id


class UpdateCommand(BaseCommand):
    def __init__(self, service: TransactionService, display_id: Callable[[int], str]) -> None:
        self.service = service
        self.display_id = display_id

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", required=True, help="거래 ID (숫자 또는 TX-000001)")
        for name in ("date", "category", "amount", "memo", "tags"):
            parser.add_argument(f"--{name}")
        parser.add_argument("--type", choices=("income", "expense"))

    def execute(self, args: argparse.Namespace) -> int:
        # update: 지정한 거래에서 전달된 필드만 수정함
        transaction_id = parse_id(args.id)
        changes = {
            name: getattr(args, name)
            for name in ("date", "type", "category", "amount", "memo", "tags")
            if getattr(args, name) is not None
        }
        updated = self.service.update(transaction_id, changes)
        if updated is None:
            print(f"[없는 데이터] id={self.display_id(transaction_id)}")
            return 1
        else:
            print(f"[수정 완료] id={self.display_id(updated.id)}")
        return 0
