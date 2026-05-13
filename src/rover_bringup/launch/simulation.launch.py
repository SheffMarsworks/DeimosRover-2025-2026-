import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def launch_setup(context, *args, **kwargs):
    mode = LaunchConfiguration("mode").perform(context)
    teleop = LaunchConfiguration("teleop").perform(context)
    world = LaunchConfiguration("world").perform(context)
    name = LaunchConfiguration("name").perform(context)
    x = LaunchConfiguration("x").perform(context)
    y = LaunchConfiguration("y").perform(context)
    z = LaunchConfiguration("z").perform(context)
    Y = LaunchConfiguration("Y").perform(context)

    actions = []

    # Gazebo + spawn robot
    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("rover_description"),
                    "launch",
                    "gazebo.launch.py",
                )
            ),
            launch_arguments={
                "world": world,
                "name": name,
                "x": x,
                "y": y,
                "z": z,
                "Y": Y,
            }.items(),
        )
    )

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
            launch_arguments={"use_sim_time": "true"}.items(),
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
                "use_sim_time": "true",
                "mode": mode,
                }.items(),
        )
    )

    # SLAM only in slam
    if mode == "slam":
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("rover_bringup"),
                        "launch",
                        "rtab.launch.py",
                    )
                )
            )
        )

    # Teleop in teleop OR slam
    if mode in ["teleop", "slam"]:
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
            DeclareLaunchArgument(
                "world",
                default_value="warehouse",
                description="World shortcut: empty | mars | warehouse | industrial",
            ),
            DeclareLaunchArgument("name", default_value="rover"),
            DeclareLaunchArgument("x", default_value="0.0"),
            DeclareLaunchArgument("y", default_value="0.0"),
            DeclareLaunchArgument("z", default_value="0.25"),
            DeclareLaunchArgument("Y", default_value="0.0"),
            OpaqueFunction(function=launch_setup),
        ]
    )