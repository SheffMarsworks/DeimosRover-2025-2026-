#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2


class CameraViewer(Node):
    def __init__(self):
        super().__init__('camera_viewer')

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            10
        )

        self.bridge = CvBridge()

        self.get_logger().info("Camera viewer started")

    def listener_callback(self, msg):
        # Convert ROS Image → OpenCV BGR image
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        cv2.imshow("DFK 33UR0521 - ROS2 Camera", frame)
        cv2.waitKey(1)


def main():
    rclpy.init()
    node = CameraViewer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
