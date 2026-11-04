from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument(
            "filter_config",
            default_value=PathJoinSubstitution(
                [FindPackageShare("mybot_slam"), "config", "scan_filter.yaml"]),
        ),
        Node(
            package="laser_filters",
            executable="scan_to_scan_filter_chain",
            name="scan_filter_node",
            output="screen",
            parameters=[
                LaunchConfiguration("filter_config"),
                {"use_sim_time": LaunchConfiguration("use_sim_time")},
            ],
            remappings=[("scan", "/scan"), ("scan_filtered", "/scan_filtered")],
        ),
    ])