from __future__ import annotations

import argparse

from . import core, selection
from .editorial import install_editorial_pipeline
from .graphiti import generate_graphiti_candidate

install_editorial_pipeline()


def normalize_legacy_candidate_metadata() -> int:
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
    generated: list[str] = []
    graphiti_path = generate_graphiti_candidate()
    if graphiti_path:
        generated.append(graphiti_path)
    public_path = selection.generate_public_candidate()
    generated.append(str(public_path))
    for path in generated:
        print(f"candidate_output={path}")
    return 0


def publish() -> int:
    path = selection.publish_best()
    if path is not None:
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
