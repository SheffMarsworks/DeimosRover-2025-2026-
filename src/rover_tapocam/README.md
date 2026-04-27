# rover_tapocam

Tapo camera control tools packaged for this ROS 2 workspace.

## Default image directory

Captured images now default to:

`/Users/yankikirlikova/Desktop/programming/rover/DeimosRover-2025-2026-/data/tapocam_images`

This can be overridden with `--output-dir` or with:

`DEIMOS_TAPOCAM_IMAGE_DIR=/some/path`

## Entry points

- `ros2 run rover_tapocam tapo_take_photos`
- `ros2 run rover_tapocam tapo_panoramic`
- `ros2 run rover_tapocam tapo_ptz_wasd`
- `ros2 run rover_tapocam tapo_cli`
- `ros2 run rover_tapocam tapo_onvif_test`
- `ros2 run rover_tapocam tapo_onvif_set_encoder`
- `ros2 run rover_tapocam tapo_onvif_dump_options`

## Credentials

Set camera credentials once per shell:

```bash
export TAPOCAM_USER="your_camera_user"
export TAPOCAM_PASSWORD="your_camera_password"
```

