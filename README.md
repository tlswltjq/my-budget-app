# 프로젝트 구조

Python 3.10 이상과 표준 라이브러리만 사용합니다. 프로젝트 루트에서 `python3 budget_app.py`로 실행합니다. `python3 -m budget_app`도 같은 명령을 실행합니다. 기본 저장 폴더는 실행한 위치의 `./data`입니다.

| 경로 | 역할 |
| --- | --- |
| `budget_app.py` | CLI 진입점 |
| `cli.py` | 명령과 서비스 연결, 공통 거래 출력 형식, 인자 파싱 |
| `command/` | 서브 커맨드의 옵션 정의와 콘솔 입출력, 공통 오류 처리 |
| `service/` | 거래·카테고리·예산·요약·CSV 업무 규칙과 입력값 검증 |
| `model/` | 거래, 카테고리, 금액, 메모, 예산의 도메인 모델 |
| `repository/` | JSONL 저장과 조회, 거래 정렬, ID·가져오기 이력 관리 |

첫 데이터 명령을 실행하면 저장 폴더와 아래 UTF-8 JSONL 파일이 생성됩니다. JSONL은 한 줄에 JSON 객체 하나를 저장합니다. 카테고리는 자동으로 등록되지 않습니다.

| 파일 | 내용 |
| --- | --- |
| `transactions.jsonl` | 거래. 날짜·ID 내림차순 저장 |
| `categories.jsonl` | 등록된 카테고리 |
| `budgets.jsonl` | 월별 예산 |
| `metadata.jsonl` | 다음 거래 ID와 가져온 CSV의 SHA-256 체크섬 |

거래 ID는 화면에 `TX-000001` 형식으로 표시하며 삭제 후에도 재사용하지 않습니다. CSV 가져오기 출처 체크섬은 거래 메모와 별도로 기록합니다. 저장 파일은 임시 파일에 기록한 뒤 교체합니다. 같은 데이터 폴더에 여러 프로세스가 동시에 쓰는 경우는 지원하지 않습니다.

# 기능별 시나리오

아래 명령은 **프로젝트 루트에서 시작해 같은 셸에서 위에서 아래로** 실행합니다. 처음에 실행에 필요한 파일을 임시 폴더로 복사하고 그곳으로 이동하므로 기존 `./data`를 건드리지 않습니다. 예시의 데이터는 임시 폴더 안의 `data/`에 저장됩니다. `printf`는 대화형 입력에 답을 순서대로 전달합니다. 직접 입력하려면 `printf ... |` 부분을 빼고 실행하면 됩니다. 오류를 확인하는 명령은 의도적으로 종료 코드 1 또는 2를 반환하므로 다음 명령을 계속 실행하세요.

## 1. 도움말과 데이터 폴더

```bash
DEMO_DIR=$(mktemp -d)
cp -R budget_app.py cli.py command model repository service "$DEMO_DIR/"
cd "$DEMO_DIR"
python3 budget_app.py -h
python3 budget_app.py category -h
python3 budget_app.py category
```

마지막 명령은 하위 명령이 없어 카테고리 도움말과 `category -h` 안내를 출력합니다. `budget`에도 `set`, `show` 하위 명령이 있습니다. 각 명령 뒤에 `-h`를 붙이면 해당 옵션을 볼 수 있습니다.

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

첫 `category list`는 빈 카테고리 목록을, 첫 거래 `list`는 거래 내역이 없음을 안내합니다. `category add`는 `--name`을 생략하면 이름을 묻고, 양쪽 공백을 제거해 저장합니다. 이름이 비어 있거나 이미 등록된 `food`를 다시 추가하면 오류가 납니다. `remove`는 현재 목록을 먼저 보여줍니다. `unused`는 삭제되지만 `unknown`은 `[없는 데이터]`와 종료 코드 1을 반환합니다. 목록 자체가 비어 있는 삭제 동작은 별도 빈 폴더로 확인할 수 있습니다.

```bash
mkdir "$DEMO_DIR/empty"
cp -R budget_app.py cli.py command model repository service "$DEMO_DIR/empty/"
(cd "$DEMO_DIR/empty" && python3 budget_app.py category remove)
```

이 경우 이름을 묻지 않고 등록된 카테고리가 없다고 안내합니다. 거래에서 사용 중인 카테고리의 삭제 제한은 6단계에서 확인합니다.

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

처음 `show`는 `[없는 데이터]`를 출력합니다. 같은 월에 다시 `set`하면 예산이 600000원으로 교체됩니다. 예산은 양의 정수이고 월은 존재하는 `YYYY-MM`이어야 하므로 마지막 두 설정은 거부됩니다.

## 4. 거래 추가: `add`

