import argparse

from command.base_command import BaseCommand
from service.category_service import CategoryService


class CategoryCommand(BaseCommand):
    def __init__(self, service: CategoryService) -> None:
        self.service = service

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest="action", required=True)
        add_parser = subparsers.add_parser("add", help="카테고리 추가")
        add_parser.add_argument("--name", help="카테고리명 (생략하면 입력)")
        subparsers.add_parser("list", help="카테고리 목록")
        remove_parser = subparsers.add_parser("remove", help="카테고리 삭제")
        remove_parser.add_argument("--name", help="삭제할 카테고리명 (생략하면 입력)")

    def execute(self, args: argparse.Namespace) -> int:
        if args.action == "add":
            category = self.service.add(args.name if args.name is not None else input("카테고리명: "))
            print(f"[저장 완료] category={category.name}")
        elif args.action == "list":
            categories = self.service.list()
            if categories:
                for category in categories:
                    print(f"- {category.name}")
            else:
                print("등록된 카테고리가 없습니다. category add로 등록하세요.")
        else:
            name = args.name if args.name is not None else input("삭제할 카테고리명: ")
            if self.service.remove(name):
                print(f"[삭제 완료] category={name.strip()}")
            else:
                print(f"[없는 데이터] category={name.strip()}")
                return 1
        return 0
