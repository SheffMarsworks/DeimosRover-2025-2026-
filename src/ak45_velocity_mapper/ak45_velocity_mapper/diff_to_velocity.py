#!/usr/bin/env python3
"""Convert /diff_drive_controller/cmd_vel into /velocity_controller/commands.

Input:
  geometry_msgs/msg/Twist on /diff_drive_controller/cmd_vel

Output:
  std_msgs/msg/Float64MultiArray on /velocity_controller/commands
  data order: [motor_1, motor_2, motor_3, motor_4]

Default wheel grouping:
  left side  = motor_1, motor_3
  right side = motor_2, motor_4
"""

from __future__ import annotations

import math
from typing import List

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class DiffToVelocity(Node):
    """Map differential-drive velocity commands to four wheel joint velocities."""

    def __init__(self) -> None:
        super().__init__('diff_to_velocity')

        self.declare_parameter('cmd_vel_topic', '/diff_drive_controller/cmd_vel')
        self.declare_parameter('velocity_command_topic', '/velocity_controller/commands')
        self.declare_parameter('wheel_radius', 0.10)       # metres
        self.declare_parameter('wheel_separation', 0.50)   # metres, left-right track width
        self.declare_parameter('max_wheel_velocity', 5.44) # rad/s, matches current URDF limit
        self.declare_parameter('publish_rate', 50.0)       # Hz
        self.declare_parameter('cmd_timeout', 0.5)         # seconds
        self.declare_parameter('linear_deadband', 0.0)
        self.declare_parameter('angular_deadband', 0.0)

        # Output order is [motor_1, motor_2, motor_3, motor_4].
        # Default signs match the user's manual forward test:
        #   [0.5, -0.5, 0.5, 0.5]
        # Change this in config if any wheel rotates the wrong way.
        self.declare_parameter('motor_signs', [1.0, -1.0, 1.0, 1.0])

        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.velocity_command_topic = self.get_parameter('velocity_command_topic').value
        self.wheel_radius = float(self.get_parameter('wheel_radius').value)
        self.wheel_separation = float(self.get_parameter('wheel_separation').value)
        self.max_wheel_velocity = float(self.get_parameter('max_wheel_velocity').value)
        self.publish_rate = float(self.get_parameter('publish_rate').value)
        self.cmd_timeout = float(self.get_parameter('cmd_timeout').value)
        self.linear_deadband = float(self.get_parameter('linear_deadband').value)
        self.angular_deadband = float(self.get_parameter('angular_deadband').value)
        self.motor_signs = [float(x) for x in self.get_parameter('motor_signs').value]

        self._validate_parameters()

        self.last_linear_x = 0.0
        self.last_angular_z = 0.0
        self.last_cmd_time = self.get_clock().now()
        self.has_command = False

        self.command_pub = self.create_publisher(
            Float64MultiArray,
            self.velocity_command_topic,
            10,
        )
        self.cmd_sub = self.create_subscription(
            Twist,
            self.cmd_vel_topic,
            self.cmd_callback,
            10,
        )

        timer_period = 1.0 / self.publish_rate
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info(
            'Diff-to-velocity mapper started: '
            f'{self.cmd_vel_topic} -> {self.velocity_command_topic}'
        )
        self.get_logger().info(
            'Wheel model: '
            f'radius={self.wheel_radius:.3f} m, '
            f'separation={self.wheel_separation:.3f} m, '
            f'max={self.max_wheel_velocity:.3f} rad/s, '
            f'motor_signs={self.motor_signs}'
        )

    def _validate_parameters(self) -> None:
        if self.wheel_radius <= 0.0:
            raise ValueError('wheel_radius must be > 0')
        if self.wheel_separation < 0.0:
            raise ValueError('wheel_separation must be >= 0')
        if self.publish_rate <= 0.0:
            raise ValueError('publish_rate must be > 0')
        if self.cmd_timeout <= 0.0:
            raise ValueError('cmd_timeout must be > 0')
        if len(self.motor_signs) != 4:
            raise ValueError('motor_signs must contain exactly 4 values')

    def cmd_callback(self, msg: Twist) -> None:
        self.last_linear_x = self._apply_deadband(float(msg.linear.x), self.linear_deadband)
        self.last_angular_z = self._apply_deadband(float(msg.angular.z), self.angular_deadband)
        self.last_cmd_time = self.get_clock().now()
        self.has_command = True

    @staticmethod
    def _apply_deadband(value: float, deadband: float) -> float:
        return 0.0 if abs(value) < deadband else value

    def timer_callback(self) -> None:
        now = self.get_clock().now()
        age = (now - self.last_cmd_time).nanoseconds / 1e9

        if (not self.has_command) or age > self.cmd_timeout:
            self.publish_wheel_commands([0.0, 0.0, 0.0, 0.0])
            return

        wheel_commands = self.calculate_wheel_commands(
            self.last_linear_x,
            self.last_angular_z,
        )
        self.publish_wheel_commands(wheel_commands)

    def calculate_wheel_commands(self, linear_x: float, angular_z: float) -> List[float]:
        """Return [motor_1, motor_2, motor_3, motor_4] velocity commands in rad/s."""
        left_velocity = (
            linear_x - angular_z * self.wheel_separation * 0.5
        ) / self.wheel_radius
        right_velocity = (
            linear_x + angular_z * self.wheel_separation * 0.5
        ) / self.wheel_radius

        raw = [left_velocity, right_velocity, left_velocity, right_velocity]
        signed = [raw[i] * self.motor_signs[i] for i in range(4)]
        return [self._clamp(value, self.max_wheel_velocity) for value in signed]

    @staticmethod
    def _clamp(value: float, limit: float) -> float:
        if limit <= 0.0 or not math.isfinite(limit):
            return value
        return max(-limit, min(limit, value))

    def publish_wheel_commands(self, commands: List[float]) -> None:
        msg = Float64MultiArray()
        msg.data = commands
        self.command_pub.publish(msg)


def main(args: List[str] | None = None) -> None:
    rclpy.init(args=args)
    node = DiffToVelocity()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop motors before shutdown.
        node.publish_wheel_commands([0.0, 0.0, 0.0, 0.0])
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
