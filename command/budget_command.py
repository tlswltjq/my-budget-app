import argparse

from command.base_command import BaseCommand
from service.budget_service import BudgetService


class BudgetCommand(BaseCommand):
    def __init__(self, service: BudgetService) -> None:
        self.service = service

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest="action", required=True)
        set_parser = subparsers.add_parser("set", help="월 예산 설정")
        set_parser.add_argument("--month", required=True, help="YYYY-MM")
        set_parser.add_argument("--amount", required=True, help="양의 정수")
        show_parser = subparsers.add_parser("show", help="월 예산 조회")
        show_parser.add_argument("--month", required=True, help="YYYY-MM")

    def execute(self, args: argparse.Namespace) -> int:
        if args.action == "set":
            budget = self.service.set(args.month, args.amount)
            print(f"[저장 완료] {budget.month} 예산 {budget.amount.amount}원")
        else:
            budget = self.service.get(args.month)
            if budget is None:
                print(f"[없는 데이터] {args.month} 예산")
            else:
                print(f"{budget.month} 예산: {budget.amount.amount}원")
        return 0
