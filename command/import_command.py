import argparse

from command.base_command import BaseCommand
from service.csv_service import ImportService


class ImportCommand(BaseCommand):
    def __init__(self, service: ImportService) -> None:
        self.service = service

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--from", dest="from_path", required=True, help="UTF-8 CSV 경로")

    def execute(self, args: argparse.Namespace) -> int:
        result = self.service.import_csv(args.from_path)
        if result.duplicate_file:
            print("[이미 가져온 파일] 체크섬이 동일합니다.")
        print(f"[완료] imported={result.imported}, skipped={result.skipped}")
        return 0
