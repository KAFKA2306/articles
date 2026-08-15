from __future__ import annotations

import argparse
import html
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
JST = ZoneInfo("Asia/Tokyo")
DEFAULT_USERNAME = "kafka2306"
USER_AGENT = "KAFKA2306/articles zenn-production-verifier/2.0"


@dataclass(frozen=True)
class Article:
    path: Path
    slug: str
    title: str
    published_at: datetime

    def url(self, username: str) -> str:
        return f"https://zenn.dev/{username}/articles/{self.slug}"


@dataclass(frozen=True)
class Verification:
    article: Article
    ok: bool
    detail: str


def _normalize(value: str) -> str:
    value = html.unescape(value)
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", value).strip()


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing front matter")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("unterminated front matter")
    result: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = _unquote(value)
    return result


def _parse_published_at(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip())
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=JST)
    return parsed.astimezone(JST)


def collect_published_articles(
    root: Path = ROOT,
    *,
    now: datetime | None = None,
) -> tuple[list[Article], list[str]]:
    now = (now or datetime.now(JST)).astimezone(JST)
    articles: list[Article] = []
    errors: list[str] = []
    for path in sorted((root / "articles").glob("*.md")):
        try:
            front = parse_front_matter(path)
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        if front.get("published", "").strip().lower() != "true":
            continue
        title = front.get("title", "").strip()
        published_at_raw = front.get("published_at", "").strip()
        if not title:
            errors.append(f"{path.name}: published:true requires title")
            continue
        if not published_at_raw:
            errors.append(f"{path.name}: published:true requires published_at")
            continue
        try:
            published_at = _parse_published_at(published_at_raw)
        except ValueError:
            errors.append(
                f"{path.name}: invalid published_at {published_at_raw!r}; "
                "use YYYY-MM-DD or YYYY-MM-DD HH:MM"
            )
            continue
        if published_at > now:
            errors.append(
                f"{path.name}: invariant violation: published:true is future-dated "
                f"({published_at.isoformat()}); keep it published:false until release"
            )
            continue
        articles.append(Article(path, path.stem, title, published_at))
    return articles, errors


def fetch_public_catalog(
    username: str, *, timeout_seconds: float = 20.0
) -> dict[str, str]:
    """Return {article_slug: title} from Zenn's documented public user RSS feed."""
    url = f"https://zenn.dev/{username}/feed?all=1"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        status = getattr(response, "status", None) or response.getcode()
        if status != 200:
            raise RuntimeError(f"public RSS returned HTTP {status}")
        payload = response.read(5_000_000)

    root = ET.fromstring(payload)
    catalog: dict[str, str] = {}
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        parsed = urllib.parse.urlparse(link)
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.netloc != "zenn.dev" or len(parts) != 3:
            continue
        if parts[0] != username or parts[1] != "articles":
            continue
        catalog[parts[2]] = title
    return catalog


def compare_catalog(
    articles: list[Article], catalog: dict[str, str]
) -> list[Verification]:
    results: list[Verification] = []
    for article in articles:
        observed = catalog.get(article.slug)
        if observed is None:
            results.append(Verification(article, False, "missing from Zenn public RSS"))
            continue
        if _normalize(observed) != _normalize(article.title):
            results.append(
                Verification(
                    article,
                    False,
                    f"title mismatch: expected={article.title!r} observed={observed!r}",
                )
            )
            continue
        results.append(
            Verification(article, True, "public RSS entry + canonical slug + title match")
        )
    return results


def verify_until_settled(
    articles: list[Article],
    *,
    username: str,
    wait_seconds: int,
    interval_seconds: int,
) -> tuple[list[Verification], str | None]:
    deadline = time.monotonic() + max(wait_seconds, 0)
    latest: list[Verification] = []
    latest_error: str | None = None
    while True:
        try:
            catalog = fetch_public_catalog(username)
            latest = compare_catalog(articles, catalog)
            latest_error = None
        except (urllib.error.URLError, TimeoutError, ET.ParseError, RuntimeError) as exc:
            latest = []
            latest_error = f"catalog fetch failed: {exc}"
        if latest_error is None and all(result.ok for result in latest):
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(max(interval_seconds, 1))
    return latest, latest_error


def _render_summary(
    articles: list[Article],
    errors: list[str],
    results: list[Verification],
    username: str,
    catalog_error: str | None,
) -> str:
    lines = [
        "## Zenn production verification",
        "",
        f"Authority: Zenn documented public user RSS `https://zenn.dev/{username}/feed?all=1`.",
        "Invariant: every `published: true` article must be present there with the canonical slug and matching title.",
        "",
        "| slug | result | detail |",
        "| --- | --- | --- |",
    ]
    by_slug = {result.article.slug: result for result in results}
    for article in articles:
        result = by_slug.get(article.slug)
        if result is None:
            mark, detail = "FAIL", catalog_error or "verification unavailable"
        else:
            mark = "PASS" if result.ok else "FAIL"
            detail = result.detail
        lines.append(
            f"| `{article.slug}` | **{mark}** | {detail.replace('|', '\\|')} |"
        )
    if errors:
        lines.extend(["", "### Contract errors", ""])
        lines.extend(f"- {error}" for error in errors)
    if catalog_error:
        lines.extend(["", "### Catalog error", "", f"- {catalog_error}"])
    verified = sum(result.ok for result in results)
    lines.extend(["", f"Verified: {verified}/{len(articles)} published:true articles"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed unless every published:true article is public on Zenn."
    )
    parser.add_argument(
        "--username", default=os.environ.get("ZENN_USERNAME", DEFAULT_USERNAME)
    )
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--interval-seconds", type=int, default=15)
    args = parser.parse_args(argv)

    articles, errors = collect_published_articles()
    results, catalog_error = verify_until_settled(
        articles,
        username=args.username,
        wait_seconds=args.wait_seconds,
        interval_seconds=args.interval_seconds,
    )
    summary = _render_summary(
        articles, errors, results, args.username, catalog_error
    )
    sys.stdout.write(summary)
    github_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_summary:
        with open(github_summary, "a", encoding="utf-8") as handle:
            handle.write(summary)
    failures = [result for result in results if not result.ok]
    return 1 if errors or catalog_error or failures or len(results) != len(articles) else 0


if __name__ == "__main__":
    raise SystemExit(main())
