# Failure analysis

The five cases below were selected for technical and portfolio value. All expected/actual observations are VERIFIED FROM RUNTIME TEST; root causes are VERIFIED FROM CODE unless marked INFERENCE.

## 1. Equal-mtime `-t` ordering — F08 and F25

**Expected**

- F08 GNU order: `alpha, mu, zeta` for three exactly equal mtimes.
- F25 GNU puts `.` before `link` when both have mtime `1787134359776026561` ns.

**Actual**

- F08 target order: `mu, alpha, zeta`.
- F25 target puts `link` before `.`; the remaining compared long records match.

**Relevant code path**

`do_Option` populates metadata and calls `time_sort_list`; `src/list_ls/listUtils.c:187-223` compares seconds and nanoseconds only.

**Root cause**

When both time components are equal, the comparator result remains zero and preserves filesystem `readdir` order. GNU applies a name tie-break. The same missing comparator stage independently appears in F08 and the combined F25 case.

**Classification / severity**

Correctness bug; medium severity. `-t` is correct for distinct times but nondeterministic relative to GNU for ties.

**Possible fix direction**

Define one chained comparator `(mtime, name)` and apply `-r` to the complete comparison policy, or name-sort first and apply a demonstrably stable time sort. Lock behavior with F08 and F25 regression tests.

## 2. Special permission bits omitted — F11

**Expected**

GNU modes: `-rwxr-sr-x`, `-rwsr-xr-x`, `drwxrwxrwt`.

**Actual**

Target modes: `-rwxr-xr-x`, `-rwxr-xr-x`, `drwxrwxrwx`.

**Relevant code path**

`decoding_authority`, `src/dirStream/longFormat.c:106-175`.

**Root cause**

The formatter maps only the low nine read/write/execute bits through `"rwxrwxrwx"`. It never checks `S_ISUID`, `S_ISGID`, or `S_ISVTX`, so it cannot produce `s/S/t/T`.

**Classification / severity**

Correctness bug; high metadata severity because `-l` presents inaccurate permissions.

**Possible fix direction**

After base rwx decoding, apply special-bit rules to user/group/other execute positions, including uppercase when the associated execute bit is absent.

## 3. Operand failure does not affect process status — F20/F21

**Expected**

GNU returns status `2` for nonexistent input, including a mixed valid/missing invocation while still listing the valid directory.

**Actual**

The target prints an `Opendir Error` and continues where possible, but returns status `0` in both cases.

**Relevant code path**

`openDirectoryStream` reports and returns NULL (`src/dirStream/dirStream.c:6-10`); `ft_ls` returns without a status (`src/main.c:31-33`); `main` unconditionally returns zero (`src/main.c:109-118`).

**Root cause**

Error information is not propagated through `ft_ls` or aggregated across operands. Diagnostics and process success/failure are separate, with no final error state.

**Classification / severity**

Correctness and robustness bug; high severity for shell scripts and automation.

**Possible fix direction**

Return a typed per-operand result, continue processing operands, accumulate a nonzero final status, and keep stdout/stderr capture semantics explicit.

## 4. Regular-file operand rejected — F22

**Expected**

GNU prints `fixtures/F22_file` and returns zero.

**Actual**

The target prints an `Opendir Error`, produces no listing, and returns zero.

**Relevant code path**

Every parsed operand enters `ft_ls`, which immediately calls `opendir` (`src/main.c:31`). There is no pre-dispatch `lstat` for argument type.

**Root cause**

The execution architecture models every operand as a directory root. It has entry metadata/rendering logic for files inside directories but no top-level file-operand path.

**Classification / severity**

USER-PROVIDED RATIONALE confirms this was intentional simplification. It is therefore a scope limitation rather than a directory-traversal bug. It still has high GNU-parity impact and high architectural interest.

**Possible fix direction**

Add an operand classification stage using `lstat`; partition direct file entries, traversable directories, and errors, then reuse the existing sort/format layer for both file operands and directory entries.

## 5. Special filename record boundaries — F24

**Expected**

An output policy that preserves distinguishable records for spaces, tabs, newlines, and a leading dash. GNU's test oracle was captured with NUL delimiters.

**Actual**

All fixture name bytes appear in target output in the correct bytewise order, but names are separated by two spaces and a final newline. A name containing two spaces or a newline is therefore indistinguishable from formatting delimiters.

**Relevant code path**

Short output writes `name` literally followed by two spaces (`src/utils/utils.c:21-26`).

**Root cause**

Presentation and record framing share the same byte sequences; there is no quoting/escaping or unambiguous delimiter mode.

**Classification / severity**

Formatting/representation limitation; PARTIAL. Entries are not dropped, but machine-readable or visually unambiguous output is unavailable for these names.

**Possible fix direction**

Choose and document a quoting/escaping policy for terminal output, or add a dedicated NUL-delimited mode if that scope is desired. Do not hide this issue in normalization.

## Additional verified failures

- F12: FIFO marker is hard-coded as uppercase `P` at `src/dirStream/longFormat.c:135-139`; GNU uses lowercase `p`.
- F23: invalid option exits with enum value `4`, while GNU exits `2` (`src/utils/parsing.c:71-75`).
- F25 is not an independent root cause; it is combined-case confirmation of the F08 equal-time tie-break defect.

## Correctness versus scope

| Category | Cases |
|---|---|
| Correctness/robustness bugs | F08, F11, F12, F20, F21, F23, F25 |
| Scope limitation / missing feature | F22 |
| Formatting/representation limitation | F24 (PARTIAL) |
| Crash | none |

## Portfolio-value ranking after design-rationale capture

1. **F08/F25 comparator policy** — best first correctness cycle: clean evidence, implemented option, narrow regression tests.
2. **F20/F21 error propagation** — strong CLI robustness and multi-operand state-design case.
3. **F11 permission semantics** — concrete metadata correctness case.
4. **F22 operand dispatch** — strongest future architectural expansion story, but user-confirmed intentional scope means it is not the first correctness fix.
5. **F24 filename framing** — advanced representation edge case, likely within the intentionally simplified GNU surface.

## Possible solution architectures

1. **Operand planner + result aggregation**: `lstat` each operand, partition file/directory/error work, reuse rendering, and aggregate final status. Addresses F20–F22.
2. **Explicit comparison-policy layer**: composable name/mtime keys with a GNU-compatible tie-break and a single reversal rule. Addresses F08/F25 and reduces duplicated sort code.
3. **Central metadata/output encoder**: one mode/type decoder with special-bit rules plus a deliberate filename framing policy. Addresses F11, F12, and F24.

No fix has been applied. PHASE 10 recommends F08/F25 first; see `improvement.md`.
