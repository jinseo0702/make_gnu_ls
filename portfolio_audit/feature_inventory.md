# Feature inventory and functional scope

Status describes source presence/completeness at CHECKPOINT A, not runtime correctness. No feature row is runtime-verified yet.

## Inventory

| Feature | Status | Source evidence / reason | Runtime verified? |
|---|---|---|---|
| No-operand default to current directory (`.`) | IMPLEMENTED | `src/main.c:101-106` | No |
| Explicit directory operand | IMPLEMENTED | parser stores operand; `ft_ls` calls `opendir`, `src/utils/parsing.c:85-89`, `src/main.c:31` | No |
| Multiple directory operands | IMPLEMENTED | linked operand list processed sequentially, `src/utils/parsing.c:91-114`, `src/main.c:109-115` | No |
| `-l` flag | IMPLEMENTED | parser bit plus long-output path, `src/utils/parsing.c:56-58`, `src/main.c:56-69` | No |
| `-R` flag | IMPLEMENTED | parser bit plus child recursion, `src/utils/parsing.c:59-61`, `src/main.c:72-91` | No |
| `-a` flag | IMPLEMENTED | parser bit; hidden removal bypass, `src/utils/parsing.c:62-64`, `src/utils/doOption.c:8-10` | No |
| `-r` flag | IMPLEMENTED | reverse name/time branches, `src/utils/doOption.c:12-17`, `src/utils/doOption.c:26-31` | No |
| Combined/repeated short flags | IMPLEMENTED | loop over option characters and idempotent bit setting, `src/utils/parsing.c:51-77` | No |
| Default hidden-entry exclusion | IMPLEMENTED | removes nodes whose first name byte is `.`, `src/list_ls/listUtils.c:113-126` | No |
| Bytewise ascending/reverse name sorting | IMPLEMENTED | linked-list bubble sorts using `ft_strncmp`, `src/list_ls/listUtils.c:129-185` | No |
| `-t` modification-time ordering | PARTIAL | seconds+nanos implemented, but exact ties have no GNU name tie-break, `src/list_ls/listUtils.c:187-260` | No |
| Basic long metadata fields | PARTIAL | type/mode, links, owner, group, size, mtime, name exist; special modes/device-number semantics are absent from formatting | No |
| File-type decoding | PARTIAL | regular/dir/char/block/FIFO/symlink/socket branches exist; FIFO is rendered `P`, and special permission bits are not decoded, `src/dirStream/longFormat.c:106-172` | No |
| Symlink target rendering in `-l` | IMPLEMENTED | `lstat` preserves link type and `readlink` builds `name -> target`, `src/dirStream/longFormat.c:93-96`, `src/dirStream/longFormat.c:272-298` | No |
| Recursive hidden-directory policy | IMPLEMENTED | filtering precedes recursion and `.`/`..` are explicitly skipped, `src/utils/doOption.c:8-10`, `src/main.c:74-88` | No |
| UID/GID name lookup with numeric fallback | IMPLEMENTED | `getpwuid`/`getgrgid` and fallback conversion, `src/dirStream/longFormat.c:186-223` | No |
| Total block aggregate in long output | PARTIAL | sums `st_blocks` and divides by two; cross-environment GNU block-size semantics not established, `src/dirStream/longFormat.c:41-43`, `src/main.c:53` | No |
| Invalid short-option handling | IMPLEMENTED | diagnostic plus process exit path, `src/utils/parsing.c:71-75` | No |
| Missing/unreadable operand behavior | PARTIAL | diagnostic exists, but `ft_ls` returns and `main` ultimately returns zero, `src/dirStream/dirStream.c:6-10`, `src/main.c:31-33`, `src/main.c:118` | No |
| Special filenames | PARTIAL | names are retained/printed literally, but whitespace-delimited output and leading-dash operand parsing leave important cases unresolved | No |
| Empty or hidden-only directory behavior | UNKNOWN | sentinel flow suggests a path, but no deterministic runtime evidence exists yet | No |
| Regular-file operand | NOT IMPLEMENTED | every operand goes directly to `opendir`; there is no `lstat` dispatch for an operand, `src/main.c:31-33` | No |
| `--` end-of-options marker | NOT IMPLEMENTED | every multi-byte leading-dash argument is parsed as option characters, `src/utils/parsing.c:85`, `src/utils/parsing.c:94-97` | No |
| Other GNU options/color/terminal column layout | NOT IMPLEMENTED | parser accepts only `lRart`; short output is fixed literal spacing | No |
| Success-path resource cleanup | IMPLEMENTED | directory close plus recursive node/string cleanup, `src/main.c:42`, `src/main.c:113-117`, `src/list_ls/listUtils.c:88-99` | No |

Computed inventory count: **15 IMPLEMENTED, 6 PARTIAL, 3 NOT IMPLEMENTED, 1 UNKNOWN** across 25 rows. This count measures code-level inventory only; it is not a correctness score.

## Current functional scope

| Scope metric | Measured value | Meaning / limitation |
|---|---:|---|
| Accepted short-option letters | 5 (`l`, `R`, `a`, `r`, `t`) | VERIFIED FROM CODE; acceptance does not prove semantics |
| Bitmask flag subsets | 32 (`2^5`) | Parser can represent them; combinations are not runtime-verified |
| Explicit sort directions/policies | 4 | name ascending, name reverse, mtime descending, mtime reverse; tie behavior is incomplete |
| Executable operand classes | 1 primary class | directories; multiple operands supported, regular-file operands not dispatched |
| Recognized filesystem type predicates | 7 + fallback | regular, directory, char, block, FIFO, symlink, socket, unknown; rendering is partial |
| Long-output information groups | 8 + aggregate | type/permissions, links, owner, group, size, mtime, name, symlink target, plus total blocks |
| Traversal modes | 2 | one directory level or recursive directory tree |
| Application translation units in the build | 7 | descriptive architecture metric only, not a portfolio achievement |

## Scope statement

VERIFIED FROM CODE: this is a Linux/POSIX-oriented, directory-first `ls` subset centered on the mandatory-looking `-lRart` option family. It materializes entries, applies filtering/sorting/metadata policies, prints them, and optionally recurses. GNU-wide option coverage and regular-file operand parity are outside the current implementation.

CHECKPOINT A 당시에는 IMPLEMENTED 행의 semantic correctness가 UNKNOWN이었다. 승인된 baseline 결과의 runtime overlay는 아래와 같다.

## PHASE 4 runtime overlay

VERIFIED FROM RUNTIME TEST after approval:

- PASS evidence exists for default/empty/hidden listing, `-a`, `-r`, distinct-time `-t/-tr`, basic long sizes/links/modes, valid and broken symlinks, recursive traversal, hidden recursive traversal, non-followed directory symlinks, and multiple directory operands.
- FAIL evidence exists for equal-mtime ordering, special permission bits, FIFO type rendering, operand error status, regular-file operands, invalid-option status, and the combined case that exposes the same equal-mtime tie behavior.
- PARTIAL evidence exists for whitespace/newline-containing filenames: bytes are emitted, but record boundaries are ambiguous.
- Full evidence and raw paths are in `test_results.md` and `test_results.json`.
