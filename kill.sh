#!/bin/bash

echo "========================================="
echo "      MyBot Cleanup Utility"
echo "========================================="

echo "[1/6] Stopping ROS 2 launch processes..."
pkill -9 -f "ros2 launch"
pkill -9 -f "ros2 run"

echo "[2/6] Stopping Gazebo..."
pkill -9 -f gzserver
pkill -9 -f gzclient
pkill -9 -f gazebo
pkill -9 -f spawn_entity

echo "[3/6] Stopping RViz..."
pkill -9 -f rviz2

echo "[4/6] Stopping Navigation and SLAM..."
pkill -9 -f nav2
pkill -9 -f amcl
pkill -9 -f map_server
pkill -9 -f planner_server
pkill -9 -f controller_server
pkill -9 -f smoother_server
pkill -9 -f behavior_server
pkill -9 -f bt_navigator
pkill -9 -f waypoint_follower
pkill -9 -f velocity_smoother
pkill -9 -f lifecycle_manager

pkill -9 -f slam_toolbox
pkill -9 -f cartographer
pkill -9 -f cartographer_node
pkill -9 -f cartographer_occupancy_grid_node

echo "[4b/6] Stopping laser scan filter..."
pkill -9 -f scan_to_scan_filter_chain
pkill -9 -f scan_filter_node

echo "[5/6] Stopping robot nodes..."
pkill -9 -f robot_state_publisher
pkill -9 -f joint_state_publisher
pkill -9 -f joint_state_broadcaster
pkill -9 -f controller_manager
pkill -9 -f diff_drive_controller
pkill -9 -f teleop_twist_keyboard
pkill -9 -f robot_localization
pkill -9 -f ekf_node
pkill -9 -f twist_mux
pkill -9 -f static_transform_publisher

echo "[6/6] Resetting ROS 2 daemon..."
ros2 daemon stop >/dev/null 2>&1
sleep 2
ros2 daemon start >/dev/null 2>&1

sleep 2

echo
echo "Checking for remaining Gazebo processes..."

if pgrep -x gzserver >/dev/null || pgrep -x gzclient >/dev/null; then
    echo "Warning: Some Gazebo processes are still running."
    ps -ef | grep gz | grep -v grep
else
    echo "Gazebo completely stopped."
fi

echo
echo "Cleanup complete."
echo "You can safely run start.sh or mapping.sh now."
