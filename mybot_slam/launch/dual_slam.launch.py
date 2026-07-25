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
    
    slam_toolbox_params = os.path.join(config_dir, "mapper_params_dual.yaml")
    ekf_config = os.path.join(config_dir, "ekf.yaml")
    scan_filter_config = os.path.join(config_dir, "scan_filter.yaml")
    rviz_config = os.path.join(pkg_slam, "rviz", "dual_slam.rviz")

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

        # 1. EKF Odometry Filter
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

        # 2. Laser Scan Filter
        Node(
            package="laser_filters",
            executable="scan_to_scan_filter_chain",
            name="scan_filter_node",
            output="screen",
            parameters=[
                scan_filter_config,
                {"use_sim_time": use_sim_time}
            ],
            remappings=[
                ("scan", "scan_raw"),
                ("scan_filtered", "scan"),
            ]
        ),

        # 3. SLAM Toolbox Node (map_frame: map_slam_toolbox -> /map_slam_toolbox)
        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox_dual",
            output="screen",
            parameters=[
                slam_toolbox_params,
                {"use_sim_time": use_sim_time}
            ],
            remappings=[
                ("map", "/map_slam_toolbox"),
                ("map_metadata", "/map_slam_toolbox_metadata")
            ]
        ),

        # 4. Cartographer Node (map_frame: map_cartographer -> odom)
        Node(
            package="cartographer_ros",
            executable="cartographer_node",
            name="cartographer_node_dual",
            output="screen",
            parameters=[
                {"use_sim_time": use_sim_time}
            ],
            arguments=[
                "-configuration_directory", config_dir,
                "-configuration_basename", "slam_dual.lua",
            ],
            remappings=[
                ("scan", "/scan"),
                ("imu", "/imu"),
                ("odom", "/odom_filtered")
            ]
        ),

        # 5. Cartographer Occupancy Grid Node (publishes to /map_cartographer)
        Node(
            package="cartographer_ros",
            executable="cartographer_occupancy_grid_node",
            name="occupancy_grid_node_dual",
            output="screen",
            parameters=[
                {"use_sim_time": use_sim_time}
            ],
            arguments=[
                "-resolution", resolution,
                "-publish_period_sec", publish_period,
            ],
            remappings=[
                ("map", "/map_cartographer")
            ]
        ),

        # 6. RViz2 Visualizer (dual maps)
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2_dual_slam",
            output="screen",
            arguments=[
                "-d", rviz_config
            ],
            parameters=[
                {"use_sim_time": use_sim_time}
            ]
        ),
    ])
