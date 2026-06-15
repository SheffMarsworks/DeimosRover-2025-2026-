import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def launch_setup(context, *args, **kwargs):
    mode = LaunchConfiguration("mode").perform(context)
    teleop = LaunchConfiguration("teleop").perform(context)

    actions = []

    # Controller
    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("rover_controller"),
                    "launch",
                    "controller.launch.py",
                )
            ),
            launch_arguments={"use_sim_time": "false"}.items(),
        )
    )

    # RViz
    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("rover_description"),
                    "launch",
                    "rviz.launch.py",
                )
            ),
            launch_arguments={
                "use_sim_time": "false",
                "mode": mode,
                }.items(),
        )
    )

    # SLAM in slam OR nav (nav needs RTAB-Map for map and map->odom TF)
    if mode in ["slam", "nav"]:
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("rover_slam"),
                        "launch",
                        "rtab.real.launch.py",
                    )
                )
            )
        )

    # Nav2 in nav
    if mode == "nav":
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("rover_navigation"),
                        "launch",
                        "nav2.launch.py",
                    )
                ),
                launch_arguments={"use_sim_time": "true"}.items(),
            )
        )

    # Teleop in teleop OR slam
    if mode in ["teleop", "slam", "nav"]:
        teleop_map = {
            "keyboard": "keyboard_teleop.launch.py",
            "joystick": "joystick_teleop.launch.py",
        }
        teleop_file = teleop_map.get(teleop)

        if teleop_file:
            actions.append(
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(
                            get_package_share_directory("rover_controller"),
                            "launch",
                            teleop_file,
                        )
                    )
                )
            )

    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "teleop",
                default_value="keyboard",
                description="Teleop type: keyboard, joystick",
            ),
            DeclareLaunchArgument(
                "mode",
                default_value="none",
                description="Mode: none | teleop | slam | nav",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )