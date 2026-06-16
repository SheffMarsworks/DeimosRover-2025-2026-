from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # Joint State Broadcaster
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "120",
            "--switch-timeout", "120",
        ],
        output="screen",
    )

    cmd_vel_to_wheels = Node(
        package="rover_controller",
        executable="cmd_vel_to_wheels",
        name="cmd_vel_to_wheels",
        output="screen",
    )

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
            output="screen",
    )

    return LaunchDescription(
        [
            joint_state_broadcaster,
            controller,
            cmd_vel_to_wheels,
        ]
    )
