#!/usr/bin/env python3
"""Publish the configured AMCL initial pose after AMCL subscribes."""

import math

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.node import Node


class AutoInitialPose(Node):
    """Publish several initial-pose messages so AMCL reliably receives one."""

    def __init__(self):
        super().__init__('auto_initial_pose')
        # use_sim_time is often set via --ros-args already; do not redeclare.
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', True)
        self.declare_parameter('enabled', True)
        self.declare_parameter('initial_pose_x', 0.0)
        self.declare_parameter('initial_pose_y', 0.0)
        self.declare_parameter('initial_pose_yaw', 0.0)
        self.declare_parameter('publish_count', 5)
        self.declare_parameter('publish_period', 1.0)

        self.enabled = bool(self.get_parameter('enabled').value)
        self.remaining = int(self.get_parameter('publish_count').value)
        self.publisher = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.timer = self.create_timer(
            float(self.get_parameter('publish_period').value), self._publish_initial_pose
        )

        if self.enabled:
            self.get_logger().info('Waiting for AMCL to subscribe to /initialpose.')
        else:
            self.get_logger().info('Automatic initial-pose publishing is disabled.')

    def _publish_initial_pose(self):
        if not self.enabled:
            return
        if self.publisher.get_subscription_count() == 0:
            return

        yaw = float(self.get_parameter('initial_pose_yaw').value)
        message = PoseWithCovarianceStamped()
        message.header.frame_id = 'map'
        # Stamp 0 => TF uses latest transform (avoids sim-time extrapolation drops).
        message.header.stamp.sec = 0
        message.header.stamp.nanosec = 0
        message.pose.pose.position.x = float(self.get_parameter('initial_pose_x').value)
        message.pose.pose.position.y = float(self.get_parameter('initial_pose_y').value)
        message.pose.pose.orientation.z = math.sin(yaw / 2.0)
        message.pose.pose.orientation.w = math.cos(yaw / 2.0)
        # 0.5 m XY and 15 degree yaw standard deviations.
        message.pose.covariance[0] = 0.25
        message.pose.covariance[7] = 0.25
        message.pose.covariance[35] = math.radians(15.0) ** 2
        self.publisher.publish(message)
        self.remaining -= 1
        self.get_logger().info(
            f'Published AMCL initial pose: x={message.pose.pose.position.x:.2f}, '
            f'y={message.pose.pose.position.y:.2f}, yaw={yaw:.2f} rad '
            f'({self.remaining} repeats remaining).'
        )
        if self.remaining <= 0:
            self.timer.cancel()


def main():
    rclpy.init()
    node = AutoInitialPose()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
