#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[mars_ws] Bringing up can0..."
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up

echo "[mars_ws] Sourcing ROS 2..."
source /opt/ros/humble/setup.bash
source "$SCRIPT_DIR/install/setup.bash"

echo "[mars_ws] Launching ak45..."
ros2 launch marsworks_ak45 ak45.launch.py

# Cleanup
sudo ip link set can0 down