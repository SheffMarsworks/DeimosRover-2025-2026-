from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Launch arguments shared by ICP odometry and RTAB-Map SLAM.
    use_sim_time = LaunchConfiguration("use_sim_time")
    base_frame = LaunchConfiguration("base_frame")
    odom_frame = LaunchConfiguration("odom_frame")
    map_frame = LaunchConfiguration("map_frame")
    points_topic = LaunchConfiguration("points_topic")
    odom_topic = LaunchConfiguration("odom_topic")

    pkg_share = FindPackageShare("rover_bringup")
    rtabmap_yaml = PathJoinSubstitution([
    pkg_share,
    "config",
    "rtabmap_3d.yaml",
    ])

    icp_yaml = PathJoinSubstitution([
        pkg_share,
        "config",
        "icp_odometry.yaml",
    ])

    # LiDAR-based odometry using RTAB-Map ICP.
    icp_odometry = Node(
        package="rtabmap_odom",
        executable="icp_odometry",
        name="icp_odometry",
        output="screen",
        parameters=[
            icp_yaml,
            {
                "use_sim_time": use_sim_time,
                "frame_id": base_frame,
                "odom_frame_id": odom_frame,
            },
        ],
        remappings=[
            ("scan_cloud", points_topic),
            ("odom", odom_topic),
        ],
    )

    # RTAB-Map SLAM consumes /icp_odom by default instead of wheel odom.
    # It still uses /lidar/points for mapping.
    rtabmap = Node(
        package="rtabmap_slam",
        executable="rtabmap",
        name="rtabmap",
        output="screen",
        parameters=[
            rtabmap_yaml,
            {
                "use_sim_time": use_sim_time,
                "frame_id": base_frame,
                "odom_frame_id": odom_frame,
                "map_frame_id": map_frame,
            },
        ],
        remappings=[
            ("scan_cloud", points_topic),
            ("odom", odom_topic),
            ("grid_map", "/map"),
            ("cloud_map", "/cloud_map"),
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("base_frame", default_value="base_footprint"),
            DeclareLaunchArgument("odom_frame", default_value="odom"),
            DeclareLaunchArgument("map_frame", default_value="map"),
            DeclareLaunchArgument("points_topic", default_value="/lidar/points"),
            DeclareLaunchArgument("odom_topic", default_value="/icp_odom"),

            icp_odometry,
            rtabmap,
        ]
    )