#!/usr/bin/env python3
"""Split ROS 2 launch output into stable, node-named log files.

The original stream is handled by ``tee`` in start.sh and remains available as
gazebo.log or navigation.log.  This helper only writes a second copy grouped by
the logger name embedded in standard ROS 2 output.
"""

import re
import sys
from pathlib import Path


LOG_LEVEL = re.compile(r"\[(?:DEBUG|INFO|WARN|ERROR|FATAL)\]")
BRACKET_VALUE = re.compile(r"\[([^\]]+)\]")
PROCESS = re.compile(r"^\[([^\]]+)\]")
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")


def log_name(line: str) -> str:
    """Return the ROS logger name, or the emitting process as a fallback."""
    clean = ANSI.sub("", line)
    level = LOG_LEVEL.search(clean)
    if level:
        values = BRACKET_VALUE.findall(clean[level.end():])
        if values:
            # Standard rclcpp output has [level] [timestamp] [node].  Launch
            # events often omit the timestamp and use [level] [node] instead.
            first = values[0]
            if re.fullmatch(r"\d+(?:\.\d+)?", first) and len(values) > 1:
                return values[1]
            return first
    match = PROCESS.search(clean)
    if match:
        # launch normally prefixes a process as e.g. ``gzserver-1``.
        return re.sub(r"-\d+$", "", match.group(1))
    return "launch"


def main() -> None:
    output_dir = Path(sys.argv[1])
    output_dir.mkdir(parents=True, exist_ok=True)

    for line in sys.stdin:
        name = SAFE_NAME.sub("_", log_name(line)).strip("._") or "launch"
        with (output_dir / f"{name}.log").open("a", encoding="utf-8") as log:
            log.write(line)


if __name__ == "__main__":
    main()
