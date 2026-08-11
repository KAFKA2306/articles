from __future__ import annotations

import argparse

from . import core
from .graphiti import generate_graphiti_candidate


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
        print("publish=no-op reason=already_published_this_month")
        return 0
    print(f"published={path.relative_to(core.ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canonical autonomous article pipeline"
    )
    parser.add_argument("mode", choices=("candidate", "publish"))
    args = parser.parse_args()
    return candidate() if args.mode == "candidate" else publish()


if __name__ == "__main__":
    raise SystemExit(main())
