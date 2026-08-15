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
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
JST = ZoneInfo("Asia/Tokyo")
DEFAULT_USERNAME = "kafka2306"
USER_AGENT = "KAFKA2306/articles zenn-production-verifier/1.0"


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


class _PageMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.og_title: str | None = None
        self._in_title = False
        self._title_parts: list[str] = []

    @property
    def html_title(self) -> str:
        return "".join(self._title_parts).strip()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
            return
        if tag.lower() != "meta":
            return
        values = {key.lower(): value for key, value in attrs if value is not None}
        if values.get("property", "").lower() == "og:title":
            self.og_title = values.get("content")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)


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
    try:
        raw = text.split("---\n", 2)[1]
    except IndexError as exc:
        raise ValueError("unterminated front matter") from exc

    result: dict[str, str] = {}
    for line in raw.splitlines():
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
        articles.append(
            Article(
                path=path,
                slug=path.stem,
                title=title,
                published_at=published_at,
            )
        )
    return articles, errors


def _title_matches(page_html: str, expected: str) -> tuple[bool, str]:
    parser = _PageMetadata()
    parser.feed(page_html)
    expected_norm = _normalize(expected)
    candidates = [value for value in (parser.og_title, parser.html_title) if value]
    for candidate in candidates:
        normalized = _normalize(candidate)
        if normalized == expected_norm or normalized.startswith(expected_norm + " |"):
            return True, candidate
    return False, " / ".join(candidates) if candidates else "no og:title or <title>"


def verify_article(
    article: Article,
    *,
    username: str,
    timeout_seconds: float = 20.0,
) -> Verification:
    url = article.url(username)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status = getattr(response, "status", None) or response.getcode()
            final_url = response.geturl()
            body = response.read(2_000_000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return Verification(article, False, f"HTTP {exc.code}")
    except urllib.error.URLError as exc:
        return Verification(article, False, f"network error: {exc.reason}")
    except TimeoutError:
        return Verification(article, False, "network timeout")

    if status != 200:
        return Verification(article, False, f"HTTP {status}")

    expected_path = urllib.parse.urlparse(url).path.rstrip("/")
    parsed_final = urllib.parse.urlparse(final_url)
    if parsed_final.netloc != "zenn.dev" or parsed_final.path.rstrip("/") != expected_path:
        return Verification(article, False, f"unexpected redirect: {final_url}")

    title_ok, observed_title = _title_matches(body, article.title)
    if not title_ok:
        return Verification(
            article,
            False,
            f"title mismatch: expected={article.title!r} observed={observed_title!r}",
        )
    return Verification(article, True, "HTTP 200 + canonical URL + title match")


def verify_until_settled(
    articles: list[Article],
    *,
    username: str,
    wait_seconds: int,
    interval_seconds: int,
) -> list[Verification]:
    deadline = time.monotonic() + max(wait_seconds, 0)
    pending = {article.slug: article for article in articles}
    latest: dict[str, Verification] = {}

    while pending:
        for slug, article in list(pending.items()):
            result = verify_article(article, username=username)
            latest[slug] = result
            if result.ok:
                del pending[slug]
        if not pending or time.monotonic() >= deadline:
            break
        time.sleep(max(interval_seconds, 1))

    return [latest[article.slug] for article in articles]


def _render_summary(
    articles: list[Article], errors: list[str], results: list[Verification], username: str
) -> str:
    lines = [
        "## Zenn production verification",
        "",
        f"Invariant: every `published: true` article must already be public under `zenn.dev/{username}/articles/<slug>`.",
        "",
        "| slug | result | detail |",
        "| --- | --- | --- |",
    ]
    by_slug = {result.article.slug: result for result in results}
    for article in articles:
        result = by_slug[article.slug]
        mark = "PASS" if result.ok else "FAIL"
        detail = result.detail.replace("|", "\\|")
        lines.append(f"| `{article.slug}` | **{mark}** | {detail} |")
    if errors:
        lines.extend(["", "### Contract errors", ""])
        lines.extend(f"- {error}" for error in errors)
    lines.extend(
        [
            "",
            f"Verified: {sum(result.ok for result in results)}/{len(articles)} production URLs",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed unless every published:true article is live on Zenn."
    )
    parser.add_argument(
        "--username", default=os.environ.get("ZENN_USERNAME", DEFAULT_USERNAME)
    )
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--interval-seconds", type=int, default=15)
    args = parser.parse_args(argv)

    articles, errors = collect_published_articles()
    results = verify_until_settled(
        articles,
        username=args.username,
        wait_seconds=args.wait_seconds,
        interval_seconds=args.interval_seconds,
    )
    summary = _render_summary(articles, errors, results, args.username)
    sys.stdout.write(summary)

    github_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_summary:
        with open(github_summary, "a", encoding="utf-8") as handle:
            handle.write(summary)

    failures = [result for result in results if not result.ok]
    return 1 if errors or failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
