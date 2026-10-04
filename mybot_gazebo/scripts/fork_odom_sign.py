#!/usr/bin/env python3
"""Publish /odom that matches Gazebo.

The wheel joints roll forward while their position decreases, and the
controller's negative radius multiplier turns that into a positive x.
Negate only the forward component and keep yaw, so a left turn stays left.
"""

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


def yaw_of(q):
    siny = 2.0 * (q.w * q.z + q.x * q.y)
    cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny, cosy)


class ForkOdomSign(Node):
    def __init__(self):
        super().__init__("fork_odom_sign")
        self.pub = self.create_publisher(Odometry, "/odom", 10)
        self.tf = TransformBroadcaster(self)
        self.last_x = None
        self.last_y = None
        self.last_yaw = 0.0
        self.x = 0.0
        self.y = 0.0
        self.create_subscription(Odometry, "/wheel_odom", self.on_odom, 10)

    def on_odom(self, msg):
        px = msg.pose.pose.position.x
        py = msg.pose.pose.position.y
        if self.last_x is not None:
            dx = px - self.last_x
            dy = py - self.last_y
            c = math.cos(self.last_yaw)
            s = math.sin(self.last_yaw)
            forward = -(c * dx + s * dy)
            sideways = -s * dx + c * dy
            self.x += c * forward - s * sideways
            self.y += s * forward + c * sideways
        self.last_x = px
        self.last_y = py
        self.last_yaw = yaw_of(msg.pose.pose.orientation)

        out = Odometry()
        out.header = msg.header
        out.child_frame_id = msg.child_frame_id
        out.pose.pose.position.x = self.x
        out.pose.pose.position.y = self.y
        out.pose.pose.position.z = msg.pose.pose.position.z
        out.pose.pose.orientation = msg.pose.pose.orientation
        out.pose.covariance = msg.pose.covariance
        out.twist.twist.linear.x = -msg.twist.twist.linear.x
        out.twist.twist.linear.y = msg.twist.twist.linear.y
        out.twist.twist.linear.z = msg.twist.twist.linear.z
        out.twist.twist.angular = msg.twist.twist.angular
        out.twist.covariance = msg.twist.covariance
        self.pub.publish(out)

        transform = TransformStamped()
        transform.header = msg.header
        transform.child_frame_id = msg.child_frame_id or "base_footprint"
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.rotation = msg.pose.pose.orientation
        self.tf.sendTransform(transform)


def main():
    rclpy.init()
    node = ForkOdomSign()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
