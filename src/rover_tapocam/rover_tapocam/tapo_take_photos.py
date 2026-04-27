#!/usr/bin/env python3
"""Capture one or more photos from a Tapo camera RTSP stream."""

import argparse
from datetime import datetime
import os
import time
from urllib.parse import quote

import cv2

try:
    from rover_tapocam.paths import default_output_dir_arg, resolve_image_dir
except ModuleNotFoundError:
    from paths import default_output_dir_arg, resolve_image_dir


def build_rtsp_url(host: str, user: str, password: str, port: int, stream: str) -> str:
    safe_user = quote(user, safe="")
    safe_password = quote(password, safe="")
    return f"rtsp://{safe_user}:{safe_password}@{host}:{port}/{stream}"


def read_frame(cap: cv2.VideoCapture, warmup_frames: int, retries: int = 5):
    for _ in range(max(0, warmup_frames)):
        cap.read()

    for _ in range(max(1, retries)):
        ok, frame = cap.read()
        if ok and frame is not None:
            return frame
        time.sleep(0.1)

    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Take photos from a Tapo camera RTSP stream.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default=os.getenv("TAPOCAM_HOST", "192.168.1.102"), help="Camera IP/hostname")
    parser.add_argument("--user", default=os.getenv("TAPOCAM_USER", ""), help="Tapo camera account username")
    parser.add_argument("--password", default=os.getenv("TAPOCAM_PASSWORD", ""), help="Tapo camera account password")
    parser.add_argument("--port", type=int, default=int(os.getenv("TAPOCAM_RTSP_PORT", "554")), help="RTSP port")
    parser.add_argument(
        "--stream",
        choices=["stream1", "stream2"],
        default=os.getenv("TAPOCAM_RTSP_STREAM", "stream1"),
        help="RTSP stream path (stream1=main, stream2=sub)",
    )
    parser.add_argument("--count", type=int, default=1, help="Number of photos to capture")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds to wait between photos when count > 1",
    )
    parser.add_argument(
        "--warmup-frames",
        type=int,
        default=5,
        help="Frames to skip before each capture to reduce stale buffer frames",
    )
    parser.add_argument(
        "--output-dir",
        default=default_output_dir_arg(),
        help="Directory where photos will be saved",
    )
    parser.add_argument("--prefix", default="tapo_photo", help="Output filename prefix")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.count < 1:
        raise ValueError("--count must be >= 1")
    if not args.user or not args.password:
        raise ValueError("Missing credentials. Set --user/--password or TAPOCAM_USER/TAPOCAM_PASSWORD.")

    output_dir = resolve_image_dir(args.output_dir)
    rtsp_url = build_rtsp_url(args.host, args.user, args.password, args.port, args.stream)
    print(f"Connecting to RTSP stream: {args.host}:{args.port}/{args.stream}")
    print(f"Saving images to: {output_dir}")

    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise RuntimeError("Could not open RTSP stream. Check host, credentials, and camera RTSP settings.")

    saved_files = []
    try:
        for index in range(args.count):
            frame = read_frame(cap, args.warmup_frames)
            if frame is None:
                raise RuntimeError(f"Failed to read frame for capture #{index + 1}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{args.prefix}_{timestamp}_{index + 1:03d}.jpg"
            destination = output_dir / filename

            if not cv2.imwrite(str(destination), frame):
                raise RuntimeError(f"Failed to write image to {destination}")

            saved_files.append(destination)
            print(f"Saved: {destination}")

            if index < args.count - 1:
                time.sleep(max(0.0, args.interval))
    finally:
        cap.release()

    print(f"Done. Captured {len(saved_files)} photo(s).")


if __name__ == "__main__":
    main()
