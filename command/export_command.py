import argparse

from command.base_command import BaseCommand
from service.csv_service import ExportService


class ExportCommand(BaseCommand):
    def __init__(self, service: ExportService) -> None:
        self.service = service

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--out", required=True, help="CSV 출력 경로")
        parser.add_argument("--month", help="YYYY-MM")
        parser.add_argument("--from", dest="from_day", help="시작일 YYYY-MM-DD")
        parser.add_argument("--to", dest="to_day", help="종료일 YYYY-MM-DD")

    def execute(self, args: argparse.Namespace) -> int:
        # export: 선택한 기간의 거래를 CSV 파일로 내보냄
        count = self.service.export_csv(args.out, args.month, args.from_day, args.to_day)
        print(f"[완료] {args.out} ({count} records)")
        return 0
