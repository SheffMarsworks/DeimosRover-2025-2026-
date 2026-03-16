import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    revolute_14_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "Revolute_14_position_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    revolute_15_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "Revolute_15_position_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    revolute_16_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "Revolute_16_position_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    revolute_17_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "Revolute_17_position_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    revolute_18_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "Revolute_18_position_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    revolute_19_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "Revolute_19_position_controller",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    return LaunchDescription(
        [
            joint_state_broadcaster_spawner,
            revolute_14_controller,
            revolute_15_controller,
            revolute_16_controller,
            revolute_17_controller,
            revolute_18_controller,
            revolute_19_controller,
        ]
    )