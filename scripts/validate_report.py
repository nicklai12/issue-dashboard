#!/usr/bin/env python3
import json
import os
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


REQUIRED_SECTIONS = [
    "## 本週摘要",
    "## Bug 分析",
    "## Todo 分析",
    "## 建議優先處理",
]
ISSUE_URL_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/issues/(\d+)/?$")


def parse_issue_url(issue_url):
    match = ISSUE_URL_RE.match(issue_url)
    if not match:
        print(f"無法解析 Issue URL: {issue_url}", file=sys.stderr)
        sys.exit(1)
    return match.group(1), match.group(2), int(match.group(3))


def fetch_issue(owner, repo, issue_number):
    token = os.environ.get("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    request = Request(url, method="GET")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")

    try:
        with urlopen(request) as response:
            if response.status != 200:
                print(f"FAIL: Issue 不存在或無法存取（HTTP {response.status}）")
                sys.exit(1)
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        print(f"FAIL: Issue 不存在或無法存取（HTTP {e.code}）")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: Issue 不存在或無法存取（{e}）")
        sys.exit(1)


def validate_issue(issue, issue_number):
    # 檢查 1：狀態是否為 open
    state = issue.get("state")
    if state != "open":
        print(f"FAIL: Issue 狀態不是 open（實際狀態：{state}）")
        sys.exit(1)

    # 檢查 2：body 是否包含必要的四個區塊標題
    body = issue.get("body") or ""
    missing = [section for section in REQUIRED_SECTIONS if section not in body]
    if missing:
        print(f"FAIL: 缺少必要區塊 {missing}")
        sys.exit(1)

    # 檢查 3：是否有 weekly-report label
    labels = [label.get("name") for label in issue.get("labels", [])]
    if "weekly-report" not in labels:
        print("FAIL: 缺少 weekly-report label")
        sys.exit(1)

    print(f"PASS: 週報驗收通過（Issue #{issue_number}）")
    sys.exit(0)


def main():
    if len(sys.argv) != 2:
        print("用法：python scripts/validate_report.py {issue_url}", file=sys.stderr)
        sys.exit(1)

    issue_url = sys.argv[1]
    owner, repo, issue_number = parse_issue_url(issue_url)
    issue = fetch_issue(owner, repo, issue_number)
    validate_issue(issue, issue_number)


if __name__ == "__main__":
    main()
