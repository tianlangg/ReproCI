"""Create a local linear demo repository with an injected regression."""

import argparse
import json
import os
import subprocess
from pathlib import Path


def git(cwd, *args):
    environment = os.environ.copy()
    # Fixed author and committer time makes the demonstration SHAs reproducible.
    environment["GIT_AUTHOR_DATE"] = "2026-10-27T00:43:44-04:00"
    environment["GIT_COMMITTER_DATE"] = "2026-10-27T00:43:44-04:00"
    return subprocess.check_output(["git", *args], cwd=cwd, text=True, env=environment).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    path = args.path.resolve()
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "ReproCI Demo")
    git(path, "config", "user.email", "demo@example.invalid")
    (path / "tests").mkdir(exist_ok=True)
    (path / "tests" / "test_total.py").write_text(
        "from totals import total\n\ndef test_total():\n    assert total([1, 2, 3]) == 6\n"
    )
    (path / "tests" / "test_flaky.py").write_text(
        "import secrets\n\ndef test_synthetic_flaky():\n"
        "    draw = secrets.randbelow(2)\n"
        "    assert draw == 0, f'synthetic random draw={draw}'\n"
    )
    (path / "tests" / "test_work.py").write_text(
        "import time\n\ndef test_independent_two_second_work():\n"
        "    time.sleep(2)\n    assert True\n"
    )
    shas = []
    for i in range(8):
        implementation = "return sum(values)" if i < 4 else "return sum(values) + 1"
        (path / "totals.py").write_text(
            f"def total(values):\n    {implementation}\n\nVERSION = {i}\n"
        )
        git(path, "add", ".")
        git(path, "commit", "-m", f"demo commit {i + 1}")
        shas.append(git(path, "rev-parse", "HEAD"))
    print(
        json.dumps(
            {
                "path": str(path),
                "good": shas[3],
                "first_bad": shas[4],
                "bad": shas[-1],
                "history": shas,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
