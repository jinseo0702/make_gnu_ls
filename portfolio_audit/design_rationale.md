# Design rationale

This document separates code/runtime facts, the author's stated rationale, and later inference. It does not treat inferred intent as verified fact.

## Verified facts

- VERIFIED FROM CODE: `recReadDir` first materializes directory entries into `t_list_ls` nodes; filtering, sorting, optional metadata conversion, and output happen afterward.
- VERIFIED FROM CODE: `t_list_ls.next` represents sibling entries and `t_list_ls.child` owns a recursively listed subdirectory.
- VERIFIED FROM CODE: entry ingestion, directory descent, and child-list cleanup are recursive.
- VERIFIED FROM CODE: list append scans to the tail and name/time ordering uses linked-list bubble sorts.
- VERIFIED FROM RUNTIME TEST: basic directory listing, long metadata, symlinks, and recursive traversal have representative GNU-matching cases.
- VERIFIED FROM RUNTIME TEST: equal-time ordering, some permission/type rendering, and error-status behavior have correctness gaps.

## User-provided rationale

The author provided the following rationale after CHECKPOINT B:

1. **Why collect before output?** Information should be gathered first, then edited and adjusted before presentation.
2. **Alternative considered:** place all data into structures or arrays and then output it using a memory-pool-style approach.
3. **Intentional simplification:** regular-file operands and some GNU behavior were intentionally kept outside the implemented scope.
4. **Hardest judgment:** understanding the relevant GNU official documentation was difficult; the recursive design also made memory leaks and efficiency difficult to assess.
5. **What would change now:** redesign the recursive algorithm, allocation/free policy, and data structure with performance in mind.

## Inference

- INFERENCE: the selected design prioritized a staged `collect → transform → output` mental model and local implementation clarity over streaming output or contiguous storage.
- INFERENCE: using the same node type for sibling and child ownership made recursive cleanup conceptually uniform, while making ownership and performance harder to reason about.
- INFERENCE: the contemplated structure/array memory pool shows that allocation locality and ownership were considered, but why it was rejected is UNKNOWN.
- INFERENCE: F22 regular-file operand behavior should remain classified as an intentional scope limitation, not as a defect relative to the author's chosen scope. It remains a verified GNU-parity gap.
- INFERENCE: broader GNU behaviors cannot all be relabeled intentional without a precise list; only the user-confirmed general simplification is recorded.

## Performance-claim boundary

No runtime, allocation-count, peak-memory, or stack-depth benchmark has been run. Therefore the audit does not claim that recursion, linked lists, or allocation policy are slow or inefficient in measured terms. The source shows plausible scaling risks, but any future use of “optimized,” “faster,” or “more efficient” requires a controlled Before/After measurement.
