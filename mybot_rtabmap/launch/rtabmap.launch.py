from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    xacro_file = PathJoinSubstitution([
        FindPackageShare('mybot_description'), 'urdf', 'mybot.urdf.xacro'
    ])

    robot_description = ParameterValue(
        Command([
            'xacro ', xacro_file, ' use_camera:=true'
        ]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}],
    )

    # Actual published topics from the camera plugin (verified via /robot_description dump):
    #   /camera/depth_camera/image_raw
    #   /camera/depth_camera/depth/image_raw
    #   /camera/depth_camera/camera_info
    rgb_topic = '/camera/depth_camera/image_raw'
    depth_topic = '/camera/depth_camera/depth/image_raw'
    camera_info_topic = '/camera/depth_camera/camera_info'

    rgbd_odometry = Node(
        package='rtabmap_odom',
        executable='rgbd_odometry',
        output='screen',
        parameters=[{
            'frame_id': 'base_footprint',
            'odom_frame_id': 'odom',
            'publish_tf': False,      # gazebo diff_drive already publishes odom->base_footprint
            'use_sim_time': use_sim_time,
            'approx_sync': True,
            'Reg/Force3DoF': 'true',  # ground robot, motion constrained to plane
        }],
        remappings=[
            ('rgb/image', rgb_topic),
            ('depth/image', depth_topic),
            ('rgb/camera_info', camera_info_topic),
            ('odom', '/rtabmap/odom'),
        ]
    )

    rtabmap_slam = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        output='screen',
        arguments=['-d'],  # delete previous database on start
        parameters=[{
            'frame_id': 'base_footprint',
            'odom_frame_id': 'odom',
            'subscribe_depth': True,
            'subscribe_rgb': True,
            'subscribe_scan': False,
            'use_sim_time': use_sim_time,
            'approx_sync': True,
            'Reg/Force3DoF': 'true',
            'Grid/3D': 'true',
            'cloud_output_voxelized': True,
        }],
        remappings=[
            ('rgb/image', rgb_topic),
            ('depth/image', depth_topic),
            ('rgb/camera_info', camera_info_topic),
            ('odom', '/rtabmap/odom'),
        ]
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        robot_state_publisher,
        rgbd_odometry,
        rtabmap_slam,
        rviz,
    ])
