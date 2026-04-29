#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILD_DIR = Path(
    os.environ.get("MINIPYCC_TEST_OUT", Path(tempfile.gettempdir()) / "minipycc-tests")
)


@dataclass(frozen=True)
class TestCase:
    name: str
    source: str
    expect_success: bool
    expected_stdout: str = ""
    expected_message: str = ""
    emit: str = "llvm,exe"


TESTS = [
    TestCase("valid_fact", "testcases/valid/fact.py", True, "-28183\n"),
    TestCase("valid_fib", "testcases/valid/fib.py", True, "55\n"),
    TestCase("valid_cond", "testcases/valid/cond.py", True, "11\n"),
    TestCase("valid_gcd", "testcases/valid/gcd.py", True, "2\n"),
    TestCase("valid_aviral", "testcases/valid/aviral.py", True, "8\n"),
    TestCase(
        "invalid_undef",
        "testcases/invalid/undef.py",
        False,
        expected_message="Undefined variable 'missing_value'",
    ),
    TestCase(
        "invalid_indent",
        "testcases/invalid/indent.py",
        False,
        expected_message="Unindent does not match any outer indentation level",
    ),
]


def main() -> int:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    failures = []
    for case in TESTS:
        ok, details = run_case(case)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case.name}")
        if not ok:
            failures.append((case.name, details))

    if failures:
        print("\nFailures:")
        for name, details in failures:
            print(f"\n{name}:")
            print(details.rstrip())
        return 1

    print(f"\n{len(TESTS)} tests passed.")
    return 0


def run_case(case: TestCase) -> tuple[bool, str]:
    out_dir = BUILD_DIR / case.name
    cmd = [
        sys.executable,
        "minipycc",
        "compile",
        case.source,
        "--out",
        str(out_dir),
        "--emit",
        case.emit,
    ]
    if case.expect_success:
        cmd.append("--run")

    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    manifest = load_manifest(out_dir)
    manifest_status = manifest.get("status")

    if case.expect_success:
        if result.returncode != 0:
            return False, format_process_failure(cmd, result)
        if manifest_status != "success":
            return False, f"Expected manifest status success, got {manifest_status!r}"

        run_output_path = out_dir / "run_output.txt"
        if not run_output_path.exists():
            return False, "Expected run_output.txt to be emitted"
        actual_stdout = run_output_path.read_text()
        if actual_stdout != case.expected_stdout:
            return (
                False,
                "Unexpected program output\n"
                f"expected: {case.expected_stdout!r}\n"
                f"actual:   {actual_stdout!r}",
            )
        return True, ""

    if result.returncode == 0:
        return False, "Expected compile failure, but command succeeded"
    if manifest_status != "fail":
        return False, f"Expected manifest status fail, got {manifest_status!r}"

    messages = [diag.get("message", "") for diag in manifest.get("diagnostics", [])]
    if case.expected_message and not any(case.expected_message in msg for msg in messages):
        return (
            False,
            "Expected diagnostic was not found\n"
            f"expected message containing: {case.expected_message!r}\n"
            f"actual messages: {messages!r}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}",
        )
    return True, ""


def load_manifest(out_dir: Path) -> dict:
    manifest_path = out_dir / "result.json"
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text())


def format_process_failure(cmd: list[str], result: subprocess.CompletedProcess) -> str:
    return (
        f"Command failed: {' '.join(cmd)}\n"
        f"exit code: {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
