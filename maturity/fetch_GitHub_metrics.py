#!/usr/bin/env python3
import os
import re
import csv
import sys
import time
import math
import json
import typing as t
from datetime import datetime, timezone

import requests

# --------- Input/Output ----------
INPUT_CSV = "biotools_github_map.csv"  # expects: biotoolsID, github_urls
OUTPUT_CSV = "biotools_with_metrics.csv"

# --------- Auth / HTTP -----------
if not GITHUB_TOKEN:
    sys.stderr.write("ERROR: Please set GITHUB_TOKEN in your environment.\n")
    sys.exit(1)

SESSION = requests.Session()
SESSION.headers.update(
    {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "bio.tools-metrics-script",
    }
)

GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"

# --------- URL parsing -----------
_GH_RE = re.compile(
    r"https?://(?:www\.)?github\.com/([^/\s]+)/([^/\s#?]+)", re.IGNORECASE
)


def normalize_owner_repo(owner: str, repo: str) -> str:
    owner = owner.strip().strip("/")

    # remove a trailing ".git" (optionally followed by a slash), but only if present
    repo = repo.strip().strip("/")
    repo = re.sub(r"\.git/?$", "", repo, flags=re.IGNORECASE)

    return f"{owner}/{repo}"


_GH_RE = re.compile(
    r"https?://(?:www\.)?github\.com/([^/\s]+)/([^/\s#?]+)", re.IGNORECASE
)


