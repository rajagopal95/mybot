import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg_description = get_package_share_directory("mybot_description")
    pkg_gazebo = get_package_share_directory("mybot_gazebo")
    pkg_gazebo_ros = get_package_share_directory("gazebo_ros")

    world_file = os.path.join(
        pkg_gazebo,
        "worlds",
        "hospital.world"
    )

    xacro_file = os.path.join(
        pkg_description,
        "urdf",
        "mybot.urdf.xacro"
    )

    robot_description = ParameterValue(
        Command(["xacro", " ", xacro_file]),
        value_type=str
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_gazebo_ros,
                "launch",
                "gazebo.launch.py"
            )
        ),
        launch_arguments={
            "world": world_file,
            "verbose": "true",
        }.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True,
            }
        ],
    )

    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        name="spawn_mybot",
        output="screen",
        arguments=[
            "-entity", "mybot",
            "-topic", "robot_description",
            "-z", "0.10",
        ],
    )

    delayed_spawn = TimerAction(
        period=2.0,
        actions=[spawn_robot],
    )

    # ---------------------------------------------------------------
    # ros2_control: spawn diff_drive_controller + joint_state_broadcaster
    # Delayed so Gazebo and controller_manager are fully up first.
    # ---------------------------------------------------------------
    spawn_diff_drive = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                name="diff_drive_spawner",
                arguments=["diff_drive_controller", "--controller-manager", "/controller_manager"],
                output="screen",
            )
        ],
    )

    spawn_joint_state_broadcaster = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                name="joint_state_broadcaster_spawner",
                arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
                output="screen",
            )
        ],
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        delayed_spawn,
        spawn_joint_state_broadcaster,
        spawn_diff_drive,
    ])
