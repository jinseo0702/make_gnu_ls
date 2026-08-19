# Corrected baseline results

## Identity

| Field | Value |
|---|---|
| Run | `20260819T101239Z` |
| Commit | `f48ad3f9026b78f4daa585973adf3b6dce92f417` |
| Target SHA-256 | `96f629d9bd7a0595ed7ad481db0386cc56540853a0850f3bea808ac678ac2d8c` |
| Oracle | GNU coreutils `ls` 9.4 |
| Oracle SHA-256 | `53a9c0557a948069d56f964cf21c7c0854bb2677d9985080369ed1e172161625` |
| Controlled environment | `LC_ALL=C`, `LANG=C`, `TZ=UTC0`, non-TTY; block-size override variables unset |
| Cases | 25 |

Corrected classification: **PASS 16, PARTIAL 1, FAIL 8, CRASH 0**.

These are semantic case classifications, not substring checks. Raw stdout, stderr, exit status, fixture manifest, and normalized records are preserved under `raw/20260819T101239Z/`.

## Complete matrix

| ID | Result | Case | Evidence summary |
|---|---|---|---|
| F01 | PASS | default regular-name listing | ordered vector matches GNU |
| F02 | PASS | explicit empty directory | empty semantic listing matches |
| F03 | PASS | hidden-only directory | default exclusion matches |
| F04 | PASS | `-a` | inclusion and order match |
| F05 | PASS | `-r` | reverse name order matches |
| F06 | PASS | `-t` distinct timestamps | newest-first including nanoseconds matches |
| F07 | PASS | `-tr` | oldest-first matches |
| F08 | FAIL | `-t` equal timestamp | target `mu, alpha, zeta`; GNU `alpha, mu, zeta` |
| F09 | PASS | `-l` sizes/hard links | size, links, fields, order, and total match |
| F10 | PASS | basic permission modes | `000`, `644`, `755` match |
| F11 | FAIL | special permission bits | setuid/setgid/sticky markers are omitted |
| F12 | FAIL | filesystem types | FIFO is rendered `P` instead of `p` |
| F13 | PASS | valid symlinks | relative/absolute target and metadata match |
| F14 | PASS | broken symlink | inclusion, target, metadata, and status match |
| F15 | PASS | recent/old/future timestamps | controlled displayed timestamps match |
| F16 | PASS | `-R` two-level tree | headings, contents, order, traversal match |
| F17 | PASS | `-Ra` hidden tree | hidden recursive traversal matches |
| F18 | PASS | recursive symlink policy | directory symlink is listed but not followed |
| F19 | PASS | multiple directories | operand order, headings, contents match |
| F20 | FAIL | nonexistent operand | target prints diagnostic but returns 0; GNU returns 2 |
| F21 | FAIL | mixed valid/missing | valid output continues, but aggregate status is 0 instead of 2 |
| F22 | FAIL | regular-file operand | target emits `opendir` error; GNU lists the file |
| F23 | FAIL | invalid option | target returns 4; GNU returns 2 |
| F24 | PARTIAL | special filenames | all bytes emitted, but whitespace/newline delimiters are ambiguous |
| F25 | FAIL | combined `-lRat` | equal-mtime `.`/`link` order differs; other compared records match |

## Most important PASS evidence

1. **F09 basic long metadata** — byte size, hard-link count, owner/group, date, order, and block total all matched.
2. **F13/F14 symlink handling** — both valid and broken links preserved link metadata and displayed exact targets.
3. **F16–F18 traversal** — nested traversal, hidden traversal under `-a`, headings, order, and non-following of directory symlinks matched GNU.
4. **F06/F07 time direction** — distinct second/nanosecond mtimes matched in both normal and reverse order.

## Harness validation

Five injected defects were all rejected:

| Check | Injected defect | Detected? |
|---|---|---|
| H01 | missing entry | Yes |
| H02 | extra entry | Yes |
| H03 | wrong order | Yes |
| H04 | wrong size metadata | Yes |
| H05 | success status on an error | Yes |

Machine-readable evidence: `harness_validation.json`.

## Normalization actually applied

- Short simple-name output was converted to ordered vectors while preserving membership and order.
- Recursive output was converted to ordered `(heading, entries)` sections.
- Long output was parsed into type/mode, links, owner, group, byte size, displayed date, name/target, and total.
- Locale, timezone, color, quoting, and terminal behavior were controlled.
- No missing/extra file, order, permission, size, type, recursion, error channel, exit status, crash, or timeout was normalized away.

F24 used GNU NUL-delimited output only to establish the unambiguous oracle vector; target raw bytes were independently checked against the fixture manifest.

## Excluded runs

- `20260819T101131Z`: fixture setup failed under sandbox restrictions before target execution; not a target failure.
- `20260819T101150Z`: invalidated because the harness set `BLOCK_SIZE=1024`, which changed GNU long-format file sizes; none of its counts are used.
