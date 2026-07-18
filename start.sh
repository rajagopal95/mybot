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

source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash

gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash; source ~/mybot_ws/install/setup.bash; ros2 launch mybot_gazebo gazebo.launch.py; exec bash"

sleep 10

gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash; source ~/mybot_ws/install/setup.bash; ros2 launch mybot_navigation navigation.launch.py; exec bash"

#ros2 topic pub /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25,0,0,0,0,0, 0,0.25,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.06853891945200942]}}" --rate 2
