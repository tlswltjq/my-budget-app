from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from command.add_command import AddCommand
from command.budget_command import BudgetCommand
from command.category_command import CategoryCommand
from command.decorators import handle_cli_errors
from command.delete_command import DeleteCommand
from command.export_command import ExportCommand
from command.import_command import ImportCommand
from command.list_command import ListCommand
from command.search_command import SearchCommand
from command.summary_command import SummaryCommand
from command.update_command import UpdateCommand
from model.transaction import Transaction
from repository.budget_repository import BudgetRepository
from repository.category_repository import CategoryRepository
from repository.metadata_repository import MetadataRepository
from repository.transaction_repository import TransactionRepository
from service.budget_service import BudgetService
from service.category_service import CategoryService
from service.csv_service import ExportService, ImportService
from service.summary_service import SummaryService
from service.transaction_service import TransactionService

DEFAULT_DATA_DIR = "./data"


def display_id(transaction_id: int) -> str:
    return f"TX-{transaction_id:06d}"


def format_transaction(transaction: Transaction) -> str:
    return (
        f"{display_id(transaction.id)} | {transaction.date.isoformat()} | "
        f"{transaction.type.name:<7} | {transaction.category.name} | "
        f"{transaction.amount.amount} | {transaction.memo.content}"
    )


COMMANDS = (
    ("add", AddCommand, "거래 추가"),
    ("list", ListCommand, "최근 거래 목록"),
    ("search", SearchCommand, "거래 검색"),
    ("summary", SummaryCommand, "월별 요약"),
    ("budget", BudgetCommand, "예산 관리"),
    ("category", CategoryCommand, "카테고리 관리"),
    ("update", UpdateCommand, "거래 수정"),
    ("delete", DeleteCommand, "거래 삭제"),
    ("import", ImportCommand, "CSV 가져오기"),
    ("export", ExportCommand, "CSV 내보내기"),
)


class CommandArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        if getattr(self, "show_help_on_error", False):
            self.print_help(sys.stderr)
            self.exit(2, f"\n{self.prog}: error: {message}\n힌트: python3 {self.prog} -h\n")
        super().error(message)


@handle_cli_errors
def main(argv: Sequence[str] | None = None) -> int:
    parser = CommandArgumentParser(description="파일 기반 가계부")
    parser.add_argument(
        "--data-dir",
        default=DEFAULT_DATA_DIR,
        help=f"JSONL 저장 폴더 (기본값: {DEFAULT_DATA_DIR})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, command_class, help_text in COMMANDS:
        command_parser = subparsers.add_parser(name, help=help_text)
        command_class.configure_parser(command_parser)
        if name == "category":
            category_parser = command_parser
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        error_parser = category_parser if args.command == "category" else parser
        error_parser.error(f"unrecognized arguments: {' '.join(unknown)}")

    data_dir = Path(args.data_dir)
    transaction_path = data_dir / "transactions.jsonl"
    category_path = data_dir / "categories.jsonl"
    budget_path = data_dir / "budgets.jsonl"
    metadata_path = data_dir / "metadata.jsonl"
    transactions = TransactionRepository(str(transaction_path))
    categories = CategoryRepository(str(category_path))
    budgets = BudgetRepository(str(budget_path))
    metadata = MetadataRepository(str(metadata_path))

    transaction_service = TransactionService(transactions, categories, metadata)
    budget_service = BudgetService(budgets)
    commands = {
        "add": AddCommand(transaction_service, display_id),
        "list": ListCommand(transaction_service, format_transaction),
        "search": SearchCommand(transaction_service, format_transaction),
        "summary": SummaryCommand(SummaryService(transactions, budget_service)),
        "budget": BudgetCommand(budget_service),
        "category": CategoryCommand(CategoryService(categories, transactions)),
        "update": UpdateCommand(transaction_service, display_id),
        "delete": DeleteCommand(transaction_service, display_id),
        "import": ImportCommand(ImportService(transactions, categories, metadata)),
        "export": ExportCommand(ExportService(
            transactions, [transaction_path, category_path, budget_path, metadata_path]
        )),
    }
    return commands[args.command].execute(args)
