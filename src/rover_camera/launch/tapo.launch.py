from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([
        Node(
            package='rover_camera',
            executable='tapo_node',
            name='front_camera',
            output='screen',
            parameters=[{
                'rtsp_url': 'rtsp://USERNAME:PASSWORD@192.168.0.100:554/stream1'
            }]
        )
    ])