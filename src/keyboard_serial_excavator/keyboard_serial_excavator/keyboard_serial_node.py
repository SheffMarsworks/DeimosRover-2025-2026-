#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import serial
import sys
import threading
import time

class KeyboardSerialNode(Node):
    def __init__(self):
        super().__init__('keyboard_serial_node')
        
        # Declare parameters
        self.declare_parameter('port', '/dev/ttyTHS1')
        self.declare_parameter('baudrate', 115200)
        
        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value
        
        # Open serial connection (same as your working code)
        try:
            self.serial_port = serial.Serial(port, baudrate)
            self.get_logger().info(f"✓ Connected to {port} at {baudrate} baud")
        except Exception as e:
            self.get_logger().error(f"✗ Failed to open {port}: {e}")
            sys.exit(1)
        
        # Key to command mapping
        self.key_commands = {
            '1': '14',
            '2': '15',
            '3': '16',
            '4': '17',
            '5': '18',
            '6': '19',

        }
        
        self.get_logger().info("Press 1 - 6 to send command")
        
        # Start keyboard thread
        self.running = True
        self.keyboard_thread = threading.Thread(target=self.listen_keyboard, daemon=True)
        self.keyboard_thread.start()
        
        # Timer to keep node alive
        self.timer = self.create_timer(1.0, self.timer_callback)
    
    def timer_callback(self):
        """Keep the node spinning"""
        pass
    
    def listen_keyboard(self):
        """Listen for keyboard input"""
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(fd)
            while self.running:
                ch = sys.stdin.read(1)
                if ch:
                    self.handle_key(ch)
        except Exception as e:
            self.get_logger().error(f"Keyboard error: {e}")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def handle_key(self, key):
        """Handle key press"""
        if key == 'q':
            self.running = False
            return
        
        if key in self.key_commands:
            command = self.key_commands[key]
            self.send_to_serial(command)
    
    def send_to_serial(self, command):
        """Send directly to serial (same as your working code)"""
        try:
            message = f"{command}\n".encode()
            self.get_logger().info(f"Writing: {repr(message)}")
            self.serial_port.write(message)
            self.get_logger().info(f"✓ Sent successfully")
        except Exception as e:
            self.get_logger().error(f"✗ Write failed: {e}")
    
    def destroy_node(self):
        self.running = False
        if self.serial_port.is_open:
            self.serial_port.close()
        super().destroy_node()
    def cleanup(self):
        self.running = False
        if self.serial_port.is_open:
            self.serial_port.close()
            self.get_logger().info("Serial port close")


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardSerialNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cleanup()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
