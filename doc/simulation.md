# Simulation Guide

This guide walks through the main ways to run and test the Deimos rover simulation.

The project uses **ROS 2 Humble**, **Ubuntu 22.04**, and **Ignition Gazebo Fortress**.  
Use the `ign` command for Gazebo Fortress, not `gz`.

## Source the workspace

Before running any launch file, source ROS 2 and the workspace:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

If the workspace has not been built yet:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Quick Start

```bash
# Keyboard teleop
ros2 launch rover_bringup simulation.launch.py mode:=teleop teleop:=keyboard world:=warehouse

# SLAM
ros2 launch rover_bringup simulation.launch.py mode:=slam teleop:=keyboard world:=warehouse

# Launch in a specific world and spawn pose

ros2 launch rover_bringup simulation.launch.py \
  mode:=slam \
  teleop:=keyboard \
  world:=cave \
  x:=1.6 \
  y:=-9.0 \
  z:=0.25 \
  Y:=1.5708
```

## Project package layout

The simulation is split across four packages:

- `rover_description` uses **ament CMake** and contains the URDF/Xacro files, meshes, RViz configs, Gazebo worlds, and simulation models.

- `rover_controller` uses **ament Python** and contains controller, keyboard teleop, and joystick teleop launch/config files.

- `rover_slam` uses **ament Python** and contains the RTAB-Map SLAM launch/config files.

- `rover_bringup` uses **ament Python** and contains the main simulation launch file that combines the other packages.

For the Python packages, launch files and config files are installed through each package's `setup.py`.  

For `rover_description`, install paths and shared resource paths are handled through CMake and environment hooks.

## Visualize the robot in RViz

Use this first to check that the robot model, joints, meshes, and TF tree load correctly.

```bash
ros2 launch rover_description rviz_demo.launch.py
```

This launch file starts:

- `robot_state_publisher`
- `joint_state_publisher_gui`
- RViz with the rover display configuration

This is useful when editing the URDF/Xacro files because it lets you test the robot model without launching Gazebo.

## Open a world directly in Gazebo

To open the Mars world without spawning the rover:

```bash
ign gazebo -r $(ros2 pkg prefix rover_description)/share/rover_description/worlds/mars.world.sdf
```

This is useful for checking that a world file loads correctly before running the full simulation.

## Run the basic simulation

The main simulation launch file is:

```bash
ros2 launch rover_bringup simulation.launch.py
```

By default, this launches the Gazebo simulation, spawns the rover, starts the controller, and opens RViz.

Teleoperation is **not** started by default. To drive the rover, launch the simulation with `mode:=teleop`, as shown in the next section.

### Worlds

You can select a world using the `world` argument:

```bash
# Warehouse world
ros2 launch rover_bringup simulation.launch.py world:=warehouse

# Mars world
ros2 launch rover_bringup simulation.launch.py world:=mars
```

Available project world shortcuts include:

```text
empty
mars
warehouse
warehouse2
industrial
cave
```

### Launch Arguments

| Argument | Default | Description |
|---|---:|---|
| `mode` | `none` | System mode: `none`, `teleop`, `slam`, `nav` |
| `teleop` | `keyboard` | Teleoperation type: `keyboard` or `joystick` |
| `world` | `warehouse` | Simulation world shortcut |
| `name` | `rover` | Robot entity name in Ignition |
| `x` | `0.0` | Initial robot X position |
| `y` | `0.0` | Initial robot Y position |
| `z` | `0.25` | Initial robot Z position |
| `Y` | `0.0` | Initial robot yaw angle in radians |

## Run teleoperation

Teleoperation is started through the same main simulation launch file.

The default teleop method is keyboard. To use joystick teleop, add the `teleop:=joystick` argument.


```bash
# Start teleop with keyboard
ros2 launch rover_bringup simulation.launch.py mode:=teleop

# Start teleop with joystick
ros2 launch rover_bringup simulation.launch.py mode:=teleop teleop:=joystick
```

The rover controller receives velocity commands on:

```text
/rover_controller/cmd_vel
```

Keyboard teleop publishes to `/cmd_vel`, then `twist_stamper` converts it to the stamped velocity command used by the rover controller.

## Run SLAM

SLAM mode starts the simulation, rover controller, RViz, ICP odometry, and RTAB-Map.


```bash
# Start SLAM in the warehouse world
ros2 launch rover_bringup simulation.launch.py world:=warehouse mode:=slam

# Start SLAM in the warehouse2 world with a custom spawn pose
ros2 launch rover_bringup simulation.launch.py world:=warehouse2 mode:=slam Y:=1.5708 x:=3 y:=-23

# Start SLAM in the industrial world with a custom spawn pose
ros2 launch rover_bringup simulation.launch.py world:=industrial mode:=slam Y:=1.5708 x:=1.6 y:=-9
```

## Open worlds from the Gazebo public library

You can open public Gazebo Fuel worlds directly with `ign gazebo`.

```bash
# Industrial warehouse world
ign gazebo "https://fuel.gazebosim.org/1.0/openrobotics/worlds/industrial-warehouse"

# Cave world
ign gazebo "https://fuel.gazebosim.org/1.0/openrobotics/worlds/cave world"
```

This is useful for testing a public world before copying or adapting it into the project.

## Download worlds from Gazebo Fuel

Worlds opened directly from the Gazebo Fuel library are downloaded and cached locally. To pre-download a world for offline use, use the `ign fuel download` command.


```bash
# Download the industrial warehouse world
ign fuel download -t world -u "https://fuel.gazebosim.org/1.0/openrobotics/worlds/industrial-warehouse"
```

Downloaded worlds are saved under

```text
~/.ignition/fuel/fuel.gazebosim.org/openrobotics/worlds/
```

To inspect downloaded worlds in the terminal:

```bash
tree ~/.ignition/fuel/fuel.gazebosim.org/openrobotics/worlds
```

The worlds can also be opened in a file explorer by

```bash
# Linux
xdg-open ~/.ignition/fuel/fuel.gazebosim.org/openrobotics/worlds

# WSL
explorer.exe "$(wslpath -w ~/.ignition/fuel/fuel.gazebosim.org/openrobotics/worlds)"
```

## Troubleshooting

### World/Launch file not found

Rebuild the workspace

```bash
colcon clean workspace -y && colcon build --symlink-install && . install/setup.bash
```

### Ignition does not start

Make sure Ignition Fortress is installed.  

For this project, use `ign gazebo` not `gz sim` to launch Gazebo Fortress.

```bash
ign gazebo --version
```
### Robot does not move

Check that the controllers are active

```bash
ros2 control list_controllers
```

### Missing transforms

Check TF tree

```bash
ros2 run tf2_tools view_frames
```

### World does not load

If a world shortcut is invalid, check the shortcut mapping in:

```text
src/rover_description/launch/gazebo.launch.py
```

The supported shortcut names are defined in `world_dict`:

```python
world_dict = {
    "empty": "empty.sdf",
    "mars": "mars.world.sdf",
    "warehouse": "warehouse.sdf",
    "warehouse2": "warehouse2.sdf",
    "industrial": "industrial_warehouse.sdf",
    "cave": "cave.sdf",
}
```


