#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')

        # Declare a ROS2 parameter for the device index (default: 1 for /dev/video1)
        self.declare_parameter('device_index', 1)
        device_index = self.get_parameter('device_index').get_parameter_value().integer_value

        self.publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        self.bridge = CvBridge()

        self.get_logger().info(f"Opening camera at /dev/video{device_index} (DFK 33UR0521)")
        self.cap = cv2.VideoCapture(device_index, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.cap.isOpened():
            self.get_logger().error(f"Cannot open camera /dev/video{device_index} (DFK 33UR0521)")
            raise RuntimeError("Camera not found")

        self.timer = self.create_timer(0.033, self.timer_callback)  # ~30 FPS
        self.get_logger().info(f"Camera publisher started (DFK 33UR0521, /dev/video{device_index}, YUYV 640x480 @ 30fps)")

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Failed to grab frame")
            return
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = CameraPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.cap.release()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
