# ft_ls

파일 metadata와 디렉터리 순회를 직접 다루기 위해 만든 `ls` 구현입니다.
GNU `ls`의 전체 기능이 아니라 디렉터리 중심의 `-lRart` 옵션 범위를 구현했습니다.

## 만든 이유

`readdir`, `lstat`, permission bit, symlink, timestamp가 실제 목록 출력으로 이어지는 과정을
이해하고 싶었습니다. GNU 문서에서 각 metadata의 의미를 해석하고, 재귀 순회 중 생성한
노드의 수명과 해제 순서를 설계하는 일이 핵심 과제였습니다.

## 핵심 기능

- 인자가 없으면 현재 디렉터리(`.`), 인자가 있으면 여러 디렉터리를 순서대로 처리
- `-l`, `-R`, `-a`, `-r`, `-t` short option을 bitmask로 파싱하고 결합·반복 표기를 수용
- `opendir`/`readdir`로 entry를 모은 뒤 숨김 필터와 이름·mtime 정렬 적용
- `lstat`으로 mode, link count, owner/group, size, mtime 수집
- `readlink`로 valid/broken symbolic link의 target 표시
- `next`/`child` 연결 구조로 sibling entry와 재귀 디렉터리 표현

regular-file operand와 `--`, GNU의 나머지 옵션 및 terminal column layout은 현재 범위에
포함하지 않습니다.

## 동작 구조

```text
CLI option/directory parsing
  -> opendir + readdir
  -> next-linked entry list
  -> hidden filter -> sort -> optional lstat/format
  -> print current directory
  -> child-linked recursive traversal (-R)
  -> recursive cleanup
```

디렉터리 entry를 바로 출력하지 않고 먼저 모두 수집한 뒤 가공합니다. `t_list_ls.next`는
같은 디렉터리의 entry를, `child`는 재귀로 읽은 하위 디렉터리를 가리킵니다. `-l`, `-R`,
`-t` 중 하나가 있을 때만 정렬·순회에 필요한 metadata를 수집합니다.

## 설계하면서 고민한 점

- 수집과 출력을 분리하면 숨김 필터, 정렬, column width 계산을 출력 전에 적용할 수 있어
  `collect → transform → output` 구조를 선택했습니다.
- 모든 데이터를 배열이나 memory pool에 넣는 방식도 고려했지만, 현재 구현은
  sibling과 child ownership을 한 node type으로 표현하는 연결 구조를 사용합니다.
- 재귀 호출과 할당·해제 경로 때문에 memory lifetime과 효율을 판단하기 어려웠습니다.
  다시 설계한다면 recursion과 자료구조를 먼저 검토하고 싶다는 회고가 남아 있습니다.
- 성능 benchmark는 수행하지 않았으므로 현재 구조가 느리거나 개선안이 더 빠르다고 주장하지 않습니다.

## Build

```bash
make
```

루트의 `makefile`이 `libft`와 `printf`를 함께 빌드하며, 실행 파일 `./ft_ls`를 생성합니다.

## Run

```bash
./ft_ls
./ft_ls -la .
./ft_ls -R path/to/directory
./ft_ls -tr dir1 dir2
```

- `-l`: long format metadata 출력
- `-R`: 하위 디렉터리 재귀 순회
- `-a`: `.`으로 시작하는 entry 포함
- `-r`: 선택한 정렬의 역순 출력
- `-t`: mtime 기준 최신 항목부터 정렬

입력 operand는 디렉터리를 전제로 합니다. regular file을 직접 넘기는 사용법은 지원하지 않습니다.

## 검증 결과

| 범위 | 결과 |
|---|---|
| 비교 기준 | GNU coreutils `ls` 9.4 |
| 실행 case | 25 |
| 분류 | PASS 16 · PARTIAL 1 · FAIL 8 · CRASH 0 |
| 대표 관찰 | 기본 long metadata, valid/broken symlink, 2-level·hidden 재귀 traversal case 일치 |

비교는 `LC_ALL=C`, `TZ=UTC0`, non-TTY 환경에서 수행했습니다. 전체 case와 raw 근거는
[`portfolio_audit/test_results.md`](portfolio_audit/test_results.md)에 있습니다.

## 확인된 한계

- mtime이 같은 entry에서 GNU의 name tie-break를 적용하지 않아 출력 순서가 달라집니다.
- setuid/setgid/sticky bit 표기가 빠지며 FIFO 타입 문자를 `p`가 아닌 `P`로 출력합니다.
- regular-file operand 미지원은 의도한 범위 제한입니다. 또한 존재하지 않는 operand의
  diagnostic을 출력해도 최종 process status가 `0`으로 남는 경로가 있습니다.

위 항목의 개선 방향은 문서에만 기록되어 있으며 source에는 아직 적용되지 않았습니다.

## 상세 문서

- [Audit 개요](portfolio_audit/README.md)
- [Architecture](portfolio_audit/architecture.md)
- [기능 범위](portfolio_audit/feature_inventory.md)
- [설계 판단](portfolio_audit/design_rationale.md)
- [실패 분석](portfolio_audit/failures.md)
