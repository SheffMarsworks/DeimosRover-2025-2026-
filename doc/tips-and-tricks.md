# Tips and Tricks

This page contains small workflow tips that make working with the Deimos rover ROS 2 workspace easier.

## Use `.` instead of `source`

In Bash, `.` is a shorter form of `source`.

For example, these two commands do the same thing:

```bash
source install/setup.bash
```

```bash
. install/setup.bash
```

This can be useful when you source the workspace often.

## Clean the workspace safely

Instead of manually deleting build folders with:

```bash
rm -rf build install log
```

use:

```bash
colcon clean workspace -y
```

This is safer and cleaner because it lets `colcon` handle the workspace cleanup.

If the command is not available, install the clean extension:

```bash
sudo apt install python3-colcon-clean
```

## Enable `colcon` autocomplete

To make `colcon` commands easier to type, enable autocomplete:

```bash
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
```

After this, pressing `Tab` can autocomplete `colcon` commands, package names, and arguments.

## Why use `--symlink-install`?

When building the workspace, use:

```bash
colcon build --symlink-install
```

The `--symlink-install` option creates symbolic links instead of copying files into the `install` directory.

This is useful during development because changes to files such as launch files, Python scripts, RViz configs, and some resource files can be reflected without needing a full rebuild every time.

A normal rebuild is still needed after changing package setup files, dependencies, CMake files, or compiled code.

## Automatic setup in `.bashrc`

To avoid sourcing everything manually every time you open a new terminal, you can add the following lines to your `~/.bashrc`.

Replace `~/path_to_project/DeimosRover-2025-2026-` with the real path to your workspace.

```bash
# Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# Enable colcon autocomplete
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash

# Source Deimos rover workspace
cd ~/path_to_project/DeimosRover-2025-2026-
source install/setup.bash
```

After editing `~/.bashrc`, reload it with:

```bash
source ~/.bashrc
```

or open a new terminal.

## Optional shorter version

If you prefer the shorter `.` form:

```bash
# Source ROS 2 Humble
. /opt/ros/humble/setup.bash

# Enable colcon autocomplete
. /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash

# Source Deimos rover workspace
cd ~/path_to_project/DeimosRover-2025-2026-
. install/setup.bash
```

## Note about changing directory in `.bashrc`

Adding `cd ~/path_to_project/DeimosRover-2025-2026-` means every new terminal will automatically open inside the project workspace.

If you do not want this behaviour, remove the `cd` line and use the full path instead:

```bash
source ~/path_to_project/DeimosRover-2025-2026-/install/setup.bash
```
