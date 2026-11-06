
import subprocess
import sys
from pathlib import Path

BASE = Path("tests/program_cfg_input_coverage")
PYTHON = sys.executable


def run_test(command, expected_file, timeout=15):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout
        )

        if result.returncode != 0:
            error_message = result.stderr.decode(
                "utf-8", errors="replace"
            ).strip()

            return (
                f"execution error (exit code {result.returncode}): "
                f"{error_message[-1000:]}"
            )

        if result.stdout != expected_file.read_bytes():
            return "output mismatch"

        return None

    except subprocess.TimeoutExpired:
        return "timeout"
    except Exception as error:
        return f"error: {error}"


def report(part, total, passed, failed):
    print()
    print(f"Part {part} Results")
    print("=" * 32)
    print(f"TOTAL: {total}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print("=" * 32)


def test_part1():
    base = BASE / "part1_program_cfg"
    total = 0
    passed = 0
    failed = 0

    for number in range(1, 11):
        name = f"program_{number:02d}"
        program = base / "programs" / f"{name}.py"
        expected = base / "expected_cfgs" / f"{name}_cfg.txt"

        total += 1
        reason = run_test(
            [PYTHON, "part1/cfg.py", str(program)],
            expected
        )

        if reason is None:
            passed += 1
        else:
            failed += 1
            print(f"[FAIL] {name}.py: {reason}", flush=True)

    report(1, total, passed, failed)
    return failed


def test_part2():
    base = BASE / "part2_program_input_coverage"
    total = 0
    passed = 0
    failed = 0

    for program_number in range(1, 11):
        name = f"program_{program_number:02d}"
        program = base / "programs" / f"{name}.py"

        for input_number in range(1, 101):
            input_name = f"input_{input_number:03d}"
            input_file = (
                base / "inputs" / name / f"{input_name}.txt"
            )
            expected = (
                base / "expected_cov" / name
                / f"{input_name}_cov.txt"
            )

            total += 1
            reason = run_test(
                [
                    PYTHON,
                    "part2/coverage.py",
                    str(program),
                    str(input_file)
                ],
                expected
            )

            if reason is None:
                passed += 1
            else:
                failed += 1
                print(
                    f"[FAIL] {name}.py / "
                    f"{input_name}.txt: {reason}",
                    flush=True
                )

        print(
            f"Part 2: {name} completed",
            flush=True
        )

    report(2, total, passed, failed)
    return failed


if __name__ == "__main__":
    part1_failures = test_part1()
    part2_failures = test_part2()

    if part1_failures or part2_failures:
        sys.exit(1)

    sys.exit(0)
