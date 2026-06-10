#!/usr/bin/env python3
"""Send a single NavigateToPose goal to Nav2.

Usage:
    ros2 run rover_navigation send_goal X Y [YAW_DEG]

Example:
    ros2 run rover_navigation send_goal 2.0 1.0 90
"""

import math
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


def yaw_to_quaternion(yaw):
    """Return (z, w) of a quaternion for a yaw rotation (radians)."""
    return math.sin(yaw / 2.0), math.cos(yaw / 2.0)


class GoalSender(Node):
    def __init__(self):
        super().__init__("rover_send_goal")
        self._client = ActionClient(self, NavigateToPose, "navigate_to_pose")

    def send(self, x, y, yaw_deg):
        self.get_logger().info("Waiting for navigate_to_pose action server...")
        if not self._client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("Action server unavailable. Is Nav2 running?")
            return False

        yaw = math.radians(yaw_deg)
        qz, qw = yaw_to_quaternion(yaw)

        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = float(x)
        goal.pose.pose.position.y = float(y)
        goal.pose.pose.orientation.z = qz
        goal.pose.pose.orientation.w = qw

        self.get_logger().info(
            f"Sending goal: x={x}, y={y}, yaw={yaw_deg} deg (frame=map)"
        )
        send_future = self._client.send_goal_async(
            goal, feedback_callback=self._on_feedback
        )
        rclpy.spin_until_future_complete(self, send_future)
        handle = send_future.result()

        if not handle.accepted:
            self.get_logger().error("Goal was rejected by Nav2.")
            return False

        self.get_logger().info("Goal accepted. Navigating...")
        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        self.get_logger().info("Navigation finished.")
        return True

    def _on_feedback(self, feedback):
        remaining = feedback.feedback.distance_remaining
        self.get_logger().info(f"Distance remaining: {remaining:.2f} m")


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: ros2 run rover_navigation send_goal X Y [YAW_DEG]")
        return

    x = float(args[0])
    y = float(args[1])
    yaw_deg = float(args[2]) if len(args) >= 3 else 0.0

    rclpy.init()
    node = GoalSender()
    try:
        node.send(x, y, yaw_deg)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
