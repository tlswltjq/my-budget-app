# Budget App

Python 3.10 이상과 표준 라이브러리만 사용하는 CLI 가계부입니다.

프로젝트 루트에서 다음 명령으로 실행합니다.

```bash
python3 budget_app.py
```

모듈 실행도 같은 방식으로 동작합니다.

```bash
python3 -m budget_app
```

기본 저장 폴더는 명령을 실행한 위치의 `./data`입니다.

## 프로젝트 구조

| 경로 | 역할 |
| --- | --- |
| `budget_app.py` | CLI 진입점 |
| `cli.py` | 명령과 서비스 연결, 공통 거래 출력 형식, 인자 파싱 |
| `command/` | 서브 커맨드의 옵션 정의와 콘솔 입출력, 공통 오류 처리 |
| `service/` | 거래·카테고리·예산·요약·CSV 업무 규칙과 입력값 검증 |
| `model/` | 거래, 카테고리, 금액, 메모, 예산의 도메인 모델 |
| `repository/` | JSONL 저장과 조회, 거래 정렬, ID·가져오기 이력 관리 |

첫 데이터 명령을 실행하면 `./data`와 다음 UTF-8 JSONL 파일이 생성됩니다. JSONL은 한 줄에 JSON 객체 하나를 저장합니다. 카테고리는 자동으로 등록되지 않습니다.

| 파일 | 내용 |
| --- | --- |
| `transactions.jsonl` | 거래. 날짜·ID 내림차순 저장 |
| `categories.jsonl` | 등록된 카테고리 |
| `budgets.jsonl` | 월별 예산 |
| `metadata.jsonl` | 다음 거래 ID와 가져온 CSV의 SHA-256 체크섬 |

거래 ID는 화면에 `TX-000001` 형식으로 표시하며 삭제 후에도 재사용하지 않습니다. CSV 가져오기 출처 체크섬은 거래 메모와 별도로 기록합니다.

저장 파일은 임시 파일에 먼저 기록한 뒤 교체합니다. 같은 데이터 폴더에 여러 프로세스가 동시에 쓰는 경우는 지원하지 않습니다.

# 기능별 시나리오

아래 명령은 **프로젝트 루트에서 같은 셸로 위에서 아래 순서대로** 실행합니다. 별도 데이터 경로를 지정하지 않으며 예시 데이터는 모두 `./data`에 저장됩니다.

처음부터 같은 결과를 재현하려면 기존 `./data`가 없는 상태에서 시작해야 합니다. 기존 데이터가 필요한 경우에는 삭제하지 말고 별도 프로젝트 사본에서 실행하세요.

`printf`는 대화형 입력을 순서대로 전달하기 위해 사용합니다. 직접 입력하려면 `printf ... |` 부분을 빼고 실행하면 됩니다.

오류 확인용 명령은 의도적으로 종료 코드 1 또는 2를 반환합니다. 해당 명령 이후에도 다음 명령을 계속 실행하면 됩니다.

## 1. 도움말과 초기 상태

```bash
python3 budget_app.py -h
python3 budget_app.py category -h
python3 budget_app.py category
```

마지막 명령은 하위 명령이 없으므로 카테고리 도움말과 `category -h` 안내를 출력합니다. `budget`에도 `set`, `show` 하위 명령이 있습니다. 각 명령 뒤에 `-h`를 붙이면 해당 옵션을 확인할 수 있습니다.

아직 등록된 카테고리가 없는 상태에서 삭제 동작도 확인합니다.

```bash
python3 budget_app.py category remove
```

이 경우 이름을 묻지 않고 등록된 카테고리가 없다고 안내합니다.

## 2. 카테고리 등록·조회·삭제: `category add/list/remove`

```bash
python3 budget_app.py category list
python3 budget_app.py list
python3 budget_app.py category add --name salary
printf 'food\n' | python3 budget_app.py category add
python3 budget_app.py category add --name transport
python3 budget_app.py category add --name unused
python3 budget_app.py category list
python3 budget_app.py category add --name ''
python3 budget_app.py category add --name food
python3 budget_app.py category remove --name unused
python3 budget_app.py category remove --name unknown
```

첫 `category list`는 빈 카테고리 목록을 출력하고, 첫 거래 `list`는 거래 내역이 없다고 안내합니다.

`category add`에서 `--name`을 생략하면 이름을 입력받습니다. 입력값 양쪽의 공백은 제거한 뒤 저장합니다. 빈 이름이나 이미 등록된 이름은 사용할 수 없습니다.

`remove`는 현재 카테고리 목록을 먼저 보여줍니다. `unused`는 삭제되고, 존재하지 않는 `unknown`은 `[없는 데이터]`와 종료 코드 1을 반환합니다.

거래에서 사용 중인 카테고리의 삭제 제한은 6단계에서 확인합니다.

## 3. 예산 조회·설정: `budget show/set`

```bash
python3 budget_app.py budget -h
python3 budget_app.py budget show --month 2024-01
python3 budget_app.py budget set --month 2024-01 --amount 500000
python3 budget_app.py budget set --month 2024-01 --amount 600000
python3 budget_app.py budget show --month 2024-01
python3 budget_app.py budget set --month 2024-01 --amount 0
python3 budget_app.py budget set --month 2024-13 --amount 100000
```

