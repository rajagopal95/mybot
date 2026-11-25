import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from nav2_common.launch import ReplaceString


def generate_launch_description():
    nav2_dir = get_package_share_directory('mybot_navigation')
    slam_dir = get_package_share_directory('mybot_slam')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    init_x = LaunchConfiguration('initial_pose_x')
    init_y = LaunchConfiguration('initial_pose_y')
    init_yaw = LaunchConfiguration('initial_pose_yaw')
    auto_init = LaunchConfiguration('auto_initial_pose')

    # Replan when IsPathValid fails (lidar-marked static obstacle on path).
    bt_xml = os.path.join(
        nav2_dir, 'behavior_trees', 'navigate_static_replan_w_recovery.xml')
    configured_params = ReplaceString(
        source_file=params_file,
        replacements={'__MYBOT_BT_XML__': bt_xml})

    ekf_config = os.path.join(nav2_dir, 'config', 'ekf.yaml')

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': use_sim_time}],
    )

    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': configured_params,
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(nav2_dir, 'rviz', 'nav2.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
    )

    # Auto 2D Pose Estimate so you do not click it every RViz open.
    # Waits until AMCL subscribes to /initialpose, then publishes N times.
    initial_pose_node = Node(
        package='mybot_navigation',
        executable='publish_initial_pose.py',
        name='auto_initial_pose',
        output='screen',
        condition=IfCondition(auto_init),
        parameters=[{
            'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
            'enabled': True,
            'initial_pose_x': ParameterValue(init_x, value_type=float),
            'initial_pose_y': ParameterValue(init_y, value_type=float),
            'initial_pose_yaw': ParameterValue(init_yaw, value_type=float),
            'publish_count': 5,
            'publish_period': 0.5,
        }],
    )

    # Gazebo sometimes stays paused; wheels then ignore cmd_vel (odom=0 forever).
    unpause_gazebo = TimerAction(
        period=2.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'service', 'call', '/unpause_physics',
                 'std_srvs/srv/Empty', '{}'],
            output='screen',
        )],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'map', default_value=os.path.join(slam_dir, 'maps', 'hospital.yaml')),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav2_dir, 'config', 'nav2_params.yaml')),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'auto_initial_pose', default_value='true',
            description='Publish /initialpose automatically (skip RViz 2D Pose Estimate)'),
        DeclareLaunchArgument('initial_pose_x', default_value='0.0'),
        DeclareLaunchArgument('initial_pose_y', default_value='0.0'),
        DeclareLaunchArgument('initial_pose_yaw', default_value='0.0'),
        ekf_node,
        nav2_bringup_launch,
        rviz_node,
        # Start immediately; node waits until AMCL subscribes.
        initial_pose_node,
        unpause_gazebo,
    ])
