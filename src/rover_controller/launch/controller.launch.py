import os
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():

    # # Joint state broadcaster
    # joint_state_broadcaster = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=[
    #         "joint_state_broadcaster",
    #         "--controller-manager", "/controller_manager",
    #     ],
    # )

    # Controller spawner
    controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "rover_controller",
            "--controller-manager", "/controller_manager",
            ],
    )

    return LaunchDescription(
        [
            # joint_state_broadcaster,
            controller,
        ]
    )
