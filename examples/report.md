# ReproCI evidence report

Repository: `ci-demo-3118dd93`
Commit: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Branch: `main`
Trigger: `manual`
Run ID: `6bddfca6-ba82-4bdc-9cec-262a7ea20074`

## suite: `31a208ba-636a-4dea-b3ef-c9e62ddea126`

State: **failed**
Started: 2026-10-27 04:50:14.035072+00:00; ended: 2026-10-27 04:50:16.679201+00:00

### Attempt `b39b652e-8e02-45bf-a99b-9b8158332aa6`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `none`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml']`
Fingerprint: `afd9c624e3a06ba059225bf541690b8f5a842093eecce341231e17fe5bb9cb43`
Artifacts: `/artifacts/attempts/b39b652e-8e02-45bf-a99b-9b8158332aa6`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s
- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError
- `tests/test_work.py::test_independent_two_second_work`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 2.001s

## replay: `4266fd5b-cfe6-46e7-916c-7ce1345f6d0e`

State: **failed**
Started: 2026-10-27 04:50:18.070563+00:00; ended: 2026-10-27 04:50:18.646452+00:00

### Attempt `b216141e-0d8b-477c-9af1-bfb101856c39`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/b216141e-0d8b-477c-9af1-bfb101856c39`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

## bisect: `655b5822-4d1c-4b5d-aeaf-89b03d9c28c4`

State: **passed**
Started: 2026-10-27 04:50:19.084978+00:00; ended: 2026-10-27 04:50:29.988018+00:00

### Attempt `ad0d32f3-b501-485c-ae34-f2d95925453f`

Source SHA: `cb77de5fa7cacd525999a8b96671e67e3958fea2`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/ad0d32f3-b501-485c-ae34-f2d95925453f`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `5b11e1a1-be38-4fe1-9d4f-bde15f925ae1`

Source SHA: `cb77de5fa7cacd525999a8b96671e67e3958fea2`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/5b11e1a1-be38-4fe1-9d4f-bde15f925ae1`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `2156a01a-efc6-469b-912b-7bee238fad61`

Source SHA: `cb77de5fa7cacd525999a8b96671e67e3958fea2`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/2156a01a-efc6-469b-912b-7bee238fad61`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `604fb6e9-ff2c-46a6-b2b3-aa7959457de3`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/604fb6e9-ff2c-46a6-b2b3-aa7959457de3`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `1011a5ac-fc02-428a-8571-b2e89b5751c4`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/1011a5ac-fc02-428a-8571-b2e89b5751c4`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `48e36983-45ab-4d3b-98cb-1578442a1d03`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/48e36983-45ab-4d3b-98cb-1578442a1d03`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `7958676b-7de1-4263-afb8-0e624b4a4438`

Source SHA: `9d459cdb45319760f8239607944580993961610b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/7958676b-7de1-4263-afb8-0e624b4a4438`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `ee1ce80e-bb4d-476b-ade5-622448740b23`

Source SHA: `9d459cdb45319760f8239607944580993961610b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/ee1ce80e-bb4d-476b-ade5-622448740b23`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `5cb1b473-fd7e-447e-9480-6ca1a1b03a91`

Source SHA: `9d459cdb45319760f8239607944580993961610b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/5cb1b473-fd7e-447e-9480-6ca1a1b03a91`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `205f9269-d369-431b-b237-9ae6a45efe35`

Source SHA: `fcb686a494ec4b61bb38ebc5e3356a13d725c778`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/205f9269-d369-431b-b237-9ae6a45efe35`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `1e44ce97-95e0-4c4d-856f-face333633e8`

Source SHA: `fcb686a494ec4b61bb38ebc5e3356a13d725c778`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/1e44ce97-95e0-4c4d-856f-face333633e8`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `8d1c2ef0-e7cc-48c6-adb2-4a189fd3ee0e`

Source SHA: `fcb686a494ec4b61bb38ebc5e3356a13d725c778`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/8d1c2ef0-e7cc-48c6-adb2-4a189fd3ee0e`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `0666d233-bd78-4efa-a10f-9f36f9e940bc`

Source SHA: `cb77de5fa7cacd525999a8b96671e67e3958fea2`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/0666d233-bd78-4efa-a10f-9f36f9e940bc`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `a7591264-7ff8-48a7-8f51-1f7580e3da51`

Source SHA: `cb77de5fa7cacd525999a8b96671e67e3958fea2`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/a7591264-7ff8-48a7-8f51-1f7580e3da51`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `e4731f75-92c5-4ec9-b4bc-3dd2d7bc6bcf`

Source SHA: `cb77de5fa7cacd525999a8b96671e67e3958fea2`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/e4731f75-92c5-4ec9-b4bc-3dd2d7bc6bcf`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `8bc0873b-3310-4e07-ab8d-766970e8896c`

Source SHA: `fcb686a494ec4b61bb38ebc5e3356a13d725c778`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/8bc0873b-3310-4e07-ab8d-766970e8896c`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `563f47fe-32e3-4180-8d4f-cca8b5b16a31`

Source SHA: `fcb686a494ec4b61bb38ebc5e3356a13d725c778`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/563f47fe-32e3-4180-8d4f-cca8b5b16a31`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

