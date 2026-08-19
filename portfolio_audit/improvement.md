# Improvement candidate selection

Status: **candidate selected; no source change has been made**.

The ranking uses the requested dimensions qualitatively because Portfolio Value and Architectural Interest are judgment dimensions, not measured quantities. Each judgment is labeled INFERENCE and grounded in the corrected baseline.

## Candidate ranking

| Candidate | Portfolio Value | Correctness Impact | Architectural Interest | Implementation Cost | Decision |
|---|---|---|---|---|---|
| F08/F25 equal-mtime comparator | High | Medium–High | Medium | Low | **Recommended first** |
| F20/F21 error propagation | High | High | High | Medium | Second |
| F11 special permission bits | Medium | High for `-l` metadata | Medium | Low | Third |
| F12 FIFO type marker | Low | Narrow but definite | Low | Very low | Small follow-up |
| F24 filename framing | Medium | Partial representation gap | Medium | Medium | Defer pending intended scope |
| F22 regular-file operand | High as an architecture story | High for GNU parity | High | High | Scope expansion; exclude from first correctness cycle |

Ratings above are INFERENCE. Runtime evidence and source locations are in `test_results.md` and `failures.md`.

## Recommended first improvement: F08/F25

Implement GNU-compatible name tie-breaking when `-t` sees identical modification timestamps.

Why this is first:

- It corrects an implemented core option rather than expanding scope.
- Two independent cases expose the same root cause: focused F08 and combined F25.
- F06 and F07 already establish correct distinct-time behavior, giving useful regression protection.
- The source change can remain localized to comparison policy rather than forcing the broader data-structure redesign before performance is measured.
- Before/After evidence is exact: ordered record vectors, not a subjective formatting judgment.

## Acceptance criteria for an approved cycle

1. Preserve the corrected baseline as Before evidence.
2. Define GNU-compatible ordering for exact timestamp ties and reverse mode before editing.
3. Add a deterministic reverse-tie regression case if needed to cover `-tr` explicitly.
4. Make only the approved comparator-policy source change.
5. Re-run F06, F07, F08, and F25, then the full 25-case suite.
6. Require F08 and F25 to become PASS without regressing existing PASS cases.
7. Record the new source hash/commit and the complete After matrix.

## Why not start with the data-structure redesign?

The author wants to revisit recursion, allocation/free, and data structures for performance. That is a valid future engineering investigation, but no performance or memory baseline exists yet. Starting there would mix correctness work with a broad unmeasured rewrite.

Before such a redesign, measure controlled directory-size workloads for runtime, allocation behavior, peak memory, recursion depth, and cleanup. Only then select a structure and make a Before/After performance claim.

## Approval gate

Source modification remains prohibited until the user explicitly approves one candidate. The current recommendation is the F08/F25 comparator-policy fix only.