def parse_owner_repo(url: str):
    url = (url or "").strip().strip(" ,.;)")
    m = _GH_RE.search(url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    return normalize_owner_repo(owner, repo).split("/", 1)


# --------- HTTP helpers ----------
def _rest_get(path: str, ok=(200,), allow_redirects=True, params=None):
    url = REST_URL + path
    r = SESSION.get(url, params=params, allow_redirects=allow_redirects, timeout=30)
    if r.status_code not in ok:
        raise RuntimeError(f"REST GET {url} -> {r.status_code}: {r.text[:200]}")
    return r


def _graphql(query: str, variables: dict):
    r = SESSION.post(
        GRAPHQL_URL, json={"query": query, "variables": variables}, timeout=30
    )
    if r.status_code != 200:
        raise RuntimeError(f"GraphQL {r.status_code}: {r.text[:200]}")
    payload = r.json()
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


# --------- Metrics collection ----------
GRAPHQL_REPO_QUERY = """
query RepoStats($owner:String!, $name:String!) {
  repository(owner:$owner, name:$name) {
    stargazerCount
    watchers { totalCount }              # subscribers_count
    forkCount
    issues(states: OPEN) { totalCount }  # open issues count
    releases { totalCount }
    pullRequests(states: [OPEN, MERGED, CLOSED]) { totalCount }
    defaultBranchRef {
      target {
        ... on Commit {
          history { totalCount }         # number of commits on default branch
        }
      }
    }
    issuesClosed: issues(states: CLOSED, first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { createdAt closedAt }
    }
  }
}
"""


def get_contributors_count(owner: str, repo: str) -> int:
    """
    Use REST: /repos/{owner}/{repo}/contributors?per_page=1&anon=1
    Count is the 'last' page number when per_page=1.
    """
    r = _rest_get(
        f"/repos/{owner}/{repo}/contributors",
        params={"per_page": 1, "anon": "1", "order": "desc"},
    )
    if "Link" not in r.headers:
        # Single (0 or 1) result
        data = r.json()
        return len(data)
    # Parse 'last' page from Link header
    link = r.headers["Link"]
    # e.g., <...&page=234>; rel="last"
    m = re.search(r'[?&]page=(\d+)>;\s*rel="last"', link)
    return int(m.group(1)) if m else 0


def get_network_count(owner: str, repo: str) -> t.Optional[int]:
    """
    REST repo object has 'network_count'.
    """
    r = _rest_get(f"/repos/{owner}/{repo}")
    data = r.json()
    return data.get("network_count")


def avg_days_to_close(issues_nodes: list[dict]) -> t.Optional[float]:
    """
    Average (closedAt - createdAt) in days for closed issues (last 100).
    """
    deltas = []
    for n in issues_nodes:
        created = n.get("createdAt")
        closed = n.get("closedAt")
        if not created or not closed:
            continue
        try:
            t0 = datetime.fromisoformat(created.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(closed.replace("Z", "+00:00"))
            dt = (t1 - t0).total_seconds() / 86400.0
            if dt >= 0:
                deltas.append(dt)
        except Exception:
            continue
    if not deltas:
        return None
    return sum(deltas) / len(deltas)


def collect_metrics(owner: str, repo: str) -> dict:
    """
    Mix GraphQL and REST to gather the requested metrics.
    """
    # GraphQL part
    data = _graphql(GRAPHQL_REPO_QUERY, {"owner": owner, "name": repo})
    repo_data = data.get("repository")
    if not repo_data:
        raise RuntimeError("Repository not found via GraphQL.")

    stargazers_count = repo_data.get("stargazerCount") or 0
    subscribers_count = (repo_data.get("watchers") or {}).get("totalCount") or 0
    forks_count = repo_data.get("forkCount") or 0
    open_issues_count = (repo_data.get("issues") or {}).get("totalCount") or 0
    releases_count = (repo_data.get("releases") or {}).get("totalCount") or 0
    pulls_count = (repo_data.get("pullRequests") or {}).get("totalCount") or 0
    commits_total = ((repo_data.get("defaultBranchRef") or {}).get("target") or {}).get(
        "history"
    )
    commits_count = (commits_total or {}).get("totalCount") or 0

    # watchers_count (REST field) historically equals stargazers_count in v3;
    watchers_count = stargazers_count

    # contributors (REST)
    try:
        contributors_count = get_contributors_count(owner, repo)
    except Exception:
        contributors_count = None

    # network_count (REST)
    try:
        network_count = get_network_count(owner, repo)
    except Exception:
        network_count = None

    # avg time to close (closed issues only; PRs are not included by GraphQL 'issues')
    issues_closed_nodes = (repo_data.get("issuesClosed") or {}).get("nodes") or []
    avg_close = avg_days_to_close(issues_closed_nodes)

    return {
        "repo.stargazers_count": stargazers_count,
        "repo.watchers_count": watchers_count,
        "repo.subscribers_count": subscribers_count,
        "repo.forks_count": forks_count,
        "repo.open_issues_count": open_issues_count,
        "repo.network_count": network_count,
        "num_contributors": contributors_count,
        "num_releases": releases_count,
        "num_commits": commits_count,
        "num_pulls": pulls_count,
        "avg_time_to_close_days": (
            round(avg_close, 3) if avg_close is not None else None
        ),
    }


# --------- Main pipeline ----------
def main():
    # read input CSV
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_fields = [
        "biotoolsID",
        "owner",
        "repo",
        "repo_url",
        "repo.stargazers_count",
        "repo.watchers_count",
        "repo.subscribers_count",
        "repo.forks_count",
        "repo.open_issues_count",
        "repo.network_count",
        "num_contributors",
        "num_releases",
        "num_commits",
        "num_pulls",
        "avg_time_to_close_days",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()

        for row in rows:
            biotools_id = (row.get("biotoolsID") or "").strip()
            urls = (row.get("github_urls") or "").split(";")
            url = next((u.strip() for u in urls if "github.com" in u.lower()), "")

            if not url:
                w.writerow({"biotoolsID": biotools_id})
                continue

            parsed = parse_owner_repo(url)
            if not parsed:
                w.writerow({"biotoolsID": biotools_id, "repo_url": url})
                continue

            owner, repo = parsed

            try:
                metrics = collect_metrics(owner, repo)
            except Exception as e:
                # follow repository moves/redirects via REST /repos to get canonical full_name if needed
                sys.stderr.write(f"[WARN] {owner}/{repo}: {e}\n")
                metrics = {
                    k: None
                    for k in out_fields
                    if k not in ("biotoolsID", "owner", "repo", "repo_url")
                }

            out = {
                "biotoolsID": biotools_id,
                "owner": owner,
                "repo": repo,
                "repo_url": url,
                **metrics,
            }
            w.writerow(out)
            # Be gentle on rate limits
            time.sleep(0.2)

    print(f"Wrote: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
