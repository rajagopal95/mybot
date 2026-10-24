#!/usr/bin/env bash
set -eo pipefail

# shellcheck source=/dev/null
source /opt/ros/humble/setup.bash

WS="${HOME}/mybot_ws"
mkdir -p "${WS}/src/mybot"

link_pkg() {
  local name="$1"
  local target="${WS}/src/mybot/${name}"
  if [[ -e "${target}" && ! -L "${target}" ]]; then
    rm -rf "${target}"
  fi
  ln -sfn "/workspace/${name}" "${target}"
}

for pkg in mybot_description mybot_gazebo mybot_navigation mybot_slam; do
  link_pkg "${pkg}"
done

mkdir -p "${WS}/src/mybot/logs"
for script in start.sh mapping.sh kill.sh verify.sh; do
  if [[ -f "/workspace/${script}" ]]; then
    ln -sfn "/workspace/${script}" "${WS}/src/mybot/${script}"
  fi
done

cd "${WS}"
colcon build --symlink-install