처음 `show`는 `[없는 데이터]`를 출력합니다. 같은 월에 다시 `set`하면 기존 예산을 교체하므로 2024년 1월 예산은 600000원이 됩니다.

예산은 양의 정수여야 하고 월은 실제 존재하는 `YYYY-MM` 형식이어야 합니다. 따라서 마지막 두 명령은 오류가 납니다.

## 4. 거래 추가: `add`

`add`는 날짜, 타입, 카테고리, 금액을 필수로 입력받고 각 값을 입력한 직후 검증합니다. 메모와 태그는 비워 둘 수 있습니다.

타입은 `income` 또는 `expense`를 사용합니다. 태그가 여러 개라면 쉼표로 구분합니다.

다음 세 명령은 `TX-000001`부터 `TX-000003`까지 거래를 등록합니다.

```bash
printf '2024-01-01\nincome\nsalary\n1000000\n월급\npay,work\n' | python3 budget_app.py add
printf '2024-01-02\nexpense\nfood\n650000\n점심\nmeal,work\n' | python3 budget_app.py add
printf '2024-01-03\nexpense\ntransport\n20000\n\n\n' | python3 budget_app.py add
```

아래 명령은 잘못된 값을 입력한 시점에서 바로 종료됩니다.

```bash
printf '0000-00-00\n' | python3 budget_app.py add
printf '2024-01-04\nin\n' | python3 budget_app.py add
printf '2024-01-04\nexpense\n\n' | python3 budget_app.py add
printf '2024-01-04\nexpense\nunknown\n' | python3 budget_app.py add
printf '2024-01-04\nexpense\nfood\n0\n' | python3 budget_app.py add
printf '2024-01-04\nexpense\nfood\n1000\n\nmeal,\n' | python3 budget_app.py add
```

날짜는 실제 존재하는 날짜여야 하고 카테고리는 미리 등록되어 있어야 합니다. 금액은 양의 정수만 허용합니다. 빈 카테고리와 쉼표 뒤에 값이 없는 태그도 거부합니다.

실패한 명령은 거래를 저장하지 않으며 거래 ID도 소비하지 않습니다.

## 5. 최근 거래와 조건 검색: `list/search`

`list`는 날짜·ID 내림차순으로 최근 거래를 출력합니다. `--limit`의 기본값은 50입니다.

`list`와 `search`는 JSONL을 한 줄씩 순회합니다. `search`에서는 날짜 범위, 카테고리, 타입, 메모 검색어, 태그 조건을 함께 사용할 수 있습니다. 메모 검색은 대소문자를 구분하지 않고 태그는 정확히 일치해야 합니다.

```bash
python3 budget_app.py list --limit 2
python3 budget_app.py search --from 2024-01-01 --to 2024-01-31 --category food --type expense --q 점심 --tag meal
python3 budget_app.py search --q 없는메모
python3 budget_app.py list --limit 0
python3 budget_app.py search --from 2024-02-01 --to 2024-01-01
```

첫 목록에는 `TX-000003`, `TX-000002` 순서로 출력됩니다. 복합 검색 결과는 `TX-000002` 한 건입니다.

검색 결과가 없으면 `검색 결과가 없습니다.`를 출력합니다. `--limit`가 0 이하이거나 시작일이 종료일보다 늦으면 오류입니다.

## 6. 월별 요약과 사용 중인 카테고리: `summary/category remove`

```bash
python3 budget_app.py summary --month 2024-02 --top 2
python3 budget_app.py summary --month 2024-01 --top 2
python3 budget_app.py summary --month 2024-01 --top 0
python3 budget_app.py category remove --name food
```

2월은 거래가 없으므로 `데이터 없음`과 0원 합계를 표시합니다.

1월 결과는 다음과 같습니다.

- 수입: 1000000원
- 지출: 670000원
- 잔액: 330000원
- 지출 상위 카테고리: `food` 650000원, `transport` 20000원
- 예산 600000원 대비 사용률: 111.7%

예산을 초과했으므로 경고도 출력합니다. `--top`은 양수만 허용합니다.

`food`는 거래에서 사용 중이므로 삭제할 수 없으며 카테고리 목록에 그대로 남습니다.

## 7. 거래 수정: `update`

`update`는 `--id`와 하나 이상의 변경 필드를 받습니다.

변경할 수 있는 필드는 `--date`, `--type`, `--category`, `--amount`, `--memo`, `--tags`이며 전달한 필드만 수정합니다. ID는 숫자 또는 `TX-000003` 형식을 사용할 수 있습니다.

```bash
python3 budget_app.py update --id TX-000003 --date 2024-02-01 --type income --category salary --amount 30000 --memo 환급 --tags refund
python3 budget_app.py list --limit 3
python3 budget_app.py summary --month 2024-02 --top 2
printf 'transport\n' | python3 budget_app.py category remove
python3 budget_app.py update --id TX-000002
python3 budget_app.py update --id TX-000002 --category unknown
python3 budget_app.py update --id 999 --amount 1
```

