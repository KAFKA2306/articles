from __future__ import annotations

import controlled_source_runner as base


# v2.4 calibration is now implemented directly in controlled_source_runner.
# Keep this compatibility entry point because the controlled workflow calls it
# in audited-repair mode, but do not maintain a second command/scoring layer.
if __name__ == "__main__":
    base.main()
