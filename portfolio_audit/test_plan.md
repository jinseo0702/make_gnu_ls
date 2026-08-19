# Baseline test plan — executed after CHECKPOINT A approval

This was the CHECKPOINT A approval boundary. The 25 cases were implemented and executed; corrected results are in `test_results.json` and `test_results.md`.

## Profile and goal

Applied plan: directory traversal and metadata/output comparison against GNU `ls` (the provided instruction's `make_gnu_ls` profile, labeled PROFILE D there).

The user's `PROFILE B` label conflicts with that document because PROFILE B is defined for an ELF/GNU nm project. The user approved target-matched routing before execution.

## Primary oracle

Required primary oracle: **an actual GNU coreutils `ls`, version and executable hash pinned at suite start**.

The oracle is pinned at `portfolio_audit/bin/gnu-ls`: GNU coreutils 9.4, SHA-256 `53a9c0557a948069d56f964cf21c7c0854bb2677d9985080369ed1e172161625`, copied byte-for-byte from `/snap/core24/1643/usr/bin/ls`. `/usr/bin/ls` remains uutils and was not used.

Independent invariants will supplement the oracle where parsing presentation is ambiguous:

- fixture manifest contains the exact expected names/order inputs;
- `lstat` supplies ground-truth type, mode, link count, UID/GID, size, blocks, and mtime;
- symlink fixtures record the exact `readlink` target;
- expected recursion graph is generated from fixture construction, not from either `ls` output.

## Controlled environment

- Use a suite-owned fixture root under `portfolio_audit/raw/` after approval.
- Set `LC_ALL=C`, `LANG=C`, `TZ=UTC0`; keep `BLOCK_SIZE`, `BLOCKSIZE`, and `POSIXLY_CORRECT` unset so GNU's default long-format byte sizes and 1 KiB `total` units are preserved.
- Run both programs non-interactively with stdout, stderr, exit status, and elapsed/timeout status captured separately.
- Use identical working directory and identical operand spelling for target and oracle.
- Fix mtimes explicitly, including nanoseconds where the filesystem supports them.
- Record filesystem type and mount/block-size context because `st_blocks`/`total` can be filesystem-dependent.
- Distinguish setup failure, oracle failure, parser/harness failure, and target failure.
- Preserve raw byte output before normalization.

## Proposed deterministic cases

| ID | Fixture / invocation focus | Semantic dimensions |
|---|---|---|
| F01 | Default invocation on regular files | default `.`, inclusion, ascending name order |
| F02 | Explicit empty directory | empty output, exit behavior |
| F03 | Directory containing only hidden entries | default exclusion and stability |
| F04 | `-a` with visible/hidden entries | inclusion of `.`, `..`, dotfiles and order |
| F05 | `-r` with deliberately unsorted names | exact reverse name order |
| F06 | `-t` with fixed distinct second/nanosecond mtimes | newest-first order |
| F07 | `-tr` on the same fixture | oldest-first order |
| F08 | `-t` with identical mtimes | GNU tie-break behavior |
| F09 | `-l` with different sizes and hard-link counts | metadata values and alignment |
| F10 | `-l` across `000`, `644`, `755` modes | nine permission bits |
| F11 | setuid, setgid, sticky fixtures where permitted | special permission rendering |
| F12 | regular, directory, FIFO, and Unix socket | type marker and relevant metadata |
| F13 | valid relative and absolute symlinks | link type and displayed target |
| F14 | broken symlink | inclusion, target, error behavior |
| F15 | fixed recent, old, and future mtimes | timestamp format boundary |
| F16 | `-R` on a small two-level tree | headings, traversal, order, no duplication |
| F17 | `-R` vs `-Ra` with hidden subdirectory | recursive hidden policy |
| F18 | `-R` with symlink to directory | must not traverse through link |
| F19 | two directory operands | operand order, headings, separation |
| F20 | nonexistent operand | stderr content/class and nonzero status |
| F21 | mixed valid and nonexistent operands | continued output plus aggregate status |
| F22 | regular-file operand | explicit current-scope boundary vs GNU behavior |
| F23 | invalid short option | diagnostic channel and status |
| F24 | spaces, tabs, newline, and `./-leading-dash` names | byte-preserving inclusion and presentation |
| F25 | combined `-lRat` on a small tree | interaction of all implemented policies |

Planned count: **25 cases**. These are case definitions, not executed tests and not PASS counts.

## Comparison model

Each case records:

```text
fixture manifest
target argv / oracle argv
raw stdout
raw stderr
exit status
timeout/signal
normalized semantic records
classification and reason
```

PASS requires the core semantic records, order, metadata, recursion graph, error channel, and status relevant to that case to agree. A substring match is insufficient.

## Normalization policy

### Normalized

- Locale, timezone, block unit, and terminal/color behavior are controlled by environment or oracle-only presentation flags.
- For simple-name short listings, physical whitespace/line wrapping may be converted to an ordered vector of names. Vector membership and order remain exact.
- Generated absolute fixture-root prefixes may be replaced with a literal `$FIXTURE` in reports only; comparison uses identical operand text.
- Oracle quoting/color is disabled where possible so it does not manufacture presentation differences.
- Raw output is always retained, so normalization remains auditable.

### Not normalized

- missing or extra entry;
- wrong entry order or time tie-break;
- wrong type, permission, link count, owner/group identity, size, block total, or timestamp content;
- wrong symlink target;
- missing/extra/wrong recursive directory or heading;
- stdout versus stderr channel;
- exit status, signal, crash, timeout, or deadlock;
- behavior for nonexistent, unreadable, mixed, or regular-file operands;
- special-filename corruption/ambiguity in F24.

Timestamp locale/timezone is controlled, but an incorrect recent/old/future decision or incorrect displayed timestamp is not normalized away.

## Classification

- `PASS`: core semantics agree with the oracle/invariant.
- `PARTIAL`: core operation occurs but meaningful semantic information is missing or incomplete.
- `FAIL`: core argument/result/order/metadata/error behavior is wrong.
- `CRASH`: abnormal signal, timeout, deadlock, or otherwise unusable execution.

## Execution record

- Approved and executed: F01–F25.
- Corrected baseline run: `raw/20260819T101239Z/`.
- One sandbox setup failure is preserved separately at `raw/20260819T101131Z/`.
- One harness-environment run invalidated because `BLOCK_SIZE=1024` altered GNU file-size display is preserved at `raw/20260819T101150Z/` and excluded from baseline counts.
