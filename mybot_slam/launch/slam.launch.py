import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration("use_sim_time")

    slam_params = os.path.join(
        get_package_share_directory("mybot_slam"),
        "config",
        "mapper_params_online_async.yaml"
    )

    rviz_config = os.path.join(
        get_package_share_directory("mybot_slam"),
        "rviz",
        "slam.rviz"
    )

    scan_filter = Node(
        package="laser_filters",
        executable="scan_to_scan_filter_chain",
        name="scan_filter_node",
        output="screen",
        parameters=[
            os.path.join(get_package_share_directory("mybot_slam"), "config", "scan_filter.yaml"),
            {"use_sim_time": use_sim_time}
        ],
        remappings=[
            ("scan", "scan_raw"),
            ("scan_filtered", "scan"),
        ]
    )

    slam_toolbox = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[
            slam_params,
            {"use_sim_time": use_sim_time}
        ]
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config],
        parameters=[
            {"use_sim_time": use_sim_time}
        ],
        output="screen",
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true"
        ),

        scan_filter,
        slam_toolbox,
        rviz,

    ])
