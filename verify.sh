#!/usr/bin/env bash
# verify.sh - check that mybot_ws dependencies and workspace are ready.
# Usage: bash verify.sh
# Exit code: 0 if all required checks pass, 1 otherwise.

# Colours (disabled when not writing to a terminal)
if [ -t 1 ]; then
  GREEN=$'\033[0;32m'; RED=$'\033[0;31m'; YELLOW=$'\033[1;33m'; NC=$'\033[0m'
else
  GREEN=""; RED=""; YELLOW=""; NC=""
fi

FAILED=0
WARNED=0
MISSING_APT=()

ok()   { echo "  ${GREEN}[ OK ]${NC} $1"; }
fail() { echo "  ${RED}[FAIL]${NC} $1"; FAILED=$((FAILED + 1)); }
warn() { echo "  ${YELLOW}[WARN]${NC} $1"; WARNED=$((WARNED + 1)); }

# check_pkg <ros_package_name> <apt_package_name> [optional]
# Passes if the ROS package is found by the ament index, or the apt package is installed.
check_pkg() {
  local ros_pkg="$1" apt_pkg="$2" optional="$3"
  if ros2 pkg prefix "$ros_pkg" >/dev/null 2>&1 || dpkg -s "$apt_pkg" >/dev/null 2>&1; then
    ok "$ros_pkg"
  elif [ "$optional" = "optional" ]; then
    warn "$ros_pkg not found (needed for forklift)  ->  sudo apt install $apt_pkg"
    MISSING_APT+=("$apt_pkg")
  else
    fail "$ros_pkg not found  ->  sudo apt install $apt_pkg"
    MISSING_APT+=("$apt_pkg")
  fi
}

# check_ws_pkg <workspace_package_name>
check_ws_pkg() {
  if ros2 pkg prefix "$1" >/dev/null 2>&1; then
    ok "$1 ($(ros2 pkg prefix "$1"))"
  else
    fail "$1 not found  ->  build and source: colcon build --symlink-install && source install/setup.bash"
  fi
}

echo "===================================="
echo "        MYBOT_WS VERIFY"
echo "===================================="

# ---------------------------------------------------------------
echo ""
echo "--- 1) System ---"
if [ -r /etc/os-release ]; then
  . /etc/os-release
  if [ "$ID" = "ubuntu" ] && [ "$VERSION_ID" = "22.04" ]; then
    ok "Ubuntu $VERSION_ID"
  else
    warn "Ubuntu 22.04 expected, found: $PRETTY_NAME"
  fi
else
  warn "Cannot read /etc/os-release"
fi

# ---------------------------------------------------------------
echo ""
echo "--- 2) ROS 2 ---"
if command -v ros2 >/dev/null 2>&1; then
  ok "ros2 found"
  if [ "$ROS_DISTRO" = "humble" ]; then
    ok "ROS_DISTRO=humble"
  else
    fail "ROS_DISTRO is '${ROS_DISTRO:-unset}', expected 'humble'  ->  source /opt/ros/humble/setup.bash"
  fi
else
  fail "ros2 not found  ->  source /opt/ros/humble/setup.bash (or install ROS 2 Humble)"
  echo ""
  echo "ROS 2 is not available, so package checks cannot run. Fix the above and re-run."
  exit 1
fi

# ---------------------------------------------------------------
echo ""
echo "--- 3) Required packages (mapping + navigation) ---"
check_pkg slam_toolbox          ros-humble-slam-toolbox
check_pkg cartographer          ros-humble-cartographer
check_pkg cartographer_ros      ros-humble-cartographer-ros
check_pkg nav2_bringup          ros-humble-nav2-bringup
check_pkg nav2_amcl             ros-humble-navigation2
check_pkg robot_localization    ros-humble-robot-localization
check_pkg teleop_twist_keyboard ros-humble-teleop-twist-keyboard
check_pkg rviz2                 ros-humble-rviz2
check_pkg gazebo_ros            ros-humble-gazebo-ros-pkgs

echo ""
echo "--- 4) Gazebo ---"
if command -v gazebo >/dev/null 2>&1; then
  ok "gazebo ($(gazebo --version 2>/dev/null | head -n 1))"
else
  fail "gazebo not found  ->  sudo apt install ros-humble-gazebo-ros-pkgs"
fi

echo ""
echo "--- 5) Forklift packages ---"
check_pkg gazebo_ros2_control    ros-humble-gazebo-ros2-control   optional
check_pkg controller_manager     ros-humble-ros2-control          optional
check_pkg diff_drive_controller  ros-humble-ros2-controllers      optional
check_pkg joint_state_broadcaster ros-humble-ros2-controllers     optional
check_pkg xacro                  ros-humble-xacro                 optional
check_pkg laser_filters          ros-humble-laser-filters         optional

# ---------------------------------------------------------------
echo ""
echo "--- 6) Workspace ---"
check_ws_pkg mybot_description
check_ws_pkg mybot_gazebo
check_ws_pkg mybot_navigation
check_ws_pkg mybot_slam

# Scripts expected next to verify.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for f in mapping.sh start.sh kill.sh; do
  if [ -f "$SCRIPT_DIR/$f" ]; then
    ok "$f present"
  else
    warn "$f not found in $SCRIPT_DIR"
  fi
done

# ---------------------------------------------------------------
echo ""
echo "--- 7) Saved maps ---"
MAP_DIR=""
if ros2 pkg prefix mybot_slam >/dev/null 2>&1; then
  MAP_DIR="$(ros2 pkg prefix mybot_slam)/share/mybot_slam/maps"
fi
if [ -n "$MAP_DIR" ] && ls "$MAP_DIR"/*.yaml >/dev/null 2>&1; then
  ok "maps found: $(ls "$MAP_DIR"/*.yaml | xargs -n1 basename | tr '\n' ' ')"
else
  warn "no saved maps found (run mapping.sh and save_map.py before start.sh)"
fi

# ---------------------------------------------------------------
echo ""
echo "===================================="
if [ ${#MISSING_APT[@]} -gt 0 ]; then
  echo "Install missing packages with:"
  echo "  sudo apt install $(printf '%s\n' "${MISSING_APT[@]}" | sort -u | tr '\n' ' ')"
  echo ""
fi

if [ "$FAILED" -eq 0 ]; then
  echo "${GREEN}All required checks passed${NC} ($WARNED warning(s))."
  exit 0
else
  echo "${RED}$FAILED required check(s) failed${NC} ($WARNED warning(s))."
  exit 1
fi
