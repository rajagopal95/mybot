#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_gazebo_share = FindPackageShare("mybot_gazebo")
    pkg_slam_share = FindPackageShare("mybot_slam")

    # Gazebo + robot spawn + controllers + robot_state_publisher
    # (robot_state_publisher already lives inside mybot_gazebo/launch/gazebo.launch.py,
    # so it isn't duplicated here)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_gazebo_share, "launch", "gazebo.launch.py"])
        )
    )

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

    # RViz
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
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

        # Start Gazebo + robot first
        gazebo,

        # Give Gazebo/controllers time to fully come up before starting
        # the scan filter, RViz, and SLAM
        TimerAction(
            period=10.0,
            actions=[scan_filter_node, rviz, slam],
        ),
    ])
