from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "mutants.json").read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    checked = 0
    for mutant in MANIFEST["mutants"]:
        target = mutant.get("target")
        if not target:
            continue
        path = ROOT / target
        if not path.exists():
            failures.append(f"{mutant['id']}: missing target {target}")
            continue
        operation = mutant["operation"]
        if operation == "replace_once":
            text = path.read_text(encoding="utf-8")
            count = text.count(mutant["old"])
            checked += 1
            if count != 1:
                failures.append(f"{mutant['id']}: replace anchor count={count}, expected=1")
        elif operation == "insert_before":
            lines = path.read_text(encoding="utf-8").splitlines()
            count = sum(1 for line in lines if mutant["anchor"] in line)
            checked += 1
            if count != 1:
                failures.append(f"{mutant['id']}: insert anchor count={count}, expected=1")
        elif operation in {
            "touch_input",
            "change_dependency_input",
            "run_hook_runners",
        }:
            checked += 1
        elif operation in {
            "repeat_without_change",
            "introduce_forbidden_dependency",
        }:
            checked += 1
        else:
            failures.append(f"{mutant['id']}: unknown operation {operation}")

    if failures:
        raise SystemExit("mutant integrity failed:\n" + "\n".join(failures))
    print(f"mutant integrity: valid ({checked} scenarios checked)")


if __name__ == "__main__":
    main()
