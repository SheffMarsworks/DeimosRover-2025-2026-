import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    pkg = get_package_share_directory("marsworks_ak45")
    xacro_file = os.path.join(pkg, "urdf", "ak45.urdf.xacro")
    robot_description = xacro.process_file(xacro_file).toxml()
    controllers_yaml = os.path.join(pkg, "config", "controllers.yaml")

    return LaunchDescription([
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[
                {"robot_description": robot_description},
                controllers_yaml,
            ],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster"],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["velocity_controller"],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_trajectory_controller", "--inactive"],
            output="screen",
        ),
        '''Node(
            package="controller_manager",
            executable="spawner",
            arguments=["diff_drive_controller"],
            output="screen",
        ),'''
    ])