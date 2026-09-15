import argparse
from datetime import datetime, date
import command

def handle_add(args):
    print("[거래 추가]", args)

def handle_list(args):
    print(f"[거래 목록] limit: {args.limit}")

def handle_search(args):
    print(f"[거래 검색] 키워드: {args.q}, 기간: {args.from_date} ~ {args.to_date}, 카테고리: {args.category}, 유형: {args.type}, 태그: {args.tag}")

def handle_summary(args):
    print(f"[요약/통계] 월: {args.month}, Top: {args.top}")

def handle_budget(args):
    print(f"[예산 설정] 액션: {args.action}, 월: {args.month}")

def handle_category(args):
    print(f"[카테고리 관리] 액션: {args.action}")
    print(command.get_categories(args.action))

def handle_import(args):
    print(f"[데이터 임포트] 출처: {args.from_path}")

def handle_export(args):
    print(f"[데이터 내보내기] 대상: {args.to_path}")

def handle_backup(args):
    print("[백업 실행]")

def handle_update(args):
    print(f"[거래 수정] ID: {args.id}")

def handle_delete(args):
    print(f"[거래 삭제] ID: {args.id}")

def parse_date(date_str):
    """YYYY-MM-DD 또는 YYYY-MM 형식을 date 객체로 변환하는 도우미 함수"""
    try:
        if len(date_str) == 7:
            return datetime.strptime(date_str, "%Y-%m").date()
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"날짜 형식이 올바르지 않습니다: '{date_str}' (YYYY-MM 또는 YYYY-MM-DD 권장)")


def main():
    parser = argparse.ArgumentParser(description="용돈 기입장 프로그램")
    subparsers = parser.add_subparsers(dest="command", required=True, help="사용할 명령어")

    # --- add ---
    parser_add = subparsers.add_parser("add", help="거래 추가")
    parser_add.set_defaults(func=handle_add)

    # --- list ---
    parser_list = subparsers.add_parser("list", help="거래 목록(최신순)")
    parser_list.add_argument("--limit", type=int, default=50, help="출력할 행 수")
    parser_list.set_defaults(func=handle_list)

    # --- search ---
    parser_search = subparsers.add_parser("search", help="조건에 맞는 거래 목록(최신순)")
    parser_search.add_argument("--from", dest="from_date", type=str, help="시작일 (YYYY-MM-DD)")
    parser_search.add_argument("--to", dest="to_date", type=str, help="종료일 (YYYY-MM-DD)")
    parser_search.add_argument("--category", type=str, help="카테고리명")
    parser_search.add_argument("--type", type=str, choices=["income", "expense"], help="입/출금 유형")
    parser_search.add_argument("--q", type=str, help="메모 키워드")
    parser_search.add_argument("--tag", type=str, help="태그")
    parser_search.set_defaults(func=handle_search)

    # --- summary ---
    parser_summary = subparsers.add_parser("summary", help="수입/지출/잔액 요약 및 통계")
    parser_summary.add_argument("--month", type=parse_date, help="YYYY-MM 해당 월 수입/지출/잔액")
    parser_summary.add_argument("--top", type=int, help="N, 카테고리별 지출 TOP N")
    parser_summary.set_defaults(func=handle_summary)

    # --- budget ---
    parser_budget = subparsers.add_parser("budget", help="예산 설정 및 관리")
    parser_budget.add_argument("action", type=str, help="예산 동작 (예: set, show)")
    parser_budget.add_argument("--month", type=parse_date, required=True, help="YYYY-MM")
    parser_budget.set_defaults(func=handle_budget)

    # --- category ---
    parser_category = subparsers.add_parser("category", help="카테고리 관리")
    parser_category.add_argument("action", choices=["add", "remove", "list"], help="수행할 작업")
    parser_category.set_defaults(func=handle_category)

    # --- import ---
    parser_import = subparsers.add_parser("import", help="데이터 불러오기")
    parser_import.add_argument("--from", dest="from_path", required=True, help="가져올 파일 경로")
    parser_import.set_defaults(func=handle_import)

    # --- export ---
    parser_export = subparsers.add_parser("export", help="데이터 내보내기")
    parser_export.add_argument("--to", dest="to_path", required=True, help="내보낼 파일 경로")
    parser_export.set_defaults(func=handle_export)

    # --- backup ---
    parser_backup = subparsers.add_parser("backup", help="데이터 백업")
    parser_backup.set_defaults(func=handle_backup)

    # --- update ---
    parser_update = subparsers.add_parser("update", help="거래 내역 수정")
    parser_update.add_argument("id", type=int, help="수정할 거래 ID")
    parser_update.set_defaults(func=handle_update)

    # --- delete ---
    parser_delete = subparsers.add_parser("delete", help="거래 내역 삭제")
    parser_delete.add_argument("id", type=int, help="삭제할 거래 ID")
    parser_delete.set_defaults(func=handle_delete)

    # 파싱 수행
    args = parser.parse_args()

    # 분기문(if/elif/else) 없이 매핑된 함수 바로 호출
    args.func(args)


if __name__ == "__main__":
    main()