`TX-000003`은 2월 수입 거래로 변경됩니다. 날짜가 바뀌었으므로 목록 순서도 다시 정렬됩니다.

`transport`는 더 이상 거래에서 사용하지 않으므로 삭제할 수 있습니다. `--name`을 생략하면 삭제할 카테고리 이름을 직접 입력합니다.

변경할 필드가 없거나 등록되지 않은 카테고리를 지정하면 오류입니다. 존재하지 않는 ID는 `[없는 데이터]`와 종료 코드 1을 반환합니다.

## 8. 거래 삭제: `delete`

```bash
python3 budget_app.py delete --id 3
python3 budget_app.py delete --id TX-000003
python3 budget_app.py list
```

첫 명령에서 수정했던 거래를 삭제합니다. 두 번째 명령은 같은 ID가 이미 삭제되었으므로 `[없는 데이터]`와 종료 코드 1을 반환합니다.

목록에는 `TX-000001`과 `TX-000002`만 남습니다. 이후 거래를 추가하거나 CSV를 가져와도 삭제된 ID 3은 다시 사용하지 않습니다.

## 9. CSV 내보내기: `export`

`export`는 월 하나 또는 시작일·종료일을 둘 다 받아 해당 거래를 CSV로 저장합니다.

출력 열은 `date,type,category,amount,memo,tags` 순서이며 거래 ID는 포함하지 않습니다. 태그에 쉼표가 들어가면 CSV 규칙에 따라 해당 셀을 인용합니다.

```bash
python3 budget_app.py export --out january.csv --month 2024-01
python3 budget_app.py export --out range.csv --from 2024-01-01 --to 2024-01-31
python3 budget_app.py export --out empty-month.csv --month 2024-03
cat january.csv
python3 budget_app.py export --out invalid.csv --month 2024-01 --from 2024-01-01 --to 2024-01-31
python3 budget_app.py export --out invalid.csv --from 2024-01-01
python3 budget_app.py export --out invalid.csv --from 2024-02-01 --to 2024-01-01
python3 budget_app.py export --out data/categories.jsonl --month 2024-01
```

앞의 두 내보내기는 각각 거래 2건을 기록합니다. 거래가 없는 3월은 헤더만 있는 CSV를 만들고 0건을 출력합니다.

다음 경우에는 내보내기를 거부합니다.

- 월과 날짜 범위를 동시에 지정한 경우
- 시작일 또는 종료일만 지정한 경우
- 시작일이 종료일보다 늦은 경우
- 앱에서 사용하는 JSONL 저장 파일을 출력 경로로 지정한 경우

## 10. CSV 가져오기: `import`

`import`는 UTF-8 CSV의 모든 행을 먼저 검증한 뒤 거래를 추가합니다.

`date`, `type`, `category`, `amount` 헤더는 필수이고 `memo`, `tags`는 선택입니다. CSV에 `id` 열이 있어도 해당 값은 사용하지 않고 새 거래 ID를 발급합니다.

등록되지 않은 카테고리나 잘못된 행·헤더가 하나라도 있으면 해당 파일의 거래는 하나도 가져오지 않습니다.

```bash
cat > invalid-import.csv <<'CSV'
date,type,category,amount,memo,tags
2024-01-05,expense,food,5000,간식,snack
2024-01-06,expense,unknown,3000,기타,
CSV

python3 budget_app.py import --from invalid-import.csv
python3 budget_app.py list

printf 'date,type,amount\n2024-01-05,expense,5000\n' > missing-header.csv
python3 budget_app.py import --from missing-header.csv
```

첫 가져오기는 CSV 3행의 `unknown` 카테고리가 등록되어 있지 않아 실패합니다. 앞의 정상 행도 저장되지 않으므로 거래 목록은 여전히 2건입니다.

두 번째 파일은 필수 `category` 헤더가 없어 실패합니다.

정상 가져오기와 중복 파일 처리는 다음과 같이 확인합니다.

```bash
python3 budget_app.py import --from january.csv
python3 budget_app.py import --from january.csv

cat > optional-columns.csv <<'CSV'
date,type,category,amount,id
2024-01-05,expense,food,5000,999
CSV

python3 budget_app.py import --from optional-columns.csv
python3 budget_app.py list --limit 6
```

첫 `january.csv` 가져오기는 2건을 추가합니다. 삭제된 `TX-000003`은 재사용하지 않으므로 새 거래에는 `TX-000004`, `TX-000005`가 발급됩니다.

같은 파일을 다시 가져오면 체크섬이 같으므로 `imported=0, skipped=2`가 출력됩니다.

`optional-columns.csv`는 `memo`, `tags`가 없어도 정상적으로 1건을 가져옵니다. CSV의 `id=999`는 무시하고 새 ID인 `TX-000006`을 사용합니다.

중복 파일은 파일명이 아니라 **파일 내용의 SHA-256 체크섬**으로 판단합니다. CSV 내용을 변경하면 새 파일로 취급하며 파일의 전체 행을 다시 가져옵니다.
