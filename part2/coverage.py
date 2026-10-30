import sys
import os
import subprocess
import tempfile

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path = [
    path for path in sys.path
    if os.path.abspath(path) != script_dir
]

import coverage


def main():
    if len(sys.argv) != 3:
        print("Usage: python coverage.py <python_file> <input_file>")
        return

    filename = os.path.abspath(sys.argv[1])
    input_filename = sys.argv[2]

    with open(filename, "r") as file:
        source_lines = file.read().splitlines()

    with open(input_filename, "r") as file:
        arguments = file.read().split()

    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, ".coverage")
        config_file = os.path.join(temp_dir, ".coveragerc")

        # Allow coverage to save data when receiving SIGTERM
        with open(config_file, "w") as file:
            file.write("[run]\nsigterm = true\n")

        command = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--rcfile",
            config_file,
            "--data-file",
            data_file,
            filename,
            *arguments
        ]

        # Run the program and handle infinite loops
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=temp_dir
        )

        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            # Request graceful termination
            process.terminate()

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        # Read coverage results
        cov = coverage.Coverage(data_file=data_file)

        if os.path.exists(data_file):
            cov.load()

            try:
                executed = cov.get_data().lines(filename) or []
            except coverage.CoverageException:
                executed = []
        else:
            executed = []

    executed = set(executed)

    output = []

    for line_number, line in enumerate(source_lines, start=1):
        prefix = "  " if line_number in executed else "# "

        if not line.strip():
            line = ""

        output.append(f"{prefix}{line_number:4}: {line}")

    # Print output with a final newline
    sys.stdout.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
