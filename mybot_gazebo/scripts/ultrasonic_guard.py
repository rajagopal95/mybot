#!/usr/bin/env python3
"""Ultrasonic guard for the forklift AMR (works in sim and on hardware).

Sits between Nav2 and the diff-drive controller:

    Nav2  ->  /cmd_vel_raw  ->  [ultrasonic_guard]  ->  /cmd_vel  ->  diff_drive_controller

Behaviour
  * Driving forward  -> watches the two front sensors.
  * Driving backward -> watches the two rear (fork side) sensors.
  * Velocity is scaled linearly from 100 % at *_slow down to 0 % at *_stop.
    Linear and angular are scaled together, so the arc is preserved.
  * Side sensors: if either reads below side_stop while moving, steering is
    frozen and speed is capped at 30 % (creep straight out, no turning into the wall).
  * Pure in-place rotation (v = 0) is NOT guarded: the fork tips sweep far outside
    where the sensors look.

Hardware notes
  * The ESP32 should publish +inf (not 0) on a missed echo.
  * Readings below the sensor's min_range are treated as "obstacle very close".
  * Set stop_on_stale:=true on the real robot so a dead sensor stops the robot.

Run:
    python3 ultrasonic_guard.py --ros-args -p input_topic:=/cmd_vel_raw -p output_topic:=/cmd_vel
"""
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Range

GROUPS = {
    'front': ['ultrasonic_front_left', 'ultrasonic_front_right'],
    'rear': ['ultrasonic_rear_left', 'ultrasonic_rear_right'],
    'side': ['ultrasonic_side_left', 'ultrasonic_side_right'],
}


class UltrasonicGuard(Node):
    def __init__(self):
        super().__init__('ultrasonic_guard')
        defaults = {
            'input_topic': '/cmd_vel_raw',
            'output_topic': '/cmd_vel',
            'front_stop': 0.25,
            'front_slow': 0.60,
            'rear_stop': 0.30,
            'rear_slow': 0.70,
            'side_stop': 0.05,
            'stale_after': 0.5,
            'stop_on_stale': False,
        }
        for key, value in defaults.items():
            self.declare_parameter(key, value)

        self.ranges = {}  # sensor name -> (range_m, rclpy Time)
        for names in GROUPS.values():
            for name in names:
                self.create_subscription(
                    Range, '/' + name,
                    lambda msg, n=name: self.on_range(n, msg),
                    qos_profile_sensor_data)

        self.pub = self.create_publisher(Twist, self.p('output_topic'), 10)
        self.create_subscription(Twist, self.p('input_topic'), self.on_cmd, 10)
        self.get_logger().info(
            f"guarding {self.p('input_topic')} -> {self.p('output_topic')}")

    def p(self, key):
        return self.get_parameter(key).value

    def on_range(self, name, msg):
        r = msg.range
        if math.isnan(r):
            return
        if r < msg.min_range:
            r = msg.min_range          # too close to measure -> treat as blocked
        elif math.isinf(r) or r >= msg.max_range:
            r = math.inf               # nothing in range
        self.ranges[name] = (r, self.get_clock().now())

    def group_min(self, group):
        now = self.get_clock().now()
        best = math.inf
        stale = False
        for name in GROUPS[group]:
            item = self.ranges.get(name)
            age = (now - item[1]).nanoseconds * 1e-9 if item else math.inf
            if age > self.p('stale_after'):
                stale = True
                continue
            best = min(best, item[0])
        return best, stale

    @staticmethod
    def scale(r, stop, slow):
        if r <= stop:
            return 0.0
        if r >= slow:
            return 1.0
        return (r - stop) / (slow - stop)

    def on_cmd(self, cmd):
        v = cmd.linear.x
        k = 1.0
        angular_locked = False
        reason = ''

        if v != 0.0:
            group = 'front' if v > 0.0 else 'rear'
            r, stale = self.group_min(group)
            k = self.scale(r, self.p(group + '_stop'), self.p(group + '_slow'))
            reason = f'{group} {r:.2f} m'
            if stale and self.p('stop_on_stale'):
                k = 0.0
                reason = f'{group} sensor data stale'

            side, _ = self.group_min('side')
            if side <= self.p('side_stop'):
                angular_locked = True
                k = min(k, 0.3)
                reason = f'side {side:.2f} m'

        out = Twist()
        out.linear.x = v * k
        out.linear.y = cmd.linear.y
        out.linear.z = cmd.linear.z
        out.angular.x = cmd.angular.x
        out.angular.y = cmd.angular.y
        if angular_locked:
            out.angular.z = 0.0
        else:
            out.angular.z = cmd.angular.z * (k if v != 0.0 else 1.0)

        if k < 1.0 or angular_locked:
            self.get_logger().warn(
                f'limiting motion ({reason}), scale={k:.2f}',
                throttle_duration_sec=2.0)
        self.pub.publish(out)


def main():
    rclpy.init()
    node = UltrasonicGuard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
