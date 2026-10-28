import json
import os
import subprocess
import sys
from pathlib import Path


def test_parameterized_node_id_is_exact(tmp_path):
    (tmp_path / "test_parameter.py").write_text(
        "import pytest\n@pytest.mark.parametrize('value', [1, 2], ids=['one', 'two'])\n"
        "def test_value(value):\n    assert value > 0\n"
    )
    result_file = tmp_path / "results.json"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(Path(__file__).parents[2] / "src" / "reproci")
    environment["REPROCI_RESULT_FILE"] = str(result_file)
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "pytest_plugin", "test_parameter.py"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    rows = json.loads(result_file.read_text())
    assert {row["node_id"] for row in rows} == {
        "test_parameter.py::test_value[one]",
        "test_parameter.py::test_value[two]",
    }
