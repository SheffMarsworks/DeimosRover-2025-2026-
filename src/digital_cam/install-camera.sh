#!/bin/bash

set -e

echo "Updating package lists..."
sudo apt update

echo "Installing camera tools..."
sudo apt install -y \
    v4l-utils \
    ffmpeg \
    guvcview \
    cheese \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad

sudo apt update
sudo apt install guvcview -y
sudo apt install ros-$ROS_DISTRO-cv-bridge ros-$ROS_DISTRO-image-transport -y
pip install opencv-python --break-system-packages

echo
echo "Installation complete."
echo
echo "Verify camera detection with:"
echo "  lsusb"
echo "  v4l2-ctl --list-devices"
