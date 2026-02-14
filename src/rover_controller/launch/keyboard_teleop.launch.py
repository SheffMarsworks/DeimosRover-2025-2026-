from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="true", description="Use simulation time if true"
    )

    # Keyboard teleop node
    teleop = Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        name="teleop_twist_keyboard",
        output="screen",
        # WSL
        prefix="xterm -e",
        # Dualboot
        # prefix="gnome-terminal -- bash -c",
        parameters=[
            {"use_sim_time": LaunchConfiguration("use_sim_time")},
        ],
    )

    # Twist stamper node
    stamper = Node(
        package="twist_stamper",
        executable="twist_stamper",
        name="twist_stamper",
        remappings=[
            ("cmd_vel_in", "/cmd_vel"),
            ("cmd_vel_out", "/rover_controller/cmd_vel"),
        ],
        parameters=[{"frame_id": "base_link"}],
    )

    return LaunchDescription(
        [
            sim_time,
            teleop,
            stamper,
        ]
    )