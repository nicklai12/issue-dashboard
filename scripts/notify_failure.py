#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main():
    failure_reason = sys.argv[1] if len(sys.argv) > 1 else "週報 workflow 執行失敗，請查看 Actions log"

    token = os.environ.get("GITHUB_TOKEN")
    owner = os.environ.get("REPO_OWNER")
    repo = os.environ.get("REPO_NAME")
    actions_run_url = os.environ.get("ACTIONS_RUN_URL", "")

    if not owner or not repo:
        print("REPO_OWNER and REPO_NAME must be set", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    title = f"⚠️ 週報產生失敗 - {today_str}"

    body_lines = [
        f"失敗原因：{failure_reason}",
        "",
        f"執行時間：{timestamp}",
    ]
    if actions_run_url:
        body_lines.append(f"Actions 執行連結：{actions_run_url}")
    body_lines.extend([
        "",
        "請人工查看 Actions log 並確認問題。",
    ])
    body = "\n".join(body_lines)

    payload = {
        "title": title,
        "body": body,
        "labels": ["alert", "auto-generated"],
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
