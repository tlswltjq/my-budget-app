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
        # budget: 월 예산 설정 또는 조회 명령을 처리함
        if args.action == "set":
            # budget set: 해당 월의 예산을 저장함
            budget = self.service.set(args.month, args.amount)
            print(f"[저장 완료] {budget.month} 예산 {budget.amount.amount}원")
        else:
            # budget show: 해당 월의 예산을 조회해 출력함
            budget = self.service.get(args.month)
            if budget is None:
                print(f"[없는 데이터] {args.month} 예산")
            else:
                print(f"{budget.month} 예산: {budget.amount.amount}원")
        return 0
