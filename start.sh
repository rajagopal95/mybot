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

echo "Starting Gazebo..."
ros2 launch mybot_gazebo gazebo.launch.py > "$RUN_DIR/gazebo.log" 2>&1 &
GAZEBO_PID=$!

sleep 10

echo "Starting Navigation..."
ros2 launch mybot_navigation navigation.launch.py > "$RUN_DIR/navigation.log" 2>&1 &
NAV_PID=$!

echo
echo "========================================="
echo "System Started Successfully"
echo "========================================="
echo "Gazebo PID     : $GAZEBO_PID"
echo "Navigation PID  : $NAV_PID"
echo "Logs saved in   : $RUN_DIR"
echo "========================================="
