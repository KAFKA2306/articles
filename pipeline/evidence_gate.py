from __future__ import annotations

import re
import csv
import io
import subprocess
from urllib.parse import unquote
from pathlib import Path
from .zenn_slug import validate_slug

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ("<!-- pipeline_meta:", "internal_lapras_rubric_proxy", "story_interest_proxy")
FILLER = ("具体的な入力、出力、テスト結果は未確認", "rows = fetch_rows()")


def check_article(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    prose = re.sub(r"(?ms)^(```|~~~).*?^\1\s*$", "", text)
    if any(marker in text for marker in FORBIDDEN):
        errors.append("contains retired pipeline scoring metadata")
    if any(marker in prose for marker in FILLER):
        errors.append("contains an explicit unverified placeholder")
    if not re.search(r"https://[^\s)\]>]+", prose):
        errors.append("requires at least one linked primary source or public evidence artifact")
    if not text.startswith("---\n"):
        return errors + ["missing YAML frontmatter"]
    end = text.find("\n---\n", 4)
    if end < 0:
        return errors + ["unterminated YAML frontmatter"]
    front = text[4:end]
    values = {}
    for key in ("title", "emoji", "type", "topics", "published"):
        match = re.search(rf"(?m)^{key}:\s*(.*?)\s*$", front)
        if not match or not match.group(1):
            errors.append(f"missing frontmatter {key}")
        else:
            values[key] = match.group(1)
    for key in ("title", "emoji"):
        if values.get(key, "").strip("'\"").strip() == "":
            errors.append(f"{key} must be a non-empty string")
    if values.get("type", "").strip("'\"") not in {"tech", "idea"}:
        errors.append("type must be tech or idea")
    if values.get("published", "") not in {"true", "false"}:
        errors.append("published must be boolean")
    topics = values.get("topics", "")
    if not (topics.startswith("[") and topics.endswith("]")):
        errors.append("topics must be a YAML list")
    else:
        try:
            parsed = next(csv.reader([topics[1:-1]], skipinitialspace=True))
            if not 1 <= len(parsed) <= 5 or any(not item.strip().strip("'\"") for item in parsed):
                errors.append("topics must contain 1..5 non-empty strings")
        except csv.Error:
            errors.append("topics list is malformed")
    for match in re.finditer(r"\]\(([^)]+)\)", text):
        target = match.group(1).split("#", 1)[0].split("?", 1)[0]
        if not target or re.match(r"(?:https?://|mailto:|//)", target) or target.startswith("#"):
            continue
        target = unquote(target)
        local = (path.parent / target).resolve()
        if not local.exists() and not (ROOT / target.lstrip("/")).exists():
            errors.append(f"broken local reference: {target}")
    return errors


def validate_published_paths(current: set[str], baseline: set[str]) -> list[str]:
    return [f"published article path removed or renamed: {path}" for path in sorted(baseline - current)]


def validate_unique_slugs(paths: list[Path]) -> list[str]:
    seen: dict[str, Path] = {}
    errors = []
    for path in paths:
        key = path.stem.casefold()
        if key in seen:
            errors.append(f"duplicate slug {path.stem!r}: {seen[key]} and {path}")
        else:
            seen[key] = path
    return errors


def main() -> int:
    failures = []
    paths = sorted((ROOT / "articles").glob("*.md"))
    failures.extend(validate_unique_slugs(paths))
    for path in paths:
        failures.extend(f"{path}: {error}" for error in validate_slug(path.stem))
        failures.extend(f"{path}: {error}" for error in check_article(path))
    try:
        baseline_ref = "origin/main"
        names = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", baseline_ref, "--", "articles"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.splitlines()
        baseline_published = set()
        for name in names:
            if not name.endswith(".md"):
                continue
            content = subprocess.run(
                ["git", "show", f"{baseline_ref}:{name}"], cwd=ROOT,
                capture_output=True, text=True, check=True,
            ).stdout
            if re.search(r"(?m)^published:\s*true\s*$", content):
                baseline_published.add(name)
        current = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "articles").glob("*.md")
            if re.search(r"(?m)^published:\s*true\s*$", path.read_text(encoding="utf-8"))
        }
        failures.extend(validate_published_paths(current, baseline_published))
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        failures.append(f"cannot verify published-path baseline: {exc}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"evidence_gate_articles={len(paths)} status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