`add`는 날짜, 타입, 카테고리, 금액을 **필수**로 묻고 입력 직후 검증합니다. 메모와 태그는 비워 둘 수 있습니다. 타입은 `income` 또는 `expense`이며, 여러 태그는 쉼표로 구분합니다. 다음 세 명령은 차례로 `TX-000001`부터 `TX-000003`까지 등록합니다.

```bash
printf '2024-01-01\nincome\nsalary\n1000000\n월급\npay,work\n' | python3 budget_app.py add
printf '2024-01-02\nexpense\nfood\n650000\n점심\nmeal,work\n' | python3 budget_app.py add
printf '2024-01-03\nexpense\ntransport\n20000\n\n\n' | python3 budget_app.py add
```

아래는 입력이 잘못된 시점에서 바로 멈춥니다. 날짜는 실제 존재해야 하고, 카테고리는 미리 등록되어 있어야 하며, 금액은 양의 정수여야 합니다. 빈 카테고리와 쉼표 뒤에 값이 없는 태그도 거부됩니다. 이 명령들로 거래나 ID가 추가되지 않습니다.

```bash
printf '0000-00-00\n' | python3 budget_app.py add
printf '2024-01-04\nin\n' | python3 budget_app.py add
printf '2024-01-04\nexpense\n\n' | python3 budget_app.py add
printf '2024-01-04\nexpense\nunknown\n' | python3 budget_app.py add
printf '2024-01-04\nexpense\nfood\n0\n' | python3 budget_app.py add
printf '2024-01-04\nexpense\nfood\n1000\n\nmeal,\n' | python3 budget_app.py add
```

## 5. 최근 거래와 조건 검색: `list/search`

`list`는 날짜·ID 내림차순의 최근 거래를 출력하며 `--limit` 기본값은 50입니다. `list`와 `search`는 JSONL을 한 줄씩 순회합니다. `search`는 날짜 범위, 카테고리, 타입, 메모 검색어, 태그를 함께 적용합니다. 메모는 대소문자를 구분하지 않고, 태그는 이름이 정확히 일치해야 합니다.

```bash
python3 budget_app.py list --limit 2
python3 budget_app.py search --from 2024-01-01 --to 2024-01-31 --category food --type expense --q 점심 --tag meal
python3 budget_app.py search --q 없는메모
python3 budget_app.py list --limit 0
python3 budget_app.py search --from 2024-02-01 --to 2024-01-01
```

첫 목록은 `TX-000003`, `TX-000002` 순서이고 복합 검색은 `TX-000002`만 찾습니다. 결과가 없는 검색은 `검색 결과가 없습니다.`를 출력합니다. `--limit`가 0 이하이거나 시작일이 종료일보다 늦으면 오류입니다.

## 6. 월별 요약과 사용 중인 카테고리: `summary/category remove`

```bash
python3 budget_app.py summary --month 2024-02 --top 2
python3 budget_app.py summary --month 2024-01 --top 2
python3 budget_app.py summary --month 2024-01 --top 0
python3 budget_app.py category remove --name food
```

2월은 거래가 없어 `데이터 없음`과 0원 합계를 표시합니다. 1월은 수입 1000000원, 지출 670000원, 잔액 330000원입니다. 지출 상위 카테고리는 `food` 650000원과 `transport` 20000원이고, 예산 600000원 대비 사용률 111.7%와 초과 경고가 나옵니다. `--top`은 양수여야 합니다. `food`는 거래에서 사용 중이므로 삭제되지 않고 카테고리 목록에 남습니다.

## 7. 거래 수정: `update`

`update`는 `--id`와 변경할 필드 하나 이상을 받습니다. `--date`, `--type`, `--category`, `--amount`, `--memo`, `--tags` 중 전달한 필드만 수정합니다. ID는 숫자 또는 `TX-000003` 형식을 사용할 수 있습니다.

```bash
python3 budget_app.py update --id TX-000003 --date 2024-02-01 --type income --category salary --amount 30000 --memo 환급 --tags refund
python3 budget_app.py list --limit 3
python3 budget_app.py summary --month 2024-02 --top 2
printf 'transport\n' | python3 budget_app.py category remove
python3 budget_app.py update --id TX-000002
python3 budget_app.py update --id TX-000002 --category unknown
python3 budget_app.py update --id 999 --amount 1
```

`TX-000003`은 2월 수입으로 바뀌고 새 날짜에 맞춰 목록 순서가 바뀝니다. `transport`는 더 이상 거래에서 쓰이지 않아 삭제할 수 있습니다. 삭제 명령에서 `--name`을 생략하면 이름을 직접 입력합니다. 수정 필드가 없거나 미등록 카테고리를 지정하면 오류이며, 없는 ID는 `[없는 데이터]`와 종료 코드 1을 반환합니다.

