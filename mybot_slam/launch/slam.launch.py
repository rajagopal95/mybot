#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_slam_share = FindPackageShare("mybot_slam")


    use_rviz = LaunchConfiguration("use_rviz")
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        condition=IfCondition(use_rviz),
        arguments=["-d", PathJoinSubstitution([pkg_slam_share, "rviz", "slam.rviz"])],
        parameters=[{"use_sim_time": True}],
    )

    # SLAM Toolbox — lifecycle-managed, via online_async_launch.py.
    # slam_params.yaml already has scan_topic set to /scan_filtered.
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_slam_share, "launch", "online_async_launch.py"])
        ),
        launch_arguments={
            "use_sim_time": "true",
            "autostart": "true",
        }.items(),
    )

    ekf = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            os.path.join(get_package_share_directory("mybot_slam"), "config", "ekf.yaml"),
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument("use_rviz", default_value="true"),
        rviz,
        slam,
        ekf,
    ])
