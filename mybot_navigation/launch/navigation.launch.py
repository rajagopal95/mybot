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

    declare_map = DeclareLaunchArgument(
        'map', default_value=os.path.join(slam_dir, 'maps', 'hospital.yaml'))
    declare_params = DeclareLaunchArgument(
        'params_file', default_value=os.path.join(nav2_dir, 'config', 'nav2_params.yaml'))

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
        nav2_bringup_launch,
        rviz_node
    ])
