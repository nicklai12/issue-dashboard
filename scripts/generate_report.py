#!/usr/bin/env python3
import json
import os
import sys

from openai import OpenAI


def main():
    issues = json.load(sys.stdin)

    lines = []
    for issue in issues:
        lines.append(f"Issue #{issue.get('number')}: {issue.get('title')}")
        lines.append(f"URL: {issue.get('html_url')}")
        lines.append(f"State: {issue.get('state')}")
        lines.append(f"Labels: {', '.join(issue.get('labels', []))}")
        lines.append(f"Created at: {issue.get('created_at')}")
        lines.append("---")

    issues_text = "\n".join(lines)

    system_prompt = "你是一個專案助理，負責分析 GitHub Issues 並產生繁體中文週報。"
    user_prompt = (
        "請根據以下 GitHub Issues 內容產生一份繁體中文週報。\n\n"
        "請務必輸出以下四個區塊，即使 Issues 列表為空也請保留標題並標示無資料：\n"
        "## 本週摘要\n"
        "## Bug 分析\n"
        "## Todo 分析\n"
        "## 建議優先處理\n\n"
        "Issues 內容如下：\n\n" + issues_text
    )

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    model = os.environ.get("AI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
