import argparse
from typing import Callable

from command.base_command import BaseCommand
from service.transaction_service import TransactionService


class AddCommand(BaseCommand):
    def __init__(self, service: TransactionService, display_id: Callable[[int], str]) -> None:
        self.service = service
        self.display_id = display_id

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.description = "거래를 대화형으로 추가합니다. 카테고리를 먼저 등록하세요."

    def execute(self, args: argparse.Namespace) -> int:
        # add: 입력받은 날짜, 타입, 카테고리, 금액 등으로 거래를 등록함
        day = input("날짜(YYYY-MM-DD): ")
        type_name = input("타입(income/expense): ")
        category = input("카테고리: ")
        amount = input("금액(양수): ")
        memo = input("메모(선택): ")
        tags = input("태그(쉼표로 구분, 없으면 엔터): ")
        transaction = self.service.add(day, type_name, category, amount, memo, tags)
        print(f"[저장 완료] id={self.display_id(transaction.id)}")
        return 0
