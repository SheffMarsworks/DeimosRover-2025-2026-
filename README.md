# Project Marsworks: Deimos Mars Rover
[![Static Badge](https://img.shields.io/badge/Ridwaan%20Joomun-orange?label=Software%20Lead&link=https%3A%2F%2Fgithub.com%2FRidwaan279)](https://github.com/Ridwaan279)

This ROS 2 workspace provides simulation, teleoperation, SLAM, and navigation support for MarsWorks' Deimos rover. The project is developed for rover competitions including the [Anatolian Rover Challenge (ARC) 2026](https://www.anatolianrover.space/), [European Rover Challenge (ERC) 2026](https://roverchallenge.eu/) and the [UK Lunabotics 2026](https://uklunabotics.co.uk/).

## Main Components

## Main Components

- **Rover Description**  
  Rover URDF/Xacro model, meshes, sensors, Gazebo worlds, and RViz configurations.

- **Rover Controller**  
  `ros2_control` configuration, differential-drive controller, keyboard teleop, and joystick teleop.

- **Rover SLAM**  
  RTAB-Map SLAM launch files and configuration, including ICP odometry and 3D LiDAR-based mapping.

- **Rover Bringup**  
  High-level launch files that combine the description, controller, SLAM, teleoperation, RViz, and Gazebo simulation.

### Prerequisites

- Ubuntu 22.04 Jammy Jellyfish

- [ROS 2 Humble](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)

- [Gazebo Fortress](https://gazebosim.org/docs/fortress/install_ubuntu/)

## Installation

```bash
# 1. Clone the repository:

git clone https://github.com/SheffMarsworks/DeimosRover-2025-2026-.git
cd DeimosRover-2025-2026-

# 2. Source ROS 2
source /opt/ros/humble/setup.bash
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash

# Install dependencies
rosdep update
rosdep install

# 3. Build the workspace

colcon build --symlink-install

# 4. Source the workspace
source install/setup.bash
```

<details>
<summary>Full Dependency Installation Command</summary>

```bash
sudo apt install -y python3-colcon-clean ros-humble-xacro ros-humble-joint-state-publisher-gui ros-humble-ros-gz ros-humble-ros-gz-bridge ros-humble-ros-gz-sim ros-humble-ros-gz-interfaces ros-humble-ign-ros2-control ros-humble-twist-stamper ros-humble-imu-tools ros-humble-ros2controlcli ros-humble-controller-manager ros-humble-ros2-controllers ros-humble-joy-teleop ros-humble-joy ros-humble-rtabmap-ros

```

</details>

## Documentation

- [Simulation Guide](doc/simulation.md)
- [Tips and Tricks](doc/tips-and-tricks.md)

## Acknowledgments

- [Project Marsworks Software Team](https://marsworks.sites.sheffield.ac.uk/team#h.4kuzgvqqcu52).
- [@Jan](https://github.com/JanUniAccount) for providing the [original Mars rover simulation URDF](https://github.com/JanUniAccount/mars_rover_pkg) in ROS1.
- [@Renzo Damian](https://github.com/renzodamgo) the 2024–2025 MarsWorks Software Team Lead, for providing last year’s framework, [Scarab Rover](https://github.com/SheffMarsworks/ScarabRover?tab=readme-ov-file), which served as the foundation for our current system.

## Contributors 
<a href="https://github.com/SheffMarsworks/DeimosRover-2025-2026-/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=SheffMarsworks/DeimosRover-2025-2026-"/>
</a>

