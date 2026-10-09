import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_file = os.path.join(os.path.dirname(pkg_dir), 'underbot_flat.urdf')
    rviz_file = os.path.join(pkg_dir, 'rviz', 'underbot.rviz')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_file]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        rviz2_node
    ])
