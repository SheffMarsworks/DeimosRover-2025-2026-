import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("rover_navigation")
    default_params = os.path.join(pkg_share, "config", "nav2_params.yaml")

    use_sim_time = LaunchConfiguration("use_sim_time")
    params_file = LaunchConfiguration("params_file")
    autostart = LaunchConfiguration("autostart")

    declare_args = [
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("params_file", default_value=default_params),
        DeclareLaunchArgument("autostart", default_value="true"),
    ]

    # Lifecycle nodes managed by lifecycle_manager_navigation.
    # NOTE: no map_server and no amcl - RTAB-Map publishes /map and map->odom.
    lifecycle_nodes = [
        "controller_server",
        "planner_server",
        "behavior_server",
        "bt_navigator",
        "waypoint_follower",
    ]

    common = [params_file, {"use_sim_time": use_sim_time}]

    controller_server = Node(
        package="nav2_controller",
        executable="controller_server",
        name="controller_server",
        output="screen",
        parameters=common,
        # controller_server publishes geometry_msgs/Twist on /cmd_vel
        remappings=[("cmd_vel", "/cmd_vel")],
    )

    planner_server = Node(
        package="nav2_planner",
        executable="planner_server",
        name="planner_server",
        output="screen",
        parameters=common,
    )

    behavior_server = Node(
        package="nav2_behaviors",
        executable="behavior_server",
        name="behavior_server",
        output="screen",
        parameters=common,
        remappings=[("cmd_vel", "/cmd_vel")],
    )

    bt_navigator = Node(
        package="nav2_bt_navigator",
        executable="bt_navigator",
        name="bt_navigator",
        output="screen",
        parameters=common,
    )

    waypoint_follower = Node(
        package="nav2_waypoint_follower",
        executable="waypoint_follower",
        name="waypoint_follower",
        output="screen",
        parameters=common,
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"autostart": autostart},
            {"node_names": lifecycle_nodes},
        ],
    )

    # Bridge: Nav2 Twist on /cmd_vel -> TwistStamped on /rover_controller/cmd_vel
    # (diff_drive_controller has use_stamped_vel: true). Same pattern as teleop.
    twist_stamper = Node(
        package="twist_stamper",
        executable="twist_stamper",
        name="nav2_twist_stamper",
        output="screen",
        parameters=[{"frame_id": "base_link", "use_sim_time": use_sim_time}],
        remappings=[
            ("cmd_vel_in", "/cmd_vel"),
            ("cmd_vel_out", "/rover_controller/cmd_vel"),
        ],
    )

    return LaunchDescription(
        declare_args
        + [
            controller_server,
            planner_server,
            behavior_server,
            bt_navigator,
            waypoint_follower,
            lifecycle_manager,
            twist_stamper,
        ]
    )
