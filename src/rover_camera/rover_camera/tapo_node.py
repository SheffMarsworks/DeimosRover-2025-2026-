import cv2
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class TapoCamera(Node):

    def __init__(self):
        super().__init__('tapo_camera')

        self.declare_parameter('rtsp_url', '')

        self.rtsp_url = self.get_parameter(
            'rtsp_url'
        ).value

        self.bridge = CvBridge()

        self.publisher = self.create_publisher(
            Image,
            '/rover/camera/front/image_raw',
            10
        )

        self.cap = None

        if self.rtsp_url:
            self.cap = cv2.VideoCapture(
                self.rtsp_url
            )

        self.timer = self.create_timer(
            1.0 / 30.0,
            self.publish_frame
        )

    def publish_frame(self):

        if self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        msg = self.bridge.cv2_to_imgmsg(
            frame,
            encoding='bgr8'
        )

        self.publisher.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = TapoCamera()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

