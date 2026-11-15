#!/usr/bin/env bash
set -eo pipefail

export DISPLAY="${DISPLAY:-:1}"

# shellcheck source=/dev/null
source /opt/ros/humble/setup.bash
if [[ -f "${HOME}/mybot_ws/install/setup.bash" ]]; then
  # shellcheck source=/dev/null
  source "${HOME}/mybot_ws/install/setup.bash"
fi

ros2 daemon stop >/dev/null 2>&1 || true
ros2 daemon start
