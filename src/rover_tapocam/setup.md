# TapoCam Setup (Ubuntu)

This guide is for testing `rover_tapocam` on a different Ubuntu computer.

## 1) Install system dependencies

```bash
sudo apt update
sudo apt install -y \
  git python3-pip python3-colcon-common-extensions python3-rosdep \
  ros-humble-desktop ros-humble-xacro \
  python3-opencv python3-onvif-zeep
```

## 2) Initialize rosdep (once per machine)

```bash
sudo rosdep init
rosdep update
```

## 3) Clone and build the workspace

```bash
mkdir -p ~/code && cd ~/code
git clone https://github.com/SheffMarsworks/DeimosRover-2025-2026-.git
cd DeimosRover-2025-2026-

# Python dependency for tapo_cli
pip install pytapo

# Install remaining ROS dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 4) Configure camera in the Tapo app

1. Enable `Camera Account` and create username/password.
2. Enable `RTSP`.
3. Enable `ONVIF`.

## 5) Export camera environment variables

```bash
export TAPOCAM_HOST="192.168.1.102"
export TAPOCAM_USER="your_camera_user"
export TAPOCAM_PASSWORD="your_camera_password"
```

## 6) Run tests

```bash
# Basic API/auth test
ros2 run rover_tapocam tapo_cli info

# ONVIF connectivity test (no movement)
ros2 run rover_tapocam tapo_onvif_test --move-seconds 0

# Capture one photo
ros2 run rover_tapocam tapo_take_photos --count 1

# Panorama capture
ros2 run rover_tapocam tapo_panoramic --start-from-home --return-home

# Manual PTZ keyboard control
ros2 run rover_tapocam tapo_ptz_wasd
```

## 7) Check saved images

```bash
ls -la ~/code/DeimosRover-2025-2026-/data/tapocam_images
```

## Notes

- Default image output directory is `data/tapocam_images` in the repo.
- Override image path with:

```bash
export DEIMOS_TAPOCAM_IMAGE_DIR="/custom/path"
```

- If `ros2: command not found`, source ROS first:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

- For Ubuntu 24.04 (ROS 2 Jazzy), package names differ; update apt package names accordingly.
