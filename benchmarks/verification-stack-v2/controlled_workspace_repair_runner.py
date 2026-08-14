from __future__ import annotations

import os
import shutil
from pathlib import Path

import controlled_workspace_runner as base


# v2.4 repair: the original runner copied the workspace while excluding
# node_modules, then invoked Nx/Turbo from PATH. Nx correctly refused to treat
# that copy as a locally installed workspace. Keep dependencies out of Git,
# but expose the exact pinned benchmark install through a local symlink after
# the clean baseline commit has been created.
def make_workspace(parent: Path, name: str) -> Path:
    dst = parent / name
    shutil.copytree(
        base.WORKSPACE,
        dst,
        ignore=shutil.ignore_patterns("node_modules", "dist", ".nx", ".turbo"),
    )
    base.git(dst, "init", "-q")
    base.git(dst, "config", "user.name", "verification-benchmark")
    base.git(dst, "config", "user.email", "benchmark@example.invalid")
    base.git(dst, "add", ".")
    base.git(dst, "commit", "-q", "-m", "baseline")

    modules = base.ROOT / "node_modules"
    if not modules.is_dir():
        raise RuntimeError("benchmark node_modules is unavailable")
    os.symlink(modules, dst / "node_modules", target_is_directory=True)
    return dst


base.make_workspace = make_workspace


if __name__ == "__main__":
    base.main()
