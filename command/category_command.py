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
        # category: 등록, 목록 조회, 삭제 명령을 처리함
        if args.action == "add":
            # category add: 이름을 받아 새 카테고리를 등록함
            category = self.service.add(args.name if args.name is not None else input("카테고리명: "))
            print(f"[저장 완료] category={category.name}")
        elif args.action == "list":
            # category list: 등록된 카테고리 목록을 출력함
            categories = self.service.list()
            if categories:
                for category in categories:
                    print(f"- {category.name}")
            else:
                print("등록된 카테고리가 없습니다. category add로 등록하세요.")
        else:
            # category remove: 현재 목록을 보여주고 선택한 카테고리를 삭제함
            categories = self.service.list()
            if not categories:
                print("등록된 카테고리가 없습니다. category add로 등록하세요.")
                return 1
            print("현재 등록된 카테고리:")
            for category in categories:
                print(f"- {category.name}")
            # --name 옵션 값이 전달되었으면 그 값을 사용하고, 생략되었으면 사용자에게 직접 입력받음
            name = args.name if args.name is not None else input("삭제할 카테고리명: ")
            if self.service.remove(name):
                print(f"[삭제 완료] category={name.strip()}")
            else:
                print(f"[없는 데이터] category={name.strip()}")
                return 1
        return 0
