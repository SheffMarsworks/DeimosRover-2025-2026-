import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Float64MultiArray

class CmdVelToWheels(Node):
    def init(self):
        super().init("cmd_vel_to_wheels")
        self.L = 0.7      # wheel separation (try wider for skid-steer)
        self.r = 0.123    # wheel radius
        self.sub = self.create_subscription(
            TwistStamped, "/rover_controller/cmd_vel", self.cb, 10)
        self.pub = self.create_publisher(
            Float64MultiArray, "/velocity_controller/commands", 10)

    def cb(self, msg):
        v = msg.twist.linear.x
        w = msg.twist.angular.z
        vl = (v - w * self.L / 2.0) / self.r
        vr = (v + w * self.L / 2.0) / self.r
        out = Float64MultiArray()
        # order must match controller.yaml joints: [bl, fl, br, fr]
        out.data = [vl, vl, vr, vr]
        self.pub.publish(out)

    def main(args=None):
        rclpy.init(args=args)
        node = CmdVelToWheels()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()


    if __name__ == "__main__":
        main()