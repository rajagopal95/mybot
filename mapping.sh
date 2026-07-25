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
pkill -9 -f compare_slam
pkill -9 -f teleop_twist_keyboard

sleep 2

source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash

echo "========================================="
echo "      MyBot Mapping Launcher"
echo "========================================="
echo
echo "Select mapping method:"
echo "1) SLAM Toolbox (Single)"
echo "2) Cartographer (Single)"
echo "3) Multi-SLAM Comparison (SLAM Toolbox + Cartographer + RTAB-Map)"
echo "4) Multi-SLAM Comparison (SLAM Toolbox + Cartographer + RTAB-Map)"
echo

read -p "Enter your choice [1-4]: " choice

echo "Starting Gazebo simulation..."
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash
ros2 launch mybot_gazebo gazebo.launch.py
exec bash"

sleep 10

case $choice in
    1)
        echo "Starting SLAM Toolbox..."
        gnome-terminal -- bash -c "
        source /opt/ros/humble/setup.bash
        source ~/mybot_ws/install/setup.bash
        ros2 launch mybot_slam slam.launch.py
        exec bash"
        ;;
    2)
        echo "Starting Cartographer..."
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
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

sleep 4

echo "Starting Teleop..."
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/mybot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
exec bash"

echo
echo "========================================="
echo "Mapping started successfully!"
echo "Drive the robot using the keyboard."
echo "========================================="
