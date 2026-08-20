#!/usr/bin/env python3
"""Fetch GitHub's rolling traffic window and merge it into daily history."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DATA_FILE = Path(__file__).with_name("traffic.json")
API_VERSION = "2026-03-10"


def fetch(endpoint: str, repository: str, token: str) -> dict:
    url = f"https://api.github.com/repos/{repository}/traffic/{endpoint}?per=day"
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "github-traffic-history-workflow",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {endpoint} request failed ({error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"GitHub API {endpoint} request failed: {error.reason}") from error


def merge_daily(existing: list[dict], views: list[dict], clones: list[dict]) -> list[dict]:
    """Upsert metrics by UTC date; never add overlapping 14-day totals."""
    by_date = {row["date"]: dict(row) for row in existing}

    for item in views:
        date = item["timestamp"][:10]
        row = by_date.setdefault(date, {"date": date})
        row["views"] = item["count"]
        row["unique_visitors"] = item["uniques"]

    for item in clones:
        date = item["timestamp"][:10]
        row = by_date.setdefault(date, {"date": date})
        row["clones"] = item["count"]
        row["unique_cloners"] = item["uniques"]

    return [by_date[date] for date in sorted(by_date)]


def main() -> int:
    token = os.environ.get("GH_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token:
        print("GH_TOKEN is required", file=sys.stderr)
        return 2
    if not repository:
        print("GITHUB_REPOSITORY is required", file=sys.stderr)
        return 2

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    views = fetch("views", repository, token)
    clones = fetch("clones", repository, token)
    merged = merge_daily(data.get("daily", []), views.get("views", []), clones.get("clones", []))

    changed = merged != data.get("daily", []) or repository != data.get("repository")
    new_data = {
        "repository": repository,
        "updated_at": (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            if changed
            else data.get("updated_at")
        ),
        "daily": merged,
    }
    DATA_FILE.write_text(json.dumps(new_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
