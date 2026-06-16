#!/bin/bash

DEVICE=/dev/video0
DEVICE_INDEX=0

if [ ! -e "$DEVICE" ]; then
    echo "DFK 33UR0521 camera not found at $DEVICE"
    echo "Run: v4l2-ctl --list-devices to check connected cameras"
    exit 1
fi

echo "DFK 33UR0521 found at $DEVICE"
echo "Sourcing ROS2..."
source /opt/ros/$ROS_DISTRO/setup.bash

echo "Launching CameraRover publisher (Terminal 1)..."
gnome-terminal -- bash -c "
    source /opt/ros/\$ROS_DISTRO/setup.bash
    echo 'Starting CameraRover publisher on $DEVICE...'
    python3 CameraRover.py --ros-args -p device_index:=$DEVICE_INDEX
    exec bash
" &

sleep 1

echo "Launching Camera viewer (Terminal 2)..."
gnome-terminal -- bash -c "
    source /opt/ros/\$ROS_DISTRO/setup.bash
    echo 'Starting Camera viewer...'
    python3 Camera_viwer.py
    exec bash
" &

echo "Both terminals launched."
