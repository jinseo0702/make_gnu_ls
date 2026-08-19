# Baseline environment

## Repository state

| Field | Value | Evidence class |
|---|---|---|
| Commit | `f48ad3f9026b78f4daa585973adf3b6dce92f417` | VERIFIED FROM RUNTIME TEST |
| Branch | `main` tracking `origin/main` | VERIFIED FROM RUNTIME TEST |
| Dirty before build | clean | VERIFIED FROM RUNTIME TEST |
| OS | Ubuntu 26.04 LTS (Resolute Raccoon) | VERIFIED FROM RUNTIME TEST |
| Kernel | Linux `7.0.0-29-generic` | VERIFIED FROM RUNTIME TEST |
| Architecture | `x86_64` | VERIFIED FROM RUNTIME TEST |
| Compiler | GCC `15.2.0` (`gcc (Ubuntu 15.2.0-16ubuntu1)`) | VERIFIED FROM RUNTIME TEST |
| Build command | `make` | VERIFIED FROM CODE + RUNTIME TEST |
| Run command | `./ft_ls [combined short options] [directory ...]` | VERIFIED FROM CODE; not behavior-tested |

README에는 제목만 있어 build/run 방법은 top-level `makefile`과 `main`/argument parser에서 도출했다.

## Build baseline

- VERIFIED FROM RUNTIME TEST: `make` exited successfully and produced a 64-bit x86-64 PIE executable named `ft_ls`.
- VERIFIED FROM RUNTIME TEST: executable is dynamically linked to libc and contains debug information.
- UNKNOWN: no feature behavior has been classified as PASS/PARTIAL/FAIL/CRASH. Building is not a semantic correctness test.
- The audit-created build artifacts (`ft_ls`, `.o`, `libft.a`, `libftprintf.a`) were removed afterward with the repository's `make fclean` target. Final Git status contains only the new `portfolio_audit/` directory.

## Source integrity

Source manifest definition:

```sh
rg --files -0 -g '*.c' -g '*.h' -g 'Makefile' -g 'makefile' \
  | sort -z | xargs -0 sha256sum | sha256sum
```

| Point | SHA-256 |
|---|---|
| Before build | `4c62c7180f41b690b93ae1c5f5a531a4612ed4b53476990bed9bfc740ece63e0` |
| After build | `4c62c7180f41b690b93ae1c5f5a531a4612ed4b53476990bed9bfc740ece63e0` |

VERIFIED FROM RUNTIME TEST: both aggregate digests match. `git diff` also contains no tracked source change.

## Reference tool status

CHECKPOINT A 시점에는 `/usr/bin/ls`가 uutils였지만, 승인 후 실제 GNU binary를 별도로 고정해 prerequisite를 충족했다:

- VERIFIED FROM RUNTIME TEST: `/usr/bin/ls` resolves to `/usr/lib/cargo/bin/coreutils/ls`.
- VERIFIED FROM RUNTIME TEST: it reports `ls (uutils coreutils) 0.8.0`, not GNU coreutils.
- VERIFIED FROM RUNTIME TEST: package ownership for `/usr/bin/ls` is `coreutils-from-uutils`.
- VERIFIED FROM RUNTIME TEST: installed package metadata also lists `coreutils 9.5-1ubuntu2+0.0.0~ubuntu25`, but no callable GNU `ls` binary was found in the checked standard locations.
- VERIFIED FROM RUNTIME TEST: `/snap/core24/1643/usr/bin/ls` reports `ls (GNU coreutils) 9.4`.
- VERIFIED FROM RUNTIME TEST: the binary was copied without byte changes to `portfolio_audit/bin/gnu-ls`.
- VERIFIED FROM RUNTIME TEST: pinned SHA-256 is `53a9c0557a948069d56f964cf21c7c0854bb2677d9985080369ed1e172161625`.
- The corrected baseline uses this pinned binary only; uutils is not used as the primary oracle.

## Baseline commands for the approved phase

```text
Build: make
Target: /home/jinseo/duo/make_gnu_ls/ft_ls
Primary oracle: portfolio_audit/bin/gnu-ls — GNU coreutils 9.4
Environment: LC_ALL=C, LANG=C, TZ=UTC0, non-TTY; BLOCK_SIZE/BLOCKSIZE/POSIXLY_CORRECT unset
```