## 8. 거래 삭제: `delete`

```bash
python3 budget_app.py delete --id 3
python3 budget_app.py delete --id TX-000003
python3 budget_app.py list
```

첫 명령은 수정했던 거래를 삭제합니다. 두 번째 명령은 같은 ID가 더는 없어 `[없는 데이터]`와 종료 코드 1을 반환합니다. 목록에는 `TX-000001`과 `TX-000002`만 남습니다. 다음에 거래를 추가하거나 CSV를 가져와도 삭제한 ID 3은 다시 사용하지 않습니다.

## 9. CSV 내보내기: `export`

`export`는 월 하나 또는 시작일·종료일을 **둘 다** 받아 해당 거래를 CSV로 씁니다. 출력 열은 `date,type,category,amount,memo,tags` 순서이며 거래 ID는 포함하지 않습니다. 태그에 쉼표가 있으면 CSV 규칙에 따라 셀을 인용합니다.

```bash
python3 budget_app.py export --out "$DEMO_DIR/january.csv" --month 2024-01
python3 budget_app.py export --out "$DEMO_DIR/range.csv" --from 2024-01-01 --to 2024-01-31
python3 budget_app.py export --out "$DEMO_DIR/empty-month.csv" --month 2024-03
cat "$DEMO_DIR/january.csv"
python3 budget_app.py export --out "$DEMO_DIR/invalid.csv" --month 2024-01 --from 2024-01-01 --to 2024-01-31
python3 budget_app.py export --out "$DEMO_DIR/invalid.csv" --from 2024-01-01
python3 budget_app.py export --out "$DEMO_DIR/invalid.csv" --from 2024-02-01 --to 2024-01-01
python3 budget_app.py export --out "$DEMO_DIR/data/categories.jsonl" --month 2024-01
```

앞의 두 내보내기는 각각 거래 2건을 기록합니다. 거래가 없는 3월은 헤더만 있는 CSV를 만들고 0건을 출력합니다. 월과 날짜 범위를 동시에 지정하거나, 날짜 경계를 하나만 주거나, 시작일을 종료일보다 늦게 주면 거부됩니다. 앱의 JSONL 저장 파일을 출력 경로로 지정해 덮어쓰는 것도 거부됩니다.

## 10. CSV 가져오기: `import`

`import`는 UTF-8 CSV의 모든 행을 먼저 검증한 후 거래를 추가합니다. `date,type,category,amount` 헤더가 필수이고 `memo,tags`는 선택입니다. CSV의 `id` 열은 무시하고 새 거래 ID를 발급합니다. 등록되지 않은 카테고리, 잘못된 행 또는 헤더가 있으면 그 파일의 거래는 하나도 가져오지 않습니다.

```bash
cat > "$DEMO_DIR/invalid-import.csv" <<'CSV'
date,type,category,amount,memo,tags
2024-01-05,expense,food,5000,간식,snack
2024-01-06,expense,unknown,3000,기타,
CSV
python3 budget_app.py import --from "$DEMO_DIR/invalid-import.csv"
python3 budget_app.py list
printf 'date,type,amount\n2024-01-05,expense,5000\n' > "$DEMO_DIR/missing-header.csv"
python3 budget_app.py import --from "$DEMO_DIR/missing-header.csv"
```

첫 가져오기는 CSV 3행의 미등록 카테고리 때문에 실패합니다. 앞의 정상 행도 저장되지 않아 목록은 여전히 2건입니다. 두 번째 가져오기는 필수 `category` 헤더가 없어 실패합니다.

```bash
python3 budget_app.py import --from "$DEMO_DIR/january.csv"
python3 budget_app.py import --from "$DEMO_DIR/january.csv"
cat > "$DEMO_DIR/optional-columns.csv" <<'CSV'
date,type,category,amount,id
2024-01-05,expense,food,5000,999
CSV
python3 budget_app.py import --from "$DEMO_DIR/optional-columns.csv"
python3 budget_app.py list --limit 6
```

첫 `january.csv` 가져오기는 2건을 추가해 삭제된 `TX-000003` 다음 ID인 `TX-000004`와 `TX-000005`를 사용합니다. 동일한 파일을 다시 가져오면 체크섬이 같아 `imported=0, skipped=2`가 나옵니다. 마지막 CSV는 메모·태그 없이도 1건을 가져오며, `id=999` 대신 새 ID `TX-000006`을 사용합니다. 중복 판단은 파일명이 아닌 **파일 내용의 SHA-256** 기준입니다. 내용을 바꾼 CSV는 새 파일로 취급해 그 파일의 전체 행을 다시 가져옵니다.
