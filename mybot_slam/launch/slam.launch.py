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

    rviz_config = os.path.join(
        get_package_share_directory("mybot_slam"),
        "rviz",
        "slam.rviz"
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

        slam_toolbox,
        rviz,

    ])
