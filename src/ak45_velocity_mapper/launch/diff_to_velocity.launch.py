import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('ak45_velocity_mapper')
    config_file = os.path.join(pkg, 'config', 'diff_to_velocity.yaml')

    return LaunchDescription([
        Node(
            package='ak45_velocity_mapper',
            executable='diff_to_velocity',
            name='diff_to_velocity',
            parameters=[config_file],
            output='screen',
        ),
    ])
