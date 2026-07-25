import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration("use_sim_time")

    slam_params = os.path.join(
        get_package_share_directory("mybot_slam"),
        "config",
        "mapper_params_online_async.yaml"
    )

    ekf_config = os.path.join(
        get_package_share_directory("mybot_slam"),
        "config",
        "ekf.yaml"
    )

    rviz_config = os.path.join(
        get_package_share_directory("mybot_slam"),
        "rviz",
        "slam.rviz"
    )

    ekf_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            ekf_config,
            {"use_sim_time": use_sim_time}
        ],
        remappings=[
            ("odometry/filtered", "/odom_filtered")
        ]
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

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("slam_toolbox"),
                "launch",
                "online_async_launch.py"
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "slam_params_file": slam_params,
        }.items()
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

        ekf_node,
        scan_filter,
        slam_toolbox,
        rviz,

    ])