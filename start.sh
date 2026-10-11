#!/bin/bash

echo "Cleaning up previous ROS2/Gazebo processes..."

# Same cleanup list as mapping.sh.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/kill.sh"

sleep 2

source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash

# ./start.sh [mybot|forklift]
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
        echo "Usage: $0 [mybot|forklift]"
        exit 0
        ;;
    *)
        echo "Unknown robot: $1"
        echo "Usage: $0 [mybot|forklift]"
        exit 1
        ;;
esac

if [ "$ROBOT" = "forklift" ]; then
    GAZEBO_LAUNCH="ros2 launch mybot_gazebo fork_gazebo.launch.py"
else
    GAZEBO_LAUNCH="ros2 launch mybot_gazebo gazebo.launch.py"
fi

BASE_LOG_DIR=~/mybot_ws/src/mybot/logs
mkdir -p "$BASE_LOG_DIR"

i=1
while [ -d "$BASE_LOG_DIR/log$i" ]; do
    i=$((i+1))
done
RUN_DIR="$BASE_LOG_DIR/log$i"
mkdir -p "$RUN_DIR"

echo "Starting Gazebo ($ROBOT)..."
$GAZEBO_LAUNCH > "$RUN_DIR/gazebo.log" 2>&1 &
GAZEBO_PID=$!

sleep 10

echo "Starting Navigation..."
ros2 launch mybot_navigation navigation.launch.py > "$RUN_DIR/navigation.log" 2>&1 &
NAV_PID=$!

echo
echo "========================================="
echo "System Started Successfully ($ROBOT)"
echo "========================================="
echo "Gazebo PID     : $GAZEBO_PID"
echo "Navigation PID  : $NAV_PID"
echo "Logs saved in   : $RUN_DIR"
echo "========================================="
