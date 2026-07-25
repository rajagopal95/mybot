#!/bin/bash

echo "Cleaning up previous ROS2/Gazebo processes..."

pkill -9 -f gzserver
pkill -9 -f gzclient
pkill -9 -f gazebo
pkill -9 -f rviz2
pkill -9 -f ros2
pkill -9 -f cartographer
pkill -9 -f slam_toolbox
pkill -9 -f rtabmap
pkill -9 -f teleop_twist_keyboard

sleep 2

source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash

BASE_LOG_DIR=~/mybot_ws/src/mybot/logs
mkdir -p "$BASE_LOG_DIR"

i=1
while [ -d "$BASE_LOG_DIR/log$i" ]; do
    i=$((i+1))
done
RUN_DIR="$BASE_LOG_DIR/log$i"
mkdir -p "$RUN_DIR"

echo "========================================="
echo "      MyBot Mapping Launcher"
echo "========================================="
echo
echo "Select mapping method:"
echo "1) SLAM Toolbox"
echo "2) Cartographer"
echo "3) RTAB-Map"
echo

read -p "Enter your choice [1-3]: " choice

echo "Starting Gazebo..."
ros2 launch mybot_gazebo gazebo.launch.py > "$RUN_DIR/gazebo.log" 2>&1 &
GAZEBO_PID=$!

sleep 10

case $choice in
    1)
        echo "Starting SLAM Toolbox..."
        ros2 launch mybot_slam slam.launch.py > "$RUN_DIR/slam.log" 2>&1 &
        ;;
    2)
        echo "Starting Cartographer..."
        ros2 launch mybot_slam cartographer.launch.py > "$RUN_DIR/cartographer.log" 2>&1 &
        ;;
    3)
        echo "Starting RTAB-Map..."
        ros2 launch mybot_slam rtabmap.launch.py > "$RUN_DIR/rtabmap.log" 2>&1 &
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

sleep 5

echo
echo "========================================="
echo "Mapping started successfully!"
echo "Gazebo PID: $GAZEBO_PID"
echo "Logs saved in: $RUN_DIR"
echo "========================================="

echo "Starting Teleop in a separate terminal..."

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
exec bash"
