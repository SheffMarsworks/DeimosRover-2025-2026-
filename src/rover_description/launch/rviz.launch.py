from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    use_gui = LaunchConfiguration("gui")

    pkg_share = FindPackageShare("rover_description")
    xacro_file = PathJoinSubstitution([pkg_share, "urdf", "rover.urdf.xacro"])
    rviz_config = PathJoinSubstitution([pkg_share, "rviz", "display.rviz"])

    robot_description = ParameterValue(
        Command(["xacro ", xacro_file]),
        value_type=str
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    joint_state_publisher = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        condition=IfCondition(use_gui),
        output="screen",
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        output="screen",
    )

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true"),
        robot_state_publisher,
        joint_state_publisher,
        rviz,
    ])
