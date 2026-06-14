# ak45_velocity_mapper

This ROS 2 package converts manual diff-drive commands into four CubeMars motor velocity commands.

## Topics

Subscribes:

```bash
/diff_drive_controller/cmd_vel    # geometry_msgs/msg/Twist
```

Publishes:

```bash
/velocity_controller/commands     # std_msgs/msg/Float64MultiArray
```

Output order:

```text
[motor_1, motor_2, motor_3, motor_4]
```

Default wheel grouping:

```text
left side  = motor_1, motor_3
right side = motor_2, motor_4
```

## Formula

```text
left  = (linear_x - angular_z * wheel_separation / 2) / wheel_radius
right = (linear_x + angular_z * wheel_separation / 2) / wheel_radius

commands = [left, right, left, right] * motor_signs
```

The default `motor_signs` are `[1.0, -1.0, 1.0, 1.0]` because your manual forward test used:

```bash
ros2 topic pub /velocity_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, -0.5, 0.5, 0.5]}" --once
```

If a motor spins in the wrong direction, edit `config/diff_to_velocity.yaml` and flip that motor sign.

## Build

From the workspace root:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Run only this mapper

```bash
ros2 launch ak45_velocity_mapper diff_to_velocity.launch.py
```

## Test

Make sure `velocity_controller` is active, then run:

```bash
ros2 topic pub /diff_drive_controller/cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.05}, angular: {z: 0.0}}" --once
```

The mapper will publish to `/velocity_controller/commands`. It automatically publishes zero if no command is received for `cmd_timeout` seconds.
