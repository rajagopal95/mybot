import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    nav2_dir = get_package_share_directory('mybot_navigation')
    slam_dir = get_package_share_directory('mybot_slam')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    publish_initial_pose = LaunchConfiguration('publish_initial_pose')
    initial_pose_x = LaunchConfiguration('initial_pose_x')
    initial_pose_y = LaunchConfiguration('initial_pose_y')
    initial_pose_yaw = LaunchConfiguration('initial_pose_yaw')

    declare_map = DeclareLaunchArgument(
        'map', default_value=os.path.join(slam_dir, 'maps', 'hospital.yaml'))
    declare_params = DeclareLaunchArgument(
        'params_file', default_value=os.path.join(nav2_dir, 'config', 'nav2_params.yaml'))

    ekf_config = os.path.join(nav2_dir, 'config', 'ekf.yaml')

    initial_pose_node = Node(
        package='mybot_navigation',
        executable='auto_initial_pose.py',
        name='auto_initial_pose',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'enabled': publish_initial_pose,
            'initial_pose_x': initial_pose_x,
            'initial_pose_y': initial_pose_y,
            'initial_pose_yaw': initial_pose_yaw,
        }],
    )

    ekf_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            ekf_config,
            {"use_sim_time": use_sim_time}

        ]
    )

    # scan_filter_node = Node(
    #     package="laser_filters",
    #     executable="scan_to_scan_filter_chain",
    #     name="scan_filter_node",
    #     output="screen",
    #     parameters=[os.path.join(slam_dir, 'config', 'scan_filter.yaml'),
    #                 {"use_sim_time": True}],
    #     remappings=[("scan", "/scan"), ("scan_filtered", "/scan_filtered")],
    # )

    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': params_file
        }.items()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(nav2_dir, 'rviz', 'nav2.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        declare_map,
        declare_params,
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('publish_initial_pose', default_value='true', description='Publish the AMCL initial pose after AMCL subscribes.'),
        DeclareLaunchArgument('initial_pose_x', default_value='0.0', description='Initial map-frame x coordinate.'),
        DeclareLaunchArgument('initial_pose_y', default_value='0.0', description='Initial map-frame y coordinate.'),
        DeclareLaunchArgument('initial_pose_yaw', default_value='0.0', description='Initial map-frame yaw in radians.'),
        ekf_node,
        nav2_bringup_launch,
        initial_pose_node,
        # scan_filter_node,
        rviz_node
    ])
