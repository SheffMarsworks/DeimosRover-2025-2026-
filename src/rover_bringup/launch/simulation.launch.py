# rover_bringup/launch/simulation.launch.py

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    teleop_arg = DeclareLaunchArgument(
        "teleop",
        default_value="none",
        description="Teleop type: keyboard, joystick, none",
    )

    controller_manager_arg = DeclareLaunchArgument(
        "controller_manager",
        default_value="/controller_manager",
        description="controller_manager namespace/service root",
    )

    def launch_setup(context, *args, **kwargs):
        teleop = LaunchConfiguration("teleop").perform(context)
        controller_manager = LaunchConfiguration("controller_manager").perform(context)

        # 1) Gazebo + spawn robot (from rover_description)
        gazebo_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("rover_description"),
                    "launch",
                    "gazebo.launch.py",
                )
            )
        )

        # 2) Spawn rover_controller via controller_manager spawner
        # Equivalent to:
        # ros2 run controller_manager spawner rover_controller --controller-manager /controller_manager
        spawn_rover_controller = Node(
            package="controller_manager",
            executable="spawner",
            arguments=["rover_controller", "--controller-manager", controller_manager],
            output="screen",
        )

        actions = [gazebo_launch, spawn_rover_controller]

        # 3) Optional teleop
        if teleop == "keyboard":
            teleop_launch = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("rover_controller"),
                        "launch",
                        "keyboard_teleop.launch.py",
                    )
                )
            )
            actions.append(teleop_launch)

        elif teleop == "joystick":
            teleop_launch = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("rover_controller"),
                        "launch",
                        "joystick_teleop.launch.py",
                    )
                )
            )
            actions.append(teleop_launch)

        # else: teleop == "none" (do nothing)

        return actions

    return LaunchDescription(
        [
            teleop_arg,
            controller_manager_arg,
            OpaqueFunction(function=launch_setup),
        ]
    )
