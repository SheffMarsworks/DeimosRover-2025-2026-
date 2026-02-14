import os
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():

    # Controller spawner
    controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "rover_controller",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "120",
            "--switch-timeout", "120",
            ],
    )

    return LaunchDescription(
        [
            controller,
        ]
    )
