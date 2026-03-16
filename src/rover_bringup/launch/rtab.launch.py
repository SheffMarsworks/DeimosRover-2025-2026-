from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    pkg_share = FindPackageShare("rover_bringup")
    rtabmap_yaml = PathJoinSubstitution([pkg_share, "config", "rtabmap_3d.yaml"])

    rtabmap = Node(
        package="rtabmap_slam",
        executable="rtabmap",
        name="rtabmap",
        output="screen",
        parameters=[rtabmap_yaml],
        remappings=[
            ("scan_cloud", LaunchConfiguration("points_topic")),
            ("odom", LaunchConfiguration("odom_topic")),
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("base_frame", default_value="base_footprint"),
            DeclareLaunchArgument("odom_frame", default_value="odom"),
            DeclareLaunchArgument("map_frame", default_value="map"),

            DeclareLaunchArgument("points_topic", default_value="/lidar/points"),
            DeclareLaunchArgument("odom_topic", default_value="/rover_controller/odom"),
            rtabmap,
        ]
    )