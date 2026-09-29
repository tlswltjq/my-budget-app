import argparse

from command.base_command import BaseCommand
from service.summary_service import SummaryService


class SummaryCommand(BaseCommand):
    def __init__(self, service: SummaryService) -> None:
        self.service = service

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--month", required=True, help="YYYY-MM")
        parser.add_argument("--top", type=int, default=3, help="지출 상위 카테고리 수 (기본값: 3)")

    def execute(self, args: argparse.Namespace) -> int:
        # summary: 월별 수입, 지출, 예산, 상위 지출 카테고리를 출력함
        summary = self.service.monthly(args.month, args.top)
        if summary.count == 0:
            print("데이터 없음")
        print(f"총 수입: {summary.income}원")
        print(f"총 지출: {summary.expense}원")
        print(f"잔액: {summary.balance}원")
        if summary.budget:
            print(f"예산: {summary.budget.amount.amount}원 (사용률 {summary.usage_percent:.1f}%)")
            if summary.expense > summary.budget.amount.amount:
                print("[경고] 월 예산을 초과했습니다.")
        print(f"\n지출 TOP {args.top}")
        for rank, (category, amount) in enumerate(summary.top_categories, start=1):
            print(f"{rank}) {category} {amount}원")
        return 0
