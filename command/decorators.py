import csv
import sys
from functools import wraps
from typing import Callable


def handle_cli_errors(function: Callable[..., int]) -> Callable[..., int]:
    """CLI 경계에서 오류를 사용자 메시지와 종료 코드로 변환합니다."""

    @wraps(function)
    def wrapper(*args, **kwargs) -> int:
        try:
            return function(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n오류: 작업이 취소되었습니다.", file=sys.stderr)
            return 130
        except (ValueError, OSError, UnicodeError, csv.Error, EOFError, KeyError, TypeError) as error:
            print(f"오류: {error}", file=sys.stderr)
            print("힌트: 입력값과 파일 경로를 확인하고 --help를 참고하세요.", file=sys.stderr)
            return 2
        except Exception as error:
            print(f"오류: 예상하지 못한 문제({type(error).__name__}): {error}", file=sys.stderr)
            print("힌트: 저장 파일 상태를 확인하고 다시 시도하세요.", file=sys.stderr)
            return 1

    return wrapper