### Attempt `a179b79d-c62f-4da8-9330-199903d68b1b`

Source SHA: `fcb686a494ec4b61bb38ebc5e3356a13d725c778`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_total.py::test_total']`
Fingerprint: `8a8ac5abc80ee4a3b4a3e170e35268c9a8a657f7af171aac9df9cef3a913ca8e`
Artifacts: `/artifacts/attempts/a179b79d-c62f-4da8-9330-199903d68b1b`
Error: none

- `tests/test_total.py::test_total`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_total.py:4: AssertionError

Classification: **first_bad_found**
First bad commit: `fcb686a494ec4b61bb38ebc5e3356a13d725c778`
Explanation: First observed breaking commit under fixed image and linear-history assumptions
Evidence: `{'cb77de5fa7cacd525999a8b96671e67e3958fea2': {'attempts': [['ad0d32f3-b501-485c-ae34-f2d95925453f', 'passed'], ['5b11e1a1-be38-4fe1-9d4f-bde15f925ae1', 'passed'], ['2156a01a-efc6-469b-912b-7bee238fad61', 'passed']], 'verdict': 'all_passed'}, '752e6b30b7399d3834646b294f1ae6a90ccbab8b': {'attempts': [['604fb6e9-ff2c-46a6-b2b3-aa7959457de3', 'failed'], ['1011a5ac-fc02-428a-8571-b2e89b5751c4', 'failed'], ['48e36983-45ab-4d3b-98cb-1578442a1d03', 'failed']], 'verdict': 'all_failed'}, '9d459cdb45319760f8239607944580993961610b': {'attempts': [['7958676b-7de1-4263-afb8-0e624b4a4438', 'failed'], ['ee1ce80e-bb4d-476b-ade5-622448740b23', 'failed'], ['5cb1b473-fd7e-447e-9480-6ca1a1b03a91', 'failed']], 'verdict': 'all_failed'}, 'fcb686a494ec4b61bb38ebc5e3356a13d725c778': {'attempts': [['205f9269-d369-431b-b237-9ae6a45efe35', 'failed'], ['1e44ce97-95e0-4c4d-856f-face333633e8', 'failed'], ['8d1c2ef0-e7cc-48c6-adb2-4a189fd3ee0e', 'failed']], 'verdict': 'all_failed'}, 'confirm:cb77de5fa7cacd525999a8b96671e67e3958fea2': {'attempts': [['0666d233-bd78-4efa-a10f-9f36f9e940bc', 'passed'], ['a7591264-7ff8-48a7-8f51-1f7580e3da51', 'passed'], ['e4731f75-92c5-4ec9-b4bc-3dd2d7bc6bcf', 'passed']], 'verdict': 'all_passed'}, 'confirm:fcb686a494ec4b61bb38ebc5e3356a13d725c778': {'attempts': [['8bc0873b-3310-4e07-ab8d-766970e8896c', 'failed'], ['563f47fe-32e3-4180-8d4f-cca8b5b16a31', 'failed'], ['a179b79d-c62f-4da8-9330-199903d68b1b', 'failed']], 'verdict': 'all_failed'}}`

## flake: `c6575c24-0629-44c8-be73-ca58b3dd6c77`

State: **passed**
Started: 2026-10-27 06:51:17.568602+00:00; ended: 2026-10-27 06:51:23.764895+00:00

### Attempt `e98de2a8-d6ee-445f-be23-2547af010536`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/e98de2a8-d6ee-445f-be23-2547af010536`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_flaky.py:5: AssertionError

### Attempt `a83e13f9-aa0b-4a46-b926-ec38b44db5f3`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/a83e13f9-aa0b-4a46-b926-ec38b44db5f3`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `0386ba54-7c25-460b-8770-e8e657f5833f`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/0386ba54-7c25-460b-8770-e8e657f5833f`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_flaky.py:5: AssertionError

### Attempt `bdb6feed-5eeb-4969-920d-4e7495091693`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/bdb6feed-5eeb-4969-920d-4e7495091693`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_flaky.py:5: AssertionError

### Attempt `5d3e056e-63d0-4420-8960-bf942cd6ac18`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/5d3e056e-63d0-4420-8960-bf942cd6ac18`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_flaky.py:5: AssertionError

### Attempt `6a9c1de8-9d50-4872-b42e-572ed1573a39`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/6a9c1de8-9d50-4872-b42e-572ed1573a39`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `86586dde-5769-4840-b866-16455524b9a7`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **failed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/86586dde-5769-4840-b866-16455524b9a7`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'failed', 'teardown': 'passed'}; 0.000s
  - Failure: tests/test_flaky.py:5: AssertionError

### Attempt `b7799dce-c1f3-4f37-b863-6d4707e15a03`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/b7799dce-c1f3-4f37-b863-6d4707e15a03`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `10cef04e-6a8e-407d-82c0-a50fa6ac379b`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/10cef04e-6a8e-407d-82c0-a50fa6ac379b`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

