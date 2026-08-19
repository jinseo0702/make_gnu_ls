# Architecture audit

All factual architecture statements below are VERIFIED FROM CODE unless otherwise marked.

## End-to-end flow

```text
argv
  ↓
parsing_argument / check_option
  ├─ t_option bitmask: l, R, a, r, t
  └─ t_parsing linked list: directory operands
  ↓ (once per operand, or "." by default)
ft_ls
  ↓
opendir → recursive readdir ingestion
  ↓
t_list_ls flat sibling list (next)
  ↓
hidden filtering → name sort → optional lstat/format → optional mtime sort
  ↓
stdout formatting
  ↓ when -R
directory nodes create child lists (child) → ft_ls recursively
  ↓
closedir + recursive list/string cleanup
```

## Entry point and components

| Component | Responsibility | Source evidence |
|---|---|---|
| `main` | Initialize option/path parsing, default to `.`, process operands sequentially, free all lists | `src/main.c:94` |
| argument parser | Pack five short options into a bitmask and store non-option operands in `t_parsing` | `src/utils/parsing.c:51`, `src/utils/parsing.c:80`, `include/utils.h:18` |
| directory stream adapter | `opendir`/`readdir`/`closedir` and error reporting | `src/dirStream/dirStream.c:6` |
| entry ingestion | Recursively consume one `readdir` result per call and append a sentinel-terminated linked-list node | `src/main.c:5` |
| option pipeline | Remove hidden entries, choose name order, populate metadata when needed, choose time order | `src/utils/doOption.c:5` |
| list/sort layer | Own sibling/child links, remove nodes, bubble-sort by name or mtime, recursively free nodes | `src/list_ls/listUtils.c:88`, `src/list_ls/listUtils.c:113`, `src/list_ls/listUtils.c:129`, `src/list_ls/listUtils.c:187` |
| metadata/long format | Call `lstat`; decode type/mode, links, UID/GID, size, mtime, and symlink target; compute column widths | `src/dirStream/longFormat.c:20`, `src/dirStream/longFormat.c:77` |
| output/error layer | Print short/long listings and diagnostics | `src/utils/utils.c:5`, `src/utils/utils.c:17` |

## Core data structures

### `t_option`

A `char` bitmask holds five flags: `l`, `R`, `a`, `r`, and `t`. Combined and repeated short flags converge on the same set bits.

### `t_parsing`

A singly linked list stores each path operand (`str`) and later owns the corresponding listing head (`head`). Operands are processed in argument order.

### `t_list_ls`

Each entry node stores:

- the directory stream pointer and full-path-like working string;
- copied `dirent` and entry name;
- selected `stat` fields (`mode`, links, UID/GID, size, blocks, mtime);
- a separately allocated printable long-format record;
- `next` for siblings and `child` for recursive subdirectory listings.

The structure therefore represents each directory as a sibling list and recursive traversal as child lists attached to directory entries.

## Control and policy details

1. A directory is fully read before output. `recReadDir` creates one node per `readdir` result plus an empty terminal node.
2. Without `-a`, all entries whose first byte is `.` are removed before sorting and recursion.
3. Without `-t`, bytewise `ft_strncmp` bubble sort determines ascending or reverse name order. Locale collation is not consulted.
4. `-l`, `-R`, or `-t` triggers `lstat` for every retained entry. `-R` needs metadata to identify directories.
5. `-t` compares `st_mtim.tv_sec`, then nanoseconds. Equal timestamps retain ingestion order; no name tie-break is present.
6. Recursive output descends only when the rendered type byte is `d`; `.` and `..` are explicitly skipped.
7. Long output turns metadata into owned strings before printing and computes widths across the directory list.

## External interfaces and platform assumptions

- Filesystem/system interfaces: `opendir`, `readdir`, `closedir`, `lstat`, `readlink`.
- Identity/time interfaces: `getpwuid`, `getgrgid`, `time`, `ctime`.
- Runtime interfaces: heap allocation/free, `errno`, `strerror`, stdout/stderr.
- Linux/POSIX coupling: `DIR`, `dirent`, `struct stat.st_mtim`, permission/type macros, and `<linux/limits.h>`/`PATH_MAX`.
- Fixed-size path buffers occur at 10,000 bytes and at `PATH_MAX`; path-boundary behavior is UNKNOWN until tested.

## Error handling and resource lifecycle

- `opendir` failure prints a diagnostic and returns from `ft_ls`.
- `readdir` errors are stored in `ErrorNum` and cause process exit; `closedir` failure only prints.
- `lstat` and `readlink` failures print but continue with the current buffer/state.
- Successful directory streams are closed after ingestion and before recursion.
- Entry lists, child lists, paths, names, and long-format strings are recursively freed after each top-level operand.
- `main` always returns `0` after ordinary operand processing, including an `opendir` failure path. GNU-compatible failure status is therefore not represented by that path.

## Most important design characteristics

1. **Bitmask option composition** — five orthogonal flags select a fixed transformation pipeline.
2. **Materialize then transform** — entries are collected before filtering, sorting, metadata conversion, and output; this simplifies global ordering/column width at the cost of storing the directory.
3. **One node type for list and recursion tree** — `next` represents siblings and `child` represents nested directory results, enabling one recursive destructor.
4. **Metadata is demand-driven** — plain name listing avoids `lstat`; `-l`, `-R`, and `-t` enable it.
5. **Traversal follows displayed order** — recursion occurs after sorting/printing, so subdirectories are visited in the selected list order.
6. **Algorithmic scaling risk** — INFERENCE: append-by-tail-scan plus bubble sorting makes large single-directory workloads quadratic in entry count; per-entry recursive ingestion also makes call depth proportional to entry count.
7. **Directory-only dispatch** — all operands go directly to `opendir`; regular-file operands have no alternate path.

USER-PROVIDED RATIONALE: none yet. The code establishes behavior/structure, not why these choices were made.
