#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_slam_share = FindPackageShare("mybot_slam")

    # Scan filter — drops points inside the robot's own footprint before
    # they reach slam_toolbox
    scan_filter_node = Node(
        package="laser_filters",
        executable="scan_to_scan_filter_chain",
        name="scan_filter_node",
        output="screen",
        parameters=[
            PathJoinSubstitution([pkg_slam_share, "config", "scan_filter.yaml"]),
            {"use_sim_time": True},
        ],
        remappings=[
            ("scan", "/scan"),
            ("scan_filtered", "/scan_filtered"),
        ],
    )

    # RViz. mapping.sh passes use_rviz:=false for the forklift and opens
    # rviz/fork_mapping.rviz itself.
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

    return LaunchDescription([
        DeclareLaunchArgument("use_rviz", default_value="true"),
        scan_filter_node,
        rviz,
        slam,
    ])
