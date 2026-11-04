#!/bin/bash
# Usage: ./start.sh [mybot|forklift] [map_name_or_path]
# Examples:
#   ./start.sh                       (interactive menu)
#   ./start.sh forklift              (default map)
#   ./start.sh forklift warehouse    (maps/warehouse.yaml)
#   ./start.sh mybot /tmp/test.yaml  (full path)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Adjust to wherever your maps live
MAP_DIR=~/mybot_ws/src/mybot/mybot_slam/maps

usage() {
    echo "Usage: $0 [mybot|forklift] [map_name_or_path]"
    echo
    echo "Available maps in $MAP_DIR:"
    ls "$MAP_DIR"/*.yaml 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/\.yaml$/  /' | sed 's/^/  - /'
}

# ---------- 1. Parse robot ----------
case "${1:-}" in
    mybot|1) ROBOT=mybot ;;
    forklift|fork|2) ROBOT=forklift ;;
    "")
        echo "Select robot:"
        echo "1) Mybot"
        echo "2) Forklift"
        echo
        read -p "Enter your choice [1-2]: " robot_choice
        case $robot_choice in
            1) ROBOT=mybot ;;
            2) ROBOT=forklift ;;
            *) echo "Invalid choice!"; exit 1 ;;
        esac
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Unknown robot: $1"
        usage
        exit 1
        ;;
esac

# ---------- 2. Parse map (validated BEFORE killing anything) ----------
MAP_ARG="${2:-}"

# In interactive mode (no args at all), offer a map choice
if [ -z "${1:-}" ] && [ -z "$MAP_ARG" ]; then
    echo
    echo "Available maps:"
    ls "$MAP_DIR"/*.yaml 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/\.yaml$//' | sed 's/^/  - /'
    echo
    read -p "Map name (Enter for default): " MAP_ARG
fi

NAV_ARGS=""
MAP_FILE=""
if [ -n "$MAP_ARG" ]; then
    if [ -f "$MAP_ARG" ]; then
        MAP_FILE="$(realpath "$MAP_ARG")"            # full/relative path given
    else
        MAP_FILE="$MAP_DIR/${MAP_ARG%.yaml}.yaml"    # name given
    fi

    if [ ! -f "$MAP_FILE" ]; then
        echo "Map not found: $MAP_FILE"
        echo
        usage
        exit 1
    fi
    NAV_ARGS="map:=$MAP_FILE"
fi

# ---------- 3. Cleanup ----------
echo "Cleaning up previous ROS2/Gazebo processes..."

# Same cleanup list as mapping.sh.
"$SCRIPT_DIR/kill.sh"

sleep 2

source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash

# ---------- 4. Pick Gazebo launch ----------
if [ "$ROBOT" = "forklift" ]; then
    GAZEBO_LAUNCH="ros2 launch mybot_gazebo fork_gazebo.launch.py"
else
    GAZEBO_LAUNCH="ros2 launch mybot_gazebo gazebo.launch.py"
fi

# ---------- 5. Log directory ----------
BASE_LOG_DIR=~/mybot_ws/src/mybot/logs
mkdir -p "$BASE_LOG_DIR"

i=1
while [ -d "$BASE_LOG_DIR/log$i" ]; do
    i=$((i+1))
done
RUN_DIR="$BASE_LOG_DIR/log$i"
mkdir -p "$RUN_DIR"

# Keep the existing combined launcher logs below, and also give ROS 2 a
# run-specific log directory.  This preserves one file per node (including
# Gazebo plugins, Nav2 servers, RViz, and controllers) instead of mixing every
# node's diagnostics only into gazebo.log or navigation.log.
ROS_RUN_LOG_DIR="$RUN_DIR/ros"
mkdir -p "$ROS_RUN_LOG_DIR"
GAZEBO_NODE_LOG_DIR="$RUN_DIR/gazebo"
NAVIGATION_NODE_LOG_DIR="$RUN_DIR/navigation"
mkdir -p "$GAZEBO_NODE_LOG_DIR" "$NAVIGATION_NODE_LOG_DIR"

# ---------- 6. Launch ----------
echo "Starting Gazebo ($ROBOT)..."
ROS_LOG_DIR="$ROS_RUN_LOG_DIR" $GAZEBO_LAUNCH \
    > >(tee "$RUN_DIR/gazebo.log" | python3 "$SCRIPT_DIR/split_node_logs.py" "$GAZEBO_NODE_LOG_DIR") \
    2>&1 &
GAZEBO_PID=$!

sleep 10

echo "Starting Navigation..."
ROS_LOG_DIR="$ROS_RUN_LOG_DIR" ros2 launch mybot_navigation navigation.launch.py $NAV_ARGS \
    > >(tee "$RUN_DIR/navigation.log" | python3 "$SCRIPT_DIR/split_node_logs.py" "$NAVIGATION_NODE_LOG_DIR") \
    2>&1 &
NAV_PID=$!

echo
echo "========================================="
echo "System Started Successfully ($ROBOT)"
echo "========================================="
echo "Map             : ${MAP_FILE:-default (from launch file)}"
echo "Gazebo PID      : $GAZEBO_PID"
echo "Navigation PID  : $NAV_PID"
echo "Logs saved in   : $RUN_DIR"
echo "Node logs       : $ROS_RUN_LOG_DIR"
echo "Gazebo nodes    : $GAZEBO_NODE_LOG_DIR"
echo "Nav2 nodes      : $NAVIGATION_NODE_LOG_DIR"
echo "========================================="
