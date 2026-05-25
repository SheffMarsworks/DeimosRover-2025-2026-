import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, TimerAction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def launch_setup(launch_context, *args, **kwargs):
    # Launch configs
    world_name = LaunchConfiguration("world").perform(launch_context)
    name = LaunchConfiguration("name").perform(launch_context)
    x = LaunchConfiguration("x").perform(launch_context)
    y = LaunchConfiguration("y").perform(launch_context)
    z = LaunchConfiguration("z").perform(launch_context)
    Y = LaunchConfiguration("Y").perform(launch_context)

    # Map world name to world file
    world_dict = {
        "empty": "empty.sdf",
        "mars": "mars.world.sdf",
        "warehouse": "warehouse.sdf",
        "warehouse2": "warehouse2.sdf",
        "industrial": "industrial_warehouse.sdf",
        "cave": "cave.sdf",
    }

    # Throw error if invalid world name
    if world_name not in world_dict:
        raise RuntimeError(
            f"Invalid world='{world_name}'. Valid: {list(world_dict.keys())}"
        )

    # Paths
    desc_pkg_path = FindPackageShare("rover_description").perform(launch_context)
    world_path = os.path.join(desc_pkg_path, "worlds", world_dict[world_name])
    xacro_path = os.path.join(desc_pkg_path, "urdf", "rover.urdf.xacro")

    # Xacro to URDF
    robot_description = ParameterValue(
        Command(["xacro ", xacro_path]),
        value_type=str,
    )

    # Gazebo
    gazebo = ExecuteProcess(
        cmd=["ign", "gazebo", "-r", world_path],
        output="screen",
    )

    # Robot State Publisher Node
    robot_state_publisher = Node(
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
            "-Y", Y,
        ],
        output="screen",
    )

    # Delay spawning until Gazebo has time to load the world
    spawn_robot = TimerAction(
        period=3.0,
        actions=[spawn_robot],
    )

    # Gazebo / ROS 2 bridge
    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # "/imu/data_raw@sensor_msgs/msg/Imu[gz.msgs.IMU",
            # "/camera/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image",
            # "/camera/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo",
            # "/depth_camera/points@sensor_msgs/msg/PointCloud2@ignition.msgs.PointCloudPacked",
            # "/depth_camera/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo",
            # "/depth_camera/image@sensor_msgs/msg/Image@ignition.msgs.Image",
            # "/depth_camera/depth_image@sensor_msgs/msg/Image@ignition.msgs.Image",
            "/lidar/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
        remappings=[
            ("/depth_camera/image", "/depth_camera/image_raw"),
        ],
        output="screen",
    )

    # # IMU filter
    # imu_filter = Node(
    #     package="imu_filter_madgwick",
    #     executable="imu_filter_madgwick_node",
    #     output="screen",
    #     parameters=[
    #         {
    #             "use_mag": False,
    #             "world_frame": "enu",
    #             "publish_tf": False,
    #             "use_sim_time": True,
    #         }
    #     ],
    # )

    return [
        gazebo,
        robot_state_publisher,
        spawn_robot,
        gz_ros2_bridge,
        # imu_filter,
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                name="world",
                default_value="empty",
                description="World shortcut: empty | mars | warehouse | industrial",
            ),
            DeclareLaunchArgument(
                name="name",
                default_value="rover",
                description="Entity name in Gazebo",
            ),
            DeclareLaunchArgument(
                name="x",
                default_value="0.0",
                description="Initial X position of the robot",
            ),
            DeclareLaunchArgument(
                name="y",
                default_value="0.0",
                description="Initial Y position of the robot",
            ),
            DeclareLaunchArgument(
                name="z",
                default_value="0.3",
                description="Initial Z position of the robot",
            ),
            DeclareLaunchArgument(
                name="Y",
                default_value="0.0",
                description="Initial yaw position of the robot",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )