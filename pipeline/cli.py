from __future__ import annotations

import argparse

from . import core
from .graphiti import generate_graphiti_candidate


def normalize_legacy_candidate_metadata() -> int:
    """Migrate one-off bootstrap metadata before any pipeline action.

    The bootstrap candidate used ``factory_meta`` before ``pipeline_meta`` became
    canonical. Normalize it in-place so monthly evaluation and publication use
    the same metadata-stripping contract and never publish the internal comment.
    """
    normalized = 0
    for path in core.candidate_files_this_month():
        text = path.read_text(encoding="utf-8")
        if not text.startswith("<!-- factory_meta: "):
            continue
        path.write_text(
            text.replace("<!-- factory_meta: ", "<!-- pipeline_meta: ", 1),
            encoding="utf-8",
        )
        normalized += 1
    if normalized:
        print(f"legacy_candidate_metadata_normalized={normalized}")
    return normalized


def candidate() -> int:
    generated = []
    graphiti_path = generate_graphiti_candidate()
    if graphiti_path:
        generated.append(graphiti_path)
    public_path = core.generate_public_candidate()
    generated.append(str(public_path))
    for path in generated:
        print(f"candidate_output={path}")
    return 0


def publish() -> int:
    path = core.publish_best()
    if path is None:
        print("publish=no-op")
        return 0
    print(f"published={path.relative_to(core.ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canonical autonomous article pipeline"
    )
    parser.add_argument("mode", choices=("candidate", "publish"))
    args = parser.parse_args()
    normalize_legacy_candidate_metadata()
    return candidate() if args.mode == "candidate" else publish()


if __name__ == "__main__":
    raise SystemExit(main())
