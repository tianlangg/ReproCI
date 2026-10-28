# Synthetic demo history

Run `python demo/create_history.py /tmp/reproci-demo` to create eight linear commits.
Commit five changes `total` so `tests/test_total.py::test_total` fails. The seed-based
test is deliberately synthetic; its default seed passes. This local fixture supports
the replay and bisect demonstration. The two-second test is a synthetic scheduling
workload. The random-draw test is an intentionally synthetic intermittent fixture.
A real GitHub delivery requires publishing the
same history to a public repository you control and registering its HTTPS clone URL.
