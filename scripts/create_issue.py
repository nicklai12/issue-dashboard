#!/usr/bin/env python3
import json
import os
import sys
from datetime import date, timedelta
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main():
    token = os.environ.get("GITHUB_TOKEN")
    owner = os.environ.get("REPO_OWNER")
    repo = os.environ.get("REPO_NAME")

    if not owner or not repo:
        print("REPO_OWNER and REPO_NAME must be set", file=sys.stderr)
        sys.exit(1)

    body_text = sys.stdin.read()

    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    title = f"📊 Weekly Report - {monday.strftime('%Y/%m/%d')} ~ {sunday.strftime('%Y/%m/%d')}"

    payload = {
        "title": title,
        "body": body_text,
        "labels": ["weekly-report"],
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")

    try:
        with urlopen(request) as response:
            if response.status != 201:
                print(f"GitHub API returned {response.status}", file=sys.stderr)
                sys.exit(1)
            issue = json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        print(f"GitHub API error: {e.code} {e.reason}\n{error_body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(issue.get("html_url"))


if __name__ == "__main__":
    main()
