import json
import subprocess
import sys
from pathlib import Path


def test_demo_history_has_reproducible_regression(tmp_path):
    script = Path(__file__).parents[2] / "demo" / "create_history.py"
    output = subprocess.check_output(
        [sys.executable, str(script), str(tmp_path / "history")], text=True
    )
    history = json.loads(output)
    assert history["good"] == "cb77de5fa7cacd525999a8b96671e67e3958fea2"
    assert history["first_bad"] == "fcb686a494ec4b61bb38ebc5e3356a13d725c778"
    assert history["bad"] == "752e6b30b7399d3834646b294f1ae6a90ccbab8b"
