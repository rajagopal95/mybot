import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    LogInfo,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    use_camera = LaunchConfiguration("use_camera")

    pkg_description = get_package_share_directory("mybot_description")
    pkg_gazebo = get_package_share_directory("mybot_gazebo")
    pkg_gazebo_ros = get_package_share_directory("gazebo_ros")

    # spawn_entity.py rewrites package:// to model://. Gazebo resolves
    # model://mybot_description/... only if the directory CONTAINING
    # mybot_description is on GAZEBO_MODEL_PATH, and /usr/share/gazebo-11/models
    # holds ground_plane + sun used by hospital.world. Setting it here (instead of
    # in a terminal) guarantees gzserver and gzclient both inherit it.
    model_path = ":".join([
        "/usr/share/gazebo-11/models",
        os.path.dirname(pkg_description),
        # aws_robomaker_warehouse_* models used by the warehouse worlds
        os.path.join(pkg_gazebo, "models"),
    ])

    # world_name: any file in mybot_gazebo/worlds (hospital.world, small_warehouse.world, ...)
    # Some warehouse model files reference meshes as "models/<name>/meshes/..." (no model://).
    # Gazebo finds those only if the folder CONTAINING "models" is on GAZEBO_RESOURCE_PATH.
    resource_path = ":".join([
        p for p in [
            os.environ.get("GAZEBO_RESOURCE_PATH", "/usr/share/gazebo-11"),
            pkg_gazebo,
        ] if p
    ])

    world_file = PathJoinSubstitution([
        pkg_gazebo,
        "worlds",
        LaunchConfiguration("world_name"),
    ])

    # xacro_name: any file in mybot_description/urdf
    xacro_file = PathJoinSubstitution([
        pkg_description,
        "urdf",
        LaunchConfiguration("xacro_name"),
    ])

    controllers_file = os.path.join(
        pkg_gazebo,
        "config",
        "fork_controllers.yaml",
    )

    declare_world = DeclareLaunchArgument(
        "world_name",
        default_value="no_roof_small_warehouse.world",
        description="World file in mybot_gazebo/worlds.",
    )
    declare_xacro = DeclareLaunchArgument(
        "xacro_name",
        default_value="fork_redesigned_urdf.xacro",
        description="Robot xacro in mybot_description/urdf.",
    )
    declare_x = DeclareLaunchArgument("x_pose", default_value="0.0")
    declare_y = DeclareLaunchArgument("y_pose", default_value="0.0")
    declare_yaw = DeclareLaunchArgument("yaw_pose", default_value="0.0")

    declare_use_camera = DeclareLaunchArgument(
        "use_camera",
        default_value="false",
        description="Compatibility argument; fork model has no camera.",
    )

    # Expand fork_redesigned_urdf.xacro.
    # Compact the XML to avoid the long ROS parameter override problem.
    robot_description_content = Command([
        "bash -c \"xacro ",
        xacro_file,
        " use_camera:=",
        use_camera,
        " | python3 -c 'import sys,xml.etree.ElementTree as ET; "
        "sys.stdout.write(ET.tostring("
        "ET.fromstring(sys.stdin.read()),"
        "encoding=\\\"unicode\\\"))' "
        "| tr -s '\\n' ' '\"",
    ])

    robot_description = ParameterValue(
        robot_description_content,
        value_type=str,
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_gazebo_ros,
                "launch",
                "gazebo.launch.py",
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
        name="spawn_fork_robot",
        output="screen",
        arguments=[
            "-entity",
            "fork_robot",
            "-topic",
            "robot_description",
            "-x",
            LaunchConfiguration("x_pose"),
            "-y",
            LaunchConfiguration("y_pose"),
            "-z",
            "0.05",
            "-Y",
            LaunchConfiguration("yaw_pose"),
        ],
    )

    # gazebo_ros2_control creates /controller_manager from the Xacro plugin.
    # Start the controllers after Gazebo + ros2_control are ready.
    spawn_joint_state_broadcaster = TimerAction(
        period=8.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                name="fork_joint_state_broadcaster_spawner",
                arguments=[
                    "joint_state_broadcaster",
                    "--controller-manager",
                    "/controller_manager",
                ],
                output="screen",
            )
        ],
    )

    scan_filter = Node(
        package="laser_filters",
        executable="scan_to_scan_filter_chain",
        name="scan_filter_node",
        output="screen",
        parameters=[
            os.path.join(pkg_gazebo, "config", "fork_scan_filter.yaml"),
            {"use_sim_time": True},
        ],
        remappings=[
            ("scan", "/scan"),
            ("scan_filtered", "/scan_filtered"),
        ],
    )

    spawn_diff_drive = TimerAction(
        period=10.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                name="fork_diff_drive_spawner",
                arguments=[
                    "diff_drive_controller",
                    "--controller-manager",
                    "/controller_manager",
                ],
                output="screen",
            )
        ],
    )

    return LaunchDescription([
        SetEnvironmentVariable("GAZEBO_MODEL_PATH", model_path),
        SetEnvironmentVariable("GAZEBO_RESOURCE_PATH", resource_path),
        SetEnvironmentVariable("GAZEBO_MODEL_DATABASE_URI", ""),
        LogInfo(msg="GAZEBO_MODEL_PATH=" + model_path),
        declare_world,
        declare_xacro,
        declare_x,
        declare_y,
        declare_yaw,
        declare_use_camera,
        gazebo,
        robot_state_publisher,
        TimerAction(
            period=2.0,
            actions=[spawn_robot],
        ),
        spawn_joint_state_broadcaster,
        spawn_diff_drive,
        scan_filter,
    ])