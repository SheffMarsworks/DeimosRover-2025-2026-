from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def configure_rviz(context):

    mode = LaunchConfiguration("mode").perform(context)
    use_sim_time = LaunchConfiguration("use_sim_time")

    pkg_share = FindPackageShare("rover_description")

    mode_to_rviz = {
        "teleop": "display.rviz",
        "slam": "slam.rviz",
        "nav": "nav.rviz",
    }

    rviz_file = mode_to_rviz.get(mode, "display.rviz")

    rviz_config = PathJoinSubstitution([pkg_share, "rviz", rviz_file])

    return [
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            parameters=[{"use_sim_time": use_sim_time}],
            output="screen",
        )
    ]


def generate_launch_description():

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="teleop"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        OpaqueFunction(function=configure_rviz),
    ])