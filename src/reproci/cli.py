import argparse
import json
from pathlib import Path

import httpx

from .config import settings


def main():
    parser = argparse.ArgumentParser(prog="reproci")
    parser.add_argument("--api", default=settings.api_url)
    sub = parser.add_subparsers(dest="command", required=True)
    repo = sub.add_parser("repo")
    repo_sub = repo.add_subparsers(dest="action", required=True)
    add = repo_sub.add_parser("add")
    add.add_argument("name")
    add.add_argument("--url", required=True)
    add.add_argument("--branch", default="main")
    add.add_argument("--image-id", required=True)
    run = sub.add_parser("run")
    run.add_argument("repository")
    run.add_argument("--commit", required=True)
    status = sub.add_parser("status")
    status.add_argument("run_id")
    tests = sub.add_parser("tests")
    tests.add_argument("run_id")
    for name in ("replay", "flakes", "bisect"):
        p = sub.add_parser(name)
        p.add_argument("attempt_id")
        p.add_argument("--test", required=True)
        if name == "flakes":
            p.add_argument("--repeats", type=int, default=10)
        if name == "bisect":
            p.add_argument("--good", required=True)
            p.add_argument("--bad", required=True)
    job = sub.add_parser("job")
    job.add_argument("job_id")
    cancel = sub.add_parser("cancel")
    cancel.add_argument("job_id")
    retry = sub.add_parser("retry")
    retry.add_argument("job_id")
    report = sub.add_parser("report")
    report.add_argument("run_id")
    report.add_argument("--output", required=True)
    args = parser.parse_args()
    with httpx.Client(base_url=args.api, timeout=20) as client:
        if args.command == "repo":
            response = client.post(
                "/repositories",
                json={
                    "name": args.name,
                    "url": args.url,
                    "branch": args.branch,
                    "image_id": args.image_id,
                },
            )
        elif args.command == "run":
            response = client.post(
                "/runs", json={"repository": args.repository, "commit": args.commit}
            )
        elif args.command == "status":
            response = client.get(f"/runs/{args.run_id}")
        elif args.command == "tests":
            response = client.get(f"/runs/{args.run_id}/tests")
        elif args.command in ("replay", "flakes", "bisect"):
            data = {"test": args.test}
            if args.command == "flakes":
                data["repeats"] = args.repeats
            if args.command == "bisect":
                data.update(good=args.good, bad=args.bad)
            response = client.post(f"/attempts/{args.attempt_id}/{args.command}", json=data)
        elif args.command == "job":
            response = client.get(f"/jobs/{args.job_id}")
        elif args.command == "cancel":
            response = client.post(f"/jobs/{args.job_id}/cancel")
        elif args.command == "retry":
            response = client.post(f"/jobs/{args.job_id}/retry")
        else:
            response = client.get(f"/runs/{args.run_id}/report")
            response.raise_for_status()
            Path(args.output).write_text(response.text)
            print(args.output)
            return
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2, default=str))


if __name__ == "__main__":
    main()