### Attempt `02d6448d-826f-4dcb-af2a-af23f5dbe34e`

Source SHA: `752e6b30b7399d3834646b294f1ae6a90ccbab8b`
Image ID: `sha256:8afb23b5939b0b94d23375109456103f8c853b54961fe987b91f59c1436a9b7f`
Outcome: **passed**
Parent attempt: `b39b652e-8e02-45bf-a99b-9b8158332aa6`
Command: `['python', '-m', 'pytest', '-p', 'pytest_plugin', '--junitxml=/output/junit.xml', 'tests/test_flaky.py::test_synthetic_flaky']`
Fingerprint: `4babb0a6315bf7cd719b159d46379e5e991ef4973c69bf0e73688251a12230bd`
Artifacts: `/artifacts/attempts/02d6448d-826f-4dcb-af2a-af23f5dbe34e`
Error: none

- `tests/test_flaky.py::test_synthetic_flaky`: {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}; 0.000s

Classification: **observed_flaky**
First bad commit: `none`
Explanation: 10 fixed-input isolated attempts; errors do not establish flakiness
Evidence: `{'counts': {'passed': 5, 'failed': 5, 'error': 0, 'cancelled': 0}, 'attempts': [{'attempt_id': 'e98de2a8-d6ee-445f-be23-2547af010536', 'outcome': 'failed', 'failure': "def test_synthetic_flaky():\n        draw = secrets.randbelow(2)\n>       assert draw == 0, f'synthetic random draw={draw}'\nE       AssertionError: synthetic random draw=1\nE       assert 1 == 0\n\ntests/test_flaky.py:5: AssertionError"}, {'attempt_id': 'a83e13f9-aa0b-4a46-b926-ec38b44db5f3', 'outcome': 'passed', 'failure': None}, {'attempt_id': '0386ba54-7c25-460b-8770-e8e657f5833f', 'outcome': 'failed', 'failure': "def test_synthetic_flaky():\n        draw = secrets.randbelow(2)\n>       assert draw == 0, f'synthetic random draw={draw}'\nE       AssertionError: synthetic random draw=1\nE       assert 1 == 0\n\ntests/test_flaky.py:5: AssertionError"}, {'attempt_id': 'bdb6feed-5eeb-4969-920d-4e7495091693', 'outcome': 'failed', 'failure': "def test_synthetic_flaky():\n        draw = secrets.randbelow(2)\n>       assert draw == 0, f'synthetic random draw={draw}'\nE       AssertionError: synthetic random draw=1\nE       assert 1 == 0\n\ntests/test_flaky.py:5: AssertionError"}, {'attempt_id': '5d3e056e-63d0-4420-8960-bf942cd6ac18', 'outcome': 'failed', 'failure': "def test_synthetic_flaky():\n        draw = secrets.randbelow(2)\n>       assert draw == 0, f'synthetic random draw={draw}'\nE       AssertionError: synthetic random draw=1\nE       assert 1 == 0\n\ntests/test_flaky.py:5: AssertionError"}, {'attempt_id': '6a9c1de8-9d50-4872-b42e-572ed1573a39', 'outcome': 'passed', 'failure': None}, {'attempt_id': '86586dde-5769-4840-b866-16455524b9a7', 'outcome': 'failed', 'failure': "def test_synthetic_flaky():\n        draw = secrets.randbelow(2)\n>       assert draw == 0, f'synthetic random draw={draw}'\nE       AssertionError: synthetic random draw=1\nE       assert 1 == 0\n\ntests/test_flaky.py:5: AssertionError"}, {'attempt_id': 'b7799dce-c1f3-4f37-b863-6d4707e15a03', 'outcome': 'passed', 'failure': None}, {'attempt_id': '10cef04e-6a8e-407d-82c0-a50fa6ac379b', 'outcome': 'passed', 'failure': None}, {'attempt_id': '02d6448d-826f-4dcb-af2a-af23f5dbe34e', 'outcome': 'passed', 'failure': None}]}`

A single-test replay can remove test-order interactions. Flakiness is only observed within recorded repeats.

## Synthetic throughput measurement

The same eight-job batch with a two-second independent test was measured five times per mode on macOS 15.6.1 arm64, Docker 29.8.2, Docker Desktop allocation of 10 CPUs and 8,319,504,384 bytes of memory. The image ID was `sha256:067ae550d9bdcff889cdb9b6affc9fbf5af42a3730f09e6e78b224604c591839`; the source commit was `cb77de5fa7cacd525999a8b96671e67e3958fea2`.

| Worker slots | Median batch time | Range | Successful jobs |
| --- | ---: | ---: | ---: |
| 1 | 36.395 s | 35.224–38.103 s | 40/40 |
| 2 | 17.334 s | 17.102–18.303 s | 40/40 |

Measured throughput speedup: **2.10×**. Image build and initial repository creation were excluded; batch submission, fresh checkout, container startup, execution, and result persistence were included. The raw observations are in `examples/benchmark.csv`; overlapping job timestamps are in `examples/concurrency.json`.
