#!/usr/bin/env python3
"""Deterministic semantic comparison of ft_ls against pinned GNU ls."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import time
from typing import Any, Callable


AUDIT = Path(__file__).resolve().parents[1]
REPO = AUDIT.parent
TARGET = REPO / "ft_ls"
ORACLE = AUDIT / "bin" / "gnu-ls"
CASES_FILE = AUDIT / "tests" / "cases.json"
TIMEOUT_SECONDS = 5

CONTROLLED_ENV = {
    "PATH": "/usr/bin:/bin",
    "LC_ALL": "C",
    "LANG": "C",
    "TZ": "UTC0",
    "TERM": "dumb",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_file(path: Path, data: bytes = b"x", mode: int = 0o644, mtime_ns: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(mode)
    if mtime_ns is not None:
        os.utime(path, ns=(mtime_ns, mtime_ns), follow_symlinks=False)


def set_mtime(path: Path, value_ns: int) -> None:
    os.utime(path, ns=(value_ns, value_ns), follow_symlinks=False)


def create_fixtures(root: Path) -> dict[str, Any]:
    fixtures = root / "fixtures"
    fixtures.mkdir(parents=True)
    now_ns = time.time_ns()
    recent_ns = now_ns - 86_400 * 1_000_000_000

    f01 = fixtures / "F01"
    f01.mkdir()
    for name in ("zeta", "alpha", "mu", ".hidden"):
        write_file(f01 / name, name.encode(), mtime_ns=recent_ns)

    (fixtures / "F02").mkdir()
    f03 = fixtures / "F03"
    f03.mkdir()
    write_file(f03 / ".zeta", b"z", mtime_ns=recent_ns)
    write_file(f03 / ".alpha", b"a", mtime_ns=recent_ns)

    f04 = fixtures / "F04"
    f04.mkdir()
    for name in ("zeta", ".hidden", "alpha"):
        write_file(f04 / name, name.encode(), mtime_ns=recent_ns)

    f05 = fixtures / "F05"
    f05.mkdir()
    for name in ("beta", "alpha", "gamma"):
        write_file(f05 / name, name.encode(), mtime_ns=recent_ns)

    for case_id in ("F06", "F07"):
        directory = fixtures / case_id
        directory.mkdir()
        write_file(directory / "old", b"o", mtime_ns=recent_ns - 2_000_000_000)
        write_file(directory / "middle", b"m", mtime_ns=recent_ns - 999_999_900)
        write_file(directory / "new", b"n", mtime_ns=recent_ns + 200)

    f08 = fixtures / "F08"
    f08.mkdir()
    for name in ("zeta", "alpha", "mu"):
        write_file(f08 / name, name.encode(), mtime_ns=recent_ns)

    f09 = fixtures / "F09"
    f09.mkdir()
    write_file(f09 / "one", b"1", mtime_ns=recent_ns)
    write_file(f09 / "ten", b"0123456789", mtime_ns=recent_ns)
    write_file(f09 / "thousand", b"x" * 1000, mtime_ns=recent_ns)
    write_file(f09 / "hard_source", b"hard", mtime_ns=recent_ns)
    os.link(f09 / "hard_source", f09 / "hard_alias")

    f10 = fixtures / "F10"
    f10.mkdir()
    write_file(f10 / "mode000", b"0", mode=0o000, mtime_ns=recent_ns)
    write_file(f10 / "mode644", b"6", mode=0o644, mtime_ns=recent_ns)
    write_file(f10 / "mode755", b"7", mode=0o755, mtime_ns=recent_ns)

    f11 = fixtures / "F11"
    f11.mkdir()
    write_file(f11 / "setuid", b"u", mode=0o4755, mtime_ns=recent_ns)
    write_file(f11 / "setgid", b"g", mode=0o2755, mtime_ns=recent_ns)
    sticky = f11 / "sticky"
    sticky.mkdir()
    sticky.chmod(0o1777)
    set_mtime(sticky, recent_ns)

    f12 = fixtures / "F12"
    f12.mkdir()
    write_file(f12 / "regular", b"r", mtime_ns=recent_ns)
    directory_entry = f12 / "directory"
    directory_entry.mkdir()
    set_mtime(directory_entry, recent_ns)
    os.mkfifo(f12 / "fifo", 0o644)
    set_mtime(f12 / "fifo", recent_ns)
    socket_path = f12 / "socket"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(socket_path))
    sock.close()
    set_mtime(socket_path, recent_ns)

    f13 = fixtures / "F13"
    f13.mkdir()
    write_file(f13 / "target", b"target", mtime_ns=recent_ns)
    os.symlink("target", f13 / "relative_link")
    os.symlink(str((f13 / "target").resolve()), f13 / "absolute_link")

    f14 = fixtures / "F14"
    f14.mkdir()
    os.symlink("missing-target", f14 / "broken")

    f15 = fixtures / "F15"
    f15.mkdir()
    write_file(f15 / "recent", b"r", mtime_ns=now_ns - 60 * 60 * 1_000_000_000)
    write_file(f15 / "old", b"o", mtime_ns=now_ns - 200 * 86_400 * 1_000_000_000)
    write_file(f15 / "future_30m", b"f", mtime_ns=now_ns + 30 * 60 * 1_000_000_000)

    f16 = fixtures / "F16"
    (f16 / "dir_a" / "nested").mkdir(parents=True)
    (f16 / "dir_b").mkdir()
    write_file(f16 / "root_b", b"b", mtime_ns=recent_ns)
    write_file(f16 / "root_a", b"a", mtime_ns=recent_ns)
    write_file(f16 / "dir_a" / "a_file", b"a", mtime_ns=recent_ns)
    write_file(f16 / "dir_a" / "nested" / "deep", b"d", mtime_ns=recent_ns)
    write_file(f16 / "dir_b" / "b_file", b"b", mtime_ns=recent_ns)

    f17 = fixtures / "F17"
    (f17 / ".secret").mkdir(parents=True)
    (f17 / "visible_dir").mkdir()
    write_file(f17 / ".hidden_file", b"h", mtime_ns=recent_ns)
    write_file(f17 / ".secret" / "inside_hidden", b"h", mtime_ns=recent_ns)
    write_file(f17 / "visible_dir" / "inside_visible", b"v", mtime_ns=recent_ns)

    f18 = fixtures / "F18"
    (f18 / "real_dir").mkdir(parents=True)
    write_file(f18 / "real_dir" / "inside", b"i", mtime_ns=recent_ns)
    os.symlink("real_dir", f18 / "link_to_dir")

    for suffix, filename in (("one", "one_file"), ("two", "two_file")):
        directory = fixtures / f"F19_{suffix}"
        directory.mkdir()
        write_file(directory / filename, suffix.encode(), mtime_ns=recent_ns)

    f21 = fixtures / "F21_valid"
    f21.mkdir()
    write_file(f21 / "valid_file", b"v", mtime_ns=recent_ns)
    write_file(fixtures / "F22_file", b"file operand", mtime_ns=recent_ns)

    f24 = fixtures / "F24"
    f24.mkdir()
    for name in ("plain", "has space", "has  two spaces", "has\ttab", "has\nnewline", "-leading-dash"):
        write_file(f24 / name, name.encode(), mtime_ns=recent_ns)

    f25 = fixtures / "F25"
    (f25 / "dir").mkdir(parents=True)
    (f25 / ".hidden_dir").mkdir()
    write_file(f25 / "visible", b"visible", mtime_ns=recent_ns - 2_000_000_000)
    write_file(f25 / ".hidden", b"hidden", mtime_ns=recent_ns - 1_000_000_000)
    write_file(f25 / "dir" / "nested", b"nested", mtime_ns=recent_ns)
    write_file(f25 / ".hidden_dir" / "secret", b"secret", mtime_ns=recent_ns + 1_000_000_000)
    os.symlink("visible", f25 / "link")

    return {"created_at_epoch_ns": now_ns, "fixture_root": str(fixtures)}


def file_type(mode: int) -> str:
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISFIFO(mode):
        return "fifo"
    if stat.S_ISSOCK(mode):
        return "socket"
    if stat.S_ISCHR(mode):
        return "char"
    if stat.S_ISBLK(mode):
        return "block"
    return "unknown"


def fixture_manifest(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        dirs.sort(key=os.fsencode)
        files.sort(key=os.fsencode)
        for name in dirs + files:
            path = Path(current) / name
            info = os.lstat(path)
            record: dict[str, Any] = {
                "path": os.path.relpath(path, root),
                "type": file_type(info.st_mode),
                "mode": oct(stat.S_IMODE(info.st_mode)),
                "nlink": info.st_nlink,
                "uid": info.st_uid,
                "gid": info.st_gid,
                "size": info.st_size,
                "blocks": info.st_blocks,
                "mtime_ns": info.st_mtime_ns,
            }
            if stat.S_ISLNK(info.st_mode):
                record["target"] = os.readlink(path)
            entries.append(record)
    entries.sort(key=lambda item: os.fsencode(item["path"]))
    return entries


def run_process(argv: list[str], cwd: Path) -> dict[str, Any]:
    start = time.monotonic_ns()
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=CONTROLLED_ENV,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
        return {
            "argv": argv,
            "cwd": str(cwd),
            "returncode": completed.returncode,
            "timed_out": False,
            "elapsed_ms": round((time.monotonic_ns() - start) / 1_000_000, 3),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as error:
        return {
            "argv": argv,
            "cwd": str(cwd),
            "returncode": None,
            "timed_out": True,
            "elapsed_ms": round((time.monotonic_ns() - start) / 1_000_000, 3),
            "stdout": error.stdout or b"",
            "stderr": error.stderr or b"",
        }


def text(data: bytes) -> str:
    return data.decode("utf-8", "surrogateescape")


def crash_result(target: dict[str, Any]) -> dict[str, Any] | None:
    if target["timed_out"]:
        return {"classification": "CRASH", "summary": "target timed out", "details": {"timeout_seconds": TIMEOUT_SECONDS}}
    if target["returncode"] is not None and target["returncode"] < 0:
        return {
            "classification": "CRASH",
            "summary": f"target terminated by signal {-target['returncode']}",
            "details": {"signal": -target["returncode"]},
        }
    return None


def parse_target_names(data: bytes) -> list[str]:
    value = text(data).rstrip("\n")
    if not value:
        return []
    return [item for item in value.split("  ") if item != ""]


def parse_oracle_names(data: bytes) -> list[str]:
    return text(data).splitlines()


def evaluate_names(target: dict[str, Any], oracle: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    abnormal = crash_result(target)
    if abnormal:
        return abnormal
    target_names = parse_target_names(target["stdout"])
    oracle_names = parse_oracle_names(oracle["stdout"])
    same = target_names == oracle_names
    clean = target["returncode"] == oracle["returncode"] == 0 and target["stderr"] == b""
    return {
        "classification": "PASS" if same and clean else "FAIL",
        "summary": "ordered name vector matches GNU ls" if same and clean else "ordered names or success/error behavior differ",
        "details": {
            "target_names": target_names,
            "oracle_names": oracle_names,
            "target_returncode": target["returncode"],
            "oracle_returncode": oracle["returncode"],
            "target_stderr": text(target["stderr"]),
        },
    }


def parse_long_line(line: str) -> dict[str, str]:
    fields = line.split()
    if len(fields) < 9 or len(fields[0]) < 10:
        raise ValueError(f"cannot parse long line: {line!r}")
    return {
        "mode": fields[0],
        "nlink": fields[1],
        "owner": fields[2],
        "group": fields[3],
        "size": fields[4],
        "date": " ".join(fields[5:8]),
        "name": " ".join(fields[8:]),
    }


def parse_long_listing(data: bytes) -> dict[str, Any]:
    total: str | None = None
    records: list[dict[str, str]] = []
    for line in text(data).splitlines():
        if not line.strip():
            continue
        if line.startswith("total "):
            total = line.split(maxsplit=1)[1]
            continue
        records.append(parse_long_line(line))
    return {"total": total, "records": records}


def evaluate_long(target: dict[str, Any], oracle: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    abnormal = crash_result(target)
    if abnormal:
        return abnormal
    try:
        target_data = parse_long_listing(target["stdout"])
        oracle_data = parse_long_listing(oracle["stdout"])
        parse_error = None
    except ValueError as error:
        target_data = None
        oracle_data = None
        parse_error = str(error)
    same = target_data == oracle_data and parse_error is None
    clean = target["returncode"] == oracle["returncode"] == 0 and target["stderr"] == b""
    return {
        "classification": "PASS" if same and clean else "FAIL",
        "summary": "long-format semantic records match GNU ls" if same and clean else "long-format metadata/order/error behavior differ",
        "details": {
            "target": target_data,
            "oracle": oracle_data,
            "parse_error": parse_error,
            "target_returncode": target["returncode"],
            "oracle_returncode": oracle["returncode"],
            "target_stderr": text(target["stderr"]),
        },
    }


def parse_short_sections(data: bytes, target_format: bool) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    loose_names: list[str] = []
    for line in text(data).splitlines():
        if not line:
            continue
        if line.endswith(":"):
            current = {"header": line[:-1], "names": []}
            sections.append(current)
            continue
        names = [item for item in line.split("  ") if item] if target_format else [line]
        if current is None:
            loose_names.extend(names)
        else:
            current["names"].extend(names)
    if loose_names:
        sections.insert(0, {"header": None, "names": loose_names})
    return sections


def evaluate_sections_short(target: dict[str, Any], oracle: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    abnormal = crash_result(target)
    if abnormal:
        return abnormal
    target_data = parse_short_sections(target["stdout"], True)
    oracle_data = parse_short_sections(oracle["stdout"], False)
    same = target_data == oracle_data
    clean = target["returncode"] == oracle["returncode"] == 0 and target["stderr"] == b""
    return {
        "classification": "PASS" if same and clean else "FAIL",
        "summary": "recursive/multi-operand sections match GNU ls" if same and clean else "section headings, entries, traversal order, or errors differ",
        "details": {
            "target_sections": target_data,
            "oracle_sections": oracle_data,
            "target_returncode": target["returncode"],
            "target_stderr": text(target["stderr"]),
        },
    }


def parse_long_sections(data: bytes) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in text(data).splitlines():
        if not line:
            continue
        if line.endswith(":"):
            current = {"header": line[:-1], "total": None, "records": []}
            sections.append(current)
            continue
        if current is None:
            current = {"header": None, "total": None, "records": []}
            sections.append(current)
        if line.startswith("total "):
            current["total"] = line.split(maxsplit=1)[1]
        else:
            current["records"].append(parse_long_line(line))
    return sections


def evaluate_sections_long(target: dict[str, Any], oracle: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    abnormal = crash_result(target)
    if abnormal:
        return abnormal
    try:
        target_data = parse_long_sections(target["stdout"])
        oracle_data = parse_long_sections(oracle["stdout"])
        parse_error = None
    except ValueError as error:
        target_data = None
        oracle_data = None
        parse_error = str(error)
    same = target_data == oracle_data and parse_error is None
    clean = target["returncode"] == oracle["returncode"] == 0 and target["stderr"] == b""
    return {
        "classification": "PASS" if same and clean else "FAIL",
        "summary": "combined recursive long semantics match GNU ls" if same and clean else "combined option semantics differ",
        "details": {
            "target_sections": target_data,
            "oracle_sections": oracle_data,
            "parse_error": parse_error,
            "target_returncode": target["returncode"],
            "target_stderr": text(target["stderr"]),
        },
    }


def evaluate_error(target: dict[str, Any], oracle: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    abnormal = crash_result(target)
    if abnormal:
        return abnormal
    target_nonzero = target["returncode"] not in (None, 0)
    oracle_nonzero = oracle["returncode"] not in (None, 0)
    has_target_diagnostic = bool(target["stderr"])
    equivalent_status = target["returncode"] == oracle["returncode"]
    passed = target_nonzero and oracle_nonzero and has_target_diagnostic and equivalent_status
    return {
        "classification": "PASS" if passed else "FAIL",
        "summary": "error status/channel matches GNU ls" if passed else "operand error status or diagnostic behavior differs",
        "details": {
            "target_returncode": target["returncode"],
            "oracle_returncode": oracle["returncode"],
            "target_stdout": text(target["stdout"]),
            "oracle_stdout": text(oracle["stdout"]),
            "target_stderr": text(target["stderr"]),
            "oracle_stderr": text(oracle["stderr"]),
        },
    }


def evaluate_file_operand(target: dict[str, Any], oracle: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    abnormal = crash_result(target)
    if abnormal:
        return abnormal
    same = target["stdout"] == oracle["stdout"] and target["stderr"] == oracle["stderr"] and target["returncode"] == oracle["returncode"]
    return {
        "classification": "PASS" if same else "FAIL",
        "summary": "regular-file operand matches GNU ls" if same else "regular-file operand is not listed like GNU ls",
        "details": {
            "target_returncode": target["returncode"],
            "oracle_returncode": oracle["returncode"],
            "target_stdout": text(target["stdout"]),
            "oracle_stdout": text(oracle["stdout"]),
            "target_stderr": text(target["stderr"]),
            "oracle_stderr": text(oracle["stderr"]),
        },
    }


def evaluate_invalid_option(target: dict[str, Any], oracle: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    abnormal = crash_result(target)
    if abnormal:
        return abnormal
    passed = (
        target["returncode"] == oracle["returncode"]
        and target["returncode"] not in (None, 0)
        and bool(target["stderr"])
        and target["stdout"] == b""
    )
    return {
        "classification": "PASS" if passed else "FAIL",
        "summary": "invalid-option status/channel matches GNU ls" if passed else "invalid-option exit status or channel differs",
        "details": {
            "target_returncode": target["returncode"],
            "oracle_returncode": oracle["returncode"],
            "target_stderr": text(target["stderr"]),
            "oracle_stderr": text(oracle["stderr"]),
        },
    }


def evaluate_special_names(target: dict[str, Any], oracle: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    abnormal = crash_result(target)
    if abnormal:
        return abnormal
    names = context["special_names"]
    ordered = sorted((os.fsencode(name) for name in names))
    expected_target = b"".join(name + b"  " for name in ordered) + b"\n"
    oracle_names = [name for name in oracle["stdout"].split(b"\0") if name]
    target_exact = target["stdout"] == expected_target
    oracle_exact = oracle_names == ordered
    clean = target["returncode"] == oracle["returncode"] == 0 and target["stderr"] == b""
    if target_exact and oracle_exact and clean:
        classification = "PARTIAL"
        summary = "all filename bytes are emitted, but whitespace/newline delimiters are ambiguous"
    else:
        classification = "FAIL"
        summary = "special filenames are missing, reordered, corrupted, or error behavior differs"
    return {
        "classification": classification,
        "summary": summary,
        "details": {
            "target_matches_expected_literal_stream": target_exact,
            "oracle_nul_vector_matches_fixture": oracle_exact,
            "ordered_names_escaped": [os.fsdecode(name).encode("unicode_escape").decode() for name in ordered],
            "target_returncode": target["returncode"],
            "oracle_returncode": oracle["returncode"],
        },
    }


EVALUATORS: dict[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "names": evaluate_names,
    "long": evaluate_long,
    "sections_short": evaluate_sections_short,
    "sections_long": evaluate_sections_long,
    "error": evaluate_error,
    "file_operand": evaluate_file_operand,
    "invalid_option": evaluate_invalid_option,
    "special_names": evaluate_special_names,
}


def serializable_process(process: dict[str, Any], raw_prefix: str) -> dict[str, Any]:
    return {
        "argv": process["argv"],
        "cwd": process["cwd"],
        "returncode": process["returncode"],
        "timed_out": process["timed_out"],
        "elapsed_ms": process["elapsed_ms"],
        "stdout_file": f"{raw_prefix}.stdout",
        "stderr_file": f"{raw_prefix}.stderr",
    }


def oracle_argv(case: dict[str, Any]) -> list[str]:
    argv = [str(ORACLE), "--color=never", "--quoting-style=literal", "-1"]
    if "l" in "".join(case["options"]):
        argv.append("--time-style=locale")
    if case["evaluator"] == "special_names":
        argv.append("--zero")
    return argv + case["options"] + case["operands"]


def main() -> int:
    if not ORACLE.is_file():
        raise SystemExit(f"missing pinned oracle: {ORACLE}")
    version = subprocess.run([str(ORACLE), "--version"], stdout=subprocess.PIPE, check=True, env=CONTROLLED_ENV).stdout
    if b"GNU coreutils" not in version:
        raise SystemExit("pinned oracle is not GNU coreutils ls")

    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_root = AUDIT / "raw" / run_id
    suffix = 1
    while run_root.exists():
        run_root = AUDIT / "raw" / f"{run_id}-{suffix}"
        suffix += 1
    run_root.mkdir(parents=True)

    build = subprocess.run(["make"], cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    (run_root / "build.stdout").write_bytes(build.stdout)
    (run_root / "build.stderr").write_bytes(build.stderr)
    if build.returncode != 0 or not TARGET.is_file():
        raise SystemExit(f"build failed; see {run_root}")

    creation = create_fixtures(run_root)
    manifest = fixture_manifest(run_root / "fixtures")
    (run_root / "fixture_manifest.json").write_text(json.dumps({**creation, "entries": manifest}, indent=2, ensure_ascii=False) + "\n")

    cases = json.loads(CASES_FILE.read_text())
    special_names = ["plain", "has space", "has  two spaces", "has\ttab", "has\nnewline", "-leading-dash"]
    results: list[dict[str, Any]] = []

    for case in cases:
        case_root = run_root / case["id"]
        case_root.mkdir()
        cwd = run_root / case["cwd"]
        target_argv = [str(TARGET)] + case["options"] + case["operands"]
        target_result = run_process(target_argv, cwd)
        oracle_result = run_process(oracle_argv(case), cwd)
        if oracle_result["timed_out"] or (oracle_result["returncode"] is not None and oracle_result["returncode"] < 0):
            raise SystemExit(f"oracle failure in {case['id']}")

        (case_root / "target.stdout").write_bytes(target_result["stdout"])
        (case_root / "target.stderr").write_bytes(target_result["stderr"])
        (case_root / "oracle.stdout").write_bytes(oracle_result["stdout"])
        (case_root / "oracle.stderr").write_bytes(oracle_result["stderr"])

        evaluation = EVALUATORS[case["evaluator"]](
            target_result,
            oracle_result,
            {"special_names": special_names},
        )
        results.append(
            {
                "id": case["id"],
                "title": case["title"],
                "evaluator": case["evaluator"],
                **evaluation,
                "target": serializable_process(target_result, f"{case['id']}/target"),
                "oracle": serializable_process(oracle_result, f"{case['id']}/oracle"),
            }
        )

    counts = {name: sum(item["classification"] == name for item in results) for name in ("PASS", "PARTIAL", "FAIL", "CRASH")}
    report = {
        "schema_version": 1,
        "run_id": run_root.name,
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, stdout=subprocess.PIPE, text=True, check=True).stdout.strip(),
        "environment": CONTROLLED_ENV,
        "target": {"path": str(TARGET), "sha256": sha256(TARGET)},
        "oracle": {
            "path": str(ORACLE),
            "sha256": sha256(ORACLE),
            "version": text(version).splitlines()[0],
            "provenance": "/snap/core24/1643/usr/bin/ls",
        },
        "case_count": len(results),
        "counts": counts,
        "results": results,
        "raw_root": str(run_root),
    }
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    (run_root / "results.json").write_text(encoded)
    (AUDIT / "test_results.json").write_text(encoded)
    (AUDIT / "raw" / "LATEST").write_text(run_root.name + "\n")
    print(json.dumps({"run_id": run_root.name, "counts": counts, "results": [(item["id"], item["classification"]) for item in results]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
