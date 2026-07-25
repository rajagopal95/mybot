import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration("use_sim_time")
    resolution = LaunchConfiguration("resolution")
    publish_period = LaunchConfiguration("publish_period_sec")

    pkg_slam = get_package_share_directory("mybot_slam")

    config_dir = os.path.join(pkg_slam, "config")
    rviz_config = os.path.join(pkg_slam, "rviz", "slam.rviz")
    ekf_config = os.path.join(pkg_slam, "config", "ekf.yaml")

    return LaunchDescription([

        SetEnvironmentVariable(
            "RCUTILS_LOGGING_BUFFERED_STREAM",
            "1"
        ),

        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true"
        ),

        DeclareLaunchArgument(
            "resolution",
            default_value="0.05"
        ),

        DeclareLaunchArgument(
            "publish_period_sec",
            default_value="1.0"
        ),

        #
        # EKF
        #
        Node(
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
        ),

        #
        # Scan filter (removes robot self-hits before SLAM sees them)
        #
        Node(
            package="laser_filters",
            executable="scan_to_scan_filter_chain",
            name="scan_filter_node",
            output="screen",
            parameters=[
                os.path.join(config_dir, "scan_filter.yaml"),
                {"use_sim_time": use_sim_time}
            ],
            remappings=[
                ("scan", "scan_raw"),
                ("scan_filtered", "scan"),
            ]
        ),

        #
        # Cartographer
        #
        Node(
            package="cartographer_ros",
            executable="cartographer_node",
            name="cartographer_node",
            output="screen",
            parameters=[
                {
                    "use_sim_time": use_sim_time
                }
            ],
            arguments=[
                "-configuration_directory",
                config_dir,
                "-configuration_basename",
                "cartographer.lua",
            ],
            remappings=[
                ("scan", "/scan"),
                ("imu", "/imu"),
                ("odom", "/odom_filtered")
            ]
        ),

        #
        # Occupancy Grid
        #
        Node(
            package="cartographer_ros",
            executable="cartographer_occupancy_grid_node",
            name="occupancy_grid_node",
            output="screen",
            parameters=[
                {
                    "use_sim_time": use_sim_time
                }
            ],
            arguments=[
                "-resolution",
                resolution,
                "-publish_period_sec",
                publish_period,
            ]
        ),

        #
        # RViz
        #
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=[
                "-d",
                rviz_config
            ],
            parameters=[
                {
                    "use_sim_time": use_sim_time
                }
            ]
        ),
    ])
