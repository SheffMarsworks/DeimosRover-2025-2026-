import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    # Launch configs
    world_name = LaunchConfiguration("world").perform(context)
    name = LaunchConfiguration("name").perform(context)
    x = LaunchConfiguration("x").perform(context)
    y = LaunchConfiguration("y").perform(context)
    z = LaunchConfiguration("z").perform(context)

    # Map world name to world file
    world_dict = {
        "empty": "empty.sdf",
        "mars": "mars.world.sdf",
        "warehouse": "warehouse.sdf",
    }

    # Throw error if invalid world name
    if world_name not in world_dict:
        raise RuntimeError(
            f"Invalid world='{world_name}'. Valid: {list(world_dict.keys())}"
        )
    
    # Paths
    desc_share = FindPackageShare("rover_description").perform(context)
    world_path = os.path.join(desc_share, "worlds", world_dict[world_name])
    xacro_path = os.path.join(desc_share, "urdf", "rover.urdf.xacro")

    # Xacro to URDF
    robot_description = Command(["xacro ", xacro_path])

    # Start Gazebo
    gazebo = ExecuteProcess(
        cmd=["ign", "gazebo", "-r", world_path],
        output="screen",
    )

    # Robot State Publisher Node
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {"robot_description": robot_description},
            {"use_sim_time": True},
        ],
        output="screen",
    )

    # Spawn Robot Node
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-name", name,
            "-x", x,
            "-y", y,
            "-z", z,
        ],
        output="screen",
    )

    # Spawn robot after Gazebo starts
    spawn_trigger = RegisterEventHandler(
        OnProcessStart(
            target_action=gazebo,
            on_start=[spawn_robot],
        )
    )

    return [
        gazebo,
        rsp,
        spawn_trigger
        ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            name = "world",
            default_value="empty",
            description="World shortcut: empty | mars | warehouse",
        ),
        DeclareLaunchArgument(
            name = "name",
            default_value="rover",
            description="Entity name in Gazebo",
        ),
        DeclareLaunchArgument(
            name = "x",
            default_value="0.0",
            description="Initial X position of the robot",
        ),
        DeclareLaunchArgument(
            name = "y",
            default_value="0.0",
            description="Initial Y position of the robot",
        ),
        DeclareLaunchArgument(
            name = "z",
            default_value="0.3",
            description="Initial Z position of the robot",
        ),
        OpaqueFunction(function=launch_setup),
    ])
