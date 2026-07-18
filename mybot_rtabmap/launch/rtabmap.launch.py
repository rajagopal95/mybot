from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

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
        rgbd_odometry,
        rtabmap_slam,
        rviz,
    ])
