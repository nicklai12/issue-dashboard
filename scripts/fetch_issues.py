#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main():
    token = os.environ.get("GITHUB_TOKEN")
    owner = os.environ.get("REPO_OWNER")
    repo = os.environ.get("REPO_NAME")
    days_back = int(os.environ.get("DAYS_BACK", "7"))

    if not owner or not repo:
        print("REPO_OWNER and REPO_NAME must be set", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days_back)
    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "state": "all",
        "per_page": "100",
        "since": since_str,
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?{urlencode(params)}"

    request = Request(url, method="GET")
    request.add_header("Accept", "application/vnd.github+json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")

    try:
        with urlopen(request) as response:
            if response.status != 200:
                print(f"GitHub API returned {response.status}", file=sys.stderr)
                sys.exit(1)
            issues = json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"GitHub API error: {e.code} {e.reason}\n{body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    cutoff = now - timedelta(days=days_back)
    result = []
    for issue in issues:
        # /issues endpoint returns both issues and pull requests; keep real issues only
        if issue.get("pull_request"):
            continue

        created_at = issue.get("created_at")
        if not created_at:
            continue

        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if created < cutoff:
            continue

        result.append(
            {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "labels": [label["name"] for label in issue.get("labels", [])],
                "created_at": created_at,
                "html_url": issue["html_url"],
            }
        )

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
