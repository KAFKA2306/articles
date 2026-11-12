"""Daily read-only screening of published articles; URL reachability is not fact verification."""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .zenn_production import ROOT, collect_published_articles

JST = ZoneInfo("Asia/Tokyo")
URL = re.compile(r"https://[^\s<>)\]\"']+")
FENCE = re.compile(r"^\s*(\x60{3,}|~{3,})")
USER_AGENT = "KAFKA2306/articles portfolio-revalidation/1.0"


def source_urls(markdown: str) -> set[str]:
    """Extract cited HTTPS URLs from prose, excluding code examples."""
    urls: set[str] = set()
    fence_char = ""
    fence_size = 0
    in_comment = False
    for raw_line in markdown.splitlines():
        line = raw_line
        if in_comment:
            if "-->" in line:
                line = line.split("-->", 1)[1]
                in_comment = False
            else:
                continue
        if "<!--" in line:
            before, after = line.split("<!--", 1)
            if "-->" in after:
                line = before + after.split("-->", 1)[1]
            else:
                line = before
                in_comment = True
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if not fence_char:
                fence_char, fence_size = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                fence_char, fence_size = "", 0
            continue
        if fence_char:
            continue
        for match in URL.finditer(line):
            url = match.group().rstrip(".,;:!?}」】")
            parsed = urllib.parse.urlsplit(url)
            host = (parsed.hostname or "").lower()
            if not host or host in {"example.com", "localhost"} or host.endswith(".local"):
                continue
            if parsed.username or parsed.password:
                continue
            urls.add(url)
    return urls


def probe(url: str, timeout: float = 8.0) -> str:
    """Return REACHABLE, BROKEN or UNKNOWN; never equate reachability with truth."""
    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"}
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return "REACHABLE" if 200 <= response.status < 400 else "UNKNOWN"
    except urllib.error.HTTPError as exc:
        return "BROKEN" if exc.code in (404, 410) else "UNKNOWN"
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return "UNKNOWN"


def report(root: Path, *, now: datetime, workers: int = 8) -> tuple[str, bool]:
    articles, errors = collect_published_articles(root, now=now)
    by_article = {
        article.slug: source_urls(article.path.read_text(encoding="utf-8"))
        for article in articles
    }
    all_urls = sorted(set().union(*by_article.values())) if by_article else []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        states = dict(zip(all_urls, pool.map(probe, all_urls)))
    lines = [
        "## Daily published-article screening",
        "",
        f"Date (JST): {now.date().isoformat()}",
        f"Repository published:true articles: {len(articles)}",
        f"Unique cited HTTPS URLs probed: {len(all_urls)}",
        "",
        "Checks: front matter, publication date, cited URL reachability. "
        "Content claims and source currency remain UNVERIFIED until an "
        "evidence-based editorial review compares claims with current sources.",
        "",
        "| Article | Age (days) | Links reachable / broken / unknown | Action |",
        "| --- | ---: | --- | --- |",
    ]
    broken_any = False
    for article in articles:
        urls = by_article[article.slug]
        counts = {
            s: sum(states[url] == s for url in urls)
            for s in ("REACHABLE", "BROKEN", "UNKNOWN")
        }
        age = max(0, (now.date() - article.published_at.date()).days)
        broken = [url for url in sorted(urls) if states[url] == "BROKEN"]
        broken_any |= bool(broken)
        action = (
            "REVALIDATE sources"
            if broken
            else ("REVALIDATE volatile facts" if age >= 90 else "Review as needed")
        )
        lines.append(
            f"| {article.slug} | {age} | "
            f"{counts['REACHABLE']} / {counts['BROKEN']} / {counts['UNKNOWN']} | {action} |"
        )
        for url in broken:
            lines.append(f"- Broken cited URL in {article.slug}: {url}")
    if errors:
        lines.extend(["", "### Article metadata errors", *[f"- {error}" for error in errors]])
    if not articles:
        lines.append("\nNo published articles found. This is not a successful content review.")
    lines.append(
        "\nNo article contents or published states were modified; "
        "production catalog synchronization is monitored by the existing Zenn verification workflow."
    )
    return "\n".join(lines) + "\n", bool(errors or broken_any or not articles)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    summary, actionable = report(args.root, now=datetime.now(JST))
    sys.stdout.write(summary)
    if summary_path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary_path, "a", encoding="utf-8") as output:
            output.write(summary)
    return 1 if actionable else 0


if __name__ == "__main__":
    raise SystemExit(main())
