from launch import LaunchDescription
from launch.actions import RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node


def generate_launch_description():

    # Joint State Broadcaster
    jsb = Node(
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

    start_rover_after_jsb = RegisterEventHandler(
        OnProcessExit(
            target_action=jsb,
            on_exit=[controller],
        )
    )

    return LaunchDescription(
        [
            jsb,
            start_rover_after_jsb,
        ]
    )
