#!/usr/bin/env python3
import json
import os
import sys


AUTO_LABELS = {"weekly-report", "auto-generated"}
DEFAULT_MAX_ISSUES = 20


def main():
    max_issues = int(os.environ.get("MAX_ISSUES", str(DEFAULT_MAX_ISSUES)))

    raw = sys.stdin.read()
    if not raw.strip():
        print("本週無新 Issues，跳過週報產生", file=sys.stderr)
        sys.exit(2)

    try:
        issues = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"輸入不是有效的 JSON: {e}", file=sys.stderr)
        sys.exit(1)

    original_count = len(issues)

    # 篩選 1 — 空值守衛
    if original_count == 0:
        print("本週無新 Issues，跳過週報產生", file=sys.stderr)
        sys.exit(2)

    # 篩選 2 — 去除 AI 自動產生的 Issues
    filtered = []
    for issue in issues:
        labels = set(issue.get("labels", []))
        if labels & AUTO_LABELS:
            continue
        filtered.append(issue)

    # 篩選 3 — 數量上限截斷（最新的優先）
    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    if len(filtered) > max_issues:
        filtered = filtered[:max_issues]
        print(f"Issues 數量超過上限，截斷至 {max_issues} 筆", file=sys.stderr)

    if len(filtered) == 0:
        print("全部為自動產生 Issues，跳過週報產生", file=sys.stderr)
        sys.exit(2)

    print(json.dumps(filtered, ensure_ascii=False))
    print(f"篩選完成：{original_count} → {len(filtered)} 筆", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
