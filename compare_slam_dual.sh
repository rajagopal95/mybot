#!/bin/bash

echo "========================================================="
echo "   Starting Dual SLAM (SLAM Toolbox + Cartographer)      "
echo "        & Real-time Comparison Suite for MyBot          "
echo "========================================================="

echo "Cleaning up previous ROS2/Gazebo processes..."
pkill -9 -f gzserver
pkill -9 -f gzclient
pkill -9 -f gazebo
pkill -9 -f rviz2
pkill -9 -f ros2
pkill -9 -f cartographer
pkill -9 -f slam_toolbox
pkill -9 -f compare_slam

sleep 2

source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash

echo "[1/4] Starting Gazebo simulation..."
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash
ros2 launch mybot_gazebo gazebo.launch.py
exec bash"

sleep 10

echo "[2/4] Starting Dual SLAM (SLAM Toolbox + Cartographer)..."
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash
ros2 launch mybot_slam dual_slam.launch.py
exec bash"

sleep 4

echo "[3/4] Starting Teleop Keyboard Controller..."
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
exec bash"

sleep 2

echo "[4/4] Launching Real-Time SLAM Comparison GUI Monitor..."
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash
ros2 run mybot_slam compare_slam.py
exec bash"

echo "========================================================="
echo " Dual SLAM Comparison suite started successfully!"
echo " Drive the robot in teleop terminal to map environment."
echo " Real-time graphs and metrics are updating in Python GUI."
echo "========================================================="
