# Issue Dashboard

這個專案包含一個靜態 GitHub Issues 儀表板與週報自動化流程。

## GitHub Pages

網站網址：[https://nicklai12.github.io/issue-dashboard/](https://nicklai12.github.io/issue-dashboard/)

儀表板會直接從 GitHub API 抓取本倉庫的 open issues 並顯示。

## 腳本

| 腳本 | 說明 |
|------|------|
| `scripts/fetch_issues.py` | 從 GitHub API 抓取最近 7 天的 issues，輸出 JSON 到 stdout |
| `scripts/generate_report.py` | 從 stdin 讀取 issues JSON，透過 GitHub Models 產生繁體中文週報 |
| `scripts/create_issue.py` | 從 stdin 讀取週報文字，建立一個標題固定格式的 GitHub Issue |

## 環境變數

| 變數 | 說明 |
|------|------|
| `GITHUB_TOKEN` | GitHub 認證 token，用於 API 與 GitHub Models |
| `REPO_OWNER` | 倉庫擁有者 |
| `REPO_NAME` | 倉庫名稱 |
| `AI_MODEL` | 使用的模型名稱（預設 `gpt-4o-mini`） |
| `DAYS_BACK` | 抓取幾天內的 issues（預設 `7`） |

## 本機執行完整週報流程

```bash
export REPO_OWNER=nicklai12
export REPO_NAME=issue-dashboard
python scripts/fetch_issues.py | python scripts/generate_report.py | python scripts/create_issue.py
```

## GitHub Actions Workflows

| Workflow | 說明 |
|----------|------|
| `.github/workflows/deploy.yml` | 推送 `main` 時自動部署 `docs/` 到 GitHub Pages |
| `.github/workflows/weekly-report.yml` | 每週一 UTC 01:00 自動產生並建立週報 issue，也支援手動觸發 |
