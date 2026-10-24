#!/bin/bash

echo "Cleaning up previous ROS2/Gazebo processes..."

<<<<<<< HEAD
pkill -9 -f gzserver
pkill -9 -f gzclient
pkill -9 -f gazebo
pkill -9 -f rviz2
pkill -9 -f ros2
pkill -9 -f cartographer
pkill -9 -f slam_toolbox
pkill -9 -f rtabmap
pkill -9 -f compare_slam
pkill -9 -f teleop_twist_keyboard
=======
# Single source of truth for cleanup — see kill.sh. Keeping only one list
# avoids this script and kill.sh drifting out of sync (which is how
# robot_state_publisher/scan_filter_node ended up missing from here before).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/kill.sh"
>>>>>>> origin/Raja

sleep 2

source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash

# ./mapping.sh [mybot|forklift]
# No argument opens the same numbered menu as the SLAM choice below.
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
    # Frames, robot model, /scan and /map. The SLAM launches skip their own RViz.
    RVIZ_ARG="use_rviz:=false"
    RVIZ_CONFIG="$(ros2 pkg prefix mybot_slam)/share/mybot_slam/rviz/fork_mapping.rviz"
else
    GAZEBO_LAUNCH="ros2 launch mybot_gazebo gazebo.launch.py"
    RVIZ_ARG="use_rviz:=true"
    RVIZ_CONFIG=""
fi

BASE_LOG_DIR=~/mybot_ws/src/mybot/logs
mkdir -p "$BASE_LOG_DIR"

i=1
while [ -d "$BASE_LOG_DIR/log$i" ]; do
    i=$((i+1))
done
RUN_DIR="$BASE_LOG_DIR/log$i"
mkdir -p "$RUN_DIR"

echo "========================================="
echo "      Mapping Launcher ($ROBOT)"
echo "========================================="
echo
echo "Select mapping method:"
<<<<<<< HEAD
echo "1) SLAM Toolbox (Single)"
echo "2) Cartographer (Single)"
echo "3) Multi-SLAM Comparison (SLAM Toolbox + Cartographer + RTAB-Map)"
echo "4) Multi-SLAM Comparison (SLAM Toolbox + Cartographer + RTAB-Map)"
echo

read -p "Enter your choice [1-4]: " choice
=======
echo "1) SLAM Toolbox"
echo "2) Cartographer"
echo

read -p "Enter your choice [1-2]: " choice
>>>>>>> origin/Raja

echo "Starting Gazebo ($ROBOT)..."

$GAZEBO_LAUNCH > "$RUN_DIR/gazebo.log" 2>&1 &
GAZEBO_PID=$!

sleep 10

case $choice in
    1)
        echo "Starting SLAM Toolbox..."
        ros2 launch mybot_slam slam.launch.py $RVIZ_ARG > "$RUN_DIR/slam.log" 2>&1 &
        ;;
    2)
        echo "Starting Cartographer..."
<<<<<<< HEAD
        gnome-terminal -- bash -c "
        source /opt/ros/humble/setup.bash
        source ~/mybot_ws/install/setup.bash
        ros2 launch mybot_slam cartographer.launch.py
        exec bash"
        ;;
    3|4)
        echo "Starting Multi-SLAM (SLAM Toolbox + Cartographer + RTAB-Map)..."
        gnome-terminal -- bash -c "
        source /opt/ros/humble/setup.bash
        source ~/mybot_ws/install/setup.bash
        ros2 launch mybot_slam dual_slam.launch.py
        exec bash"

        sleep 4
        echo "Starting Real-Time Multi-SLAM Comparison Monitor..."
        gnome-terminal -- bash -c "
        source /opt/ros/humble/setup.bash
        source ~/mybot_ws/install/setup.bash
        ros2 run mybot_slam compare_slam.py
        exec bash"
=======
        ros2 launch mybot_slam cartographer.launch.py $RVIZ_ARG > "$RUN_DIR/cartographer.log" 2>&1 &
>>>>>>> origin/Raja
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

sleep 4

echo
echo "========================================="
echo "Mapping started successfully!"
echo "Gazebo PID: $GAZEBO_PID"
echo "Logs saved in: $RUN_DIR"
echo "========================================="

if [ -n "$RVIZ_CONFIG" ]; then
    echo "Starting RViz (frames + map)..."
    ros2 run rviz2 rviz2 -d "$RVIZ_CONFIG" --ros-args -p use_sim_time:=true > "$RUN_DIR/rviz.log" 2>&1 &
fi

echo "Starting Teleop in a separate terminal..."

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
exec bash"