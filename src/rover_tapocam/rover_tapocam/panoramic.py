#!/usr/bin/env python3
"""Capture two camera views with PTZ pan movement and stitch them side-by-side."""

import argparse
from datetime import datetime
import os
import time
from urllib.parse import quote

import cv2
from onvif import ONVIFCamera

try:
    from rover_tapocam.paths import default_output_dir_arg, resolve_image_dir
except ModuleNotFoundError:
    from paths import default_output_dir_arg, resolve_image_dir


def build_rtsp_url(host: str, user: str, password: str, port: int, stream: str) -> str:
    safe_user = quote(user, safe="")
    safe_password = quote(password, safe="")
    return f"rtsp://{safe_user}:{safe_password}@{host}:{port}/{stream}"


def connect_ptz(host: str, port: int, user: str, password: str):
    cam = ONVIFCamera(host, port, user, password)
    media = cam.create_media_service()
    profile = media.GetProfiles()[0]
    ptz = cam.create_ptz_service()
    return ptz, profile.token


def stop_pan(ptz, profile_token: str) -> None:
    try:
        ptz.Stop({"ProfileToken": profile_token, "PanTilt": True})
    except Exception:
        pass


def pan_for_seconds(ptz, profile_token: str, speed: float, seconds: float) -> None:
    ptz.ContinuousMove(
        {
            "ProfileToken": profile_token,
            "Velocity": {"PanTilt": {"x": speed, "y": 0.0}},
        }
    )
    time.sleep(max(0.05, seconds))
    stop_pan(ptz, profile_token)


def capture_frame(rtsp_url: str, warmup_frames: int, retries: int = 8):
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise RuntimeError("Could not open RTSP stream. Check camera IP, credentials, and RTSP settings.")

    try:
        for _ in range(max(0, warmup_frames)):
            cap.read()

        for _ in range(max(1, retries)):
            ok, frame = cap.read()
            if ok and frame is not None:
                return frame
            time.sleep(0.12)
    finally:
        cap.release()

    raise RuntimeError("Failed to capture a frame from RTSP stream.")


def normalize_height(left, right):
    target_h = min(left.shape[0], right.shape[0])
    if left.shape[0] != target_h:
        left_w = int(left.shape[1] * (target_h / left.shape[0]))
        left = cv2.resize(left, (left_w, target_h), interpolation=cv2.INTER_AREA)
    if right.shape[0] != target_h:
        right_w = int(right.shape[1] * (target_h / right.shape[0]))
        right = cv2.resize(right, (right_w, target_h), interpolation=cv2.INTER_AREA)
    return left, right


def parse_args():
    parser = argparse.ArgumentParser(
        description="Capture two snapshots with PTZ pan and build a side-by-side panorama.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default=os.getenv("TAPOCAM_HOST", "192.168.1.102"), help="Camera IP/hostname")
    parser.add_argument("--user", default=os.getenv("TAPOCAM_USER", ""), help="Camera account username")
    parser.add_argument("--password", default=os.getenv("TAPOCAM_PASSWORD", ""), help="Camera account password")
    parser.add_argument("--onvif-port", type=int, default=int(os.getenv("TAPOCAM_ONVIF_PORT", "2020")), help="ONVIF service port")
    parser.add_argument("--rtsp-port", type=int, default=int(os.getenv("TAPOCAM_RTSP_PORT", "554")), help="RTSP port")
    parser.add_argument(
        "--stream",
        choices=["stream1", "stream2"],
        default=os.getenv("TAPOCAM_RTSP_STREAM", "stream1"),
        help="RTSP stream path",
    )
    parser.add_argument("--pan-speed", type=float, default=0.8, help="Pan speed from -1.0 to 1.0")
    parser.add_argument(
        "--half-sweep-seconds",
        type=float,
        default=1.6,
        help="Duration to pan from center to one side (script pans double this for the second shot)",
    )
    parser.add_argument("--settle-seconds", type=float, default=1.0, help="Wait time before each snapshot")
    parser.add_argument("--warmup-frames", type=int, default=6, help="Frames to discard before each snapshot")
    parser.add_argument("--output-dir", default=default_output_dir_arg(), help="Directory to save snapshots and panorama")
    parser.add_argument("--start-from-home", action="store_true", help="Try to move to camera home position before shooting")
    parser.add_argument("--return-home", action="store_true", help="Try to return camera to home position at the end")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.user or not args.password:
        raise ValueError("Missing credentials. Set --user/--password or TAPOCAM_USER/TAPOCAM_PASSWORD.")

    output_dir = resolve_image_dir(args.output_dir)
    rtsp_url = build_rtsp_url(args.host, args.user, args.password, args.rtsp_port, args.stream)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    left_path = output_dir / f"{ts}_left.jpg"
    right_path = output_dir / f"{ts}_right.jpg"
    pano_path = output_dir / f"{ts}_panorama.jpg"

    speed = abs(args.pan_speed)
    half_sweep = max(0.1, args.half_sweep_seconds)
    settle = max(0.1, args.settle_seconds)

    print(f"Connecting ONVIF PTZ at {args.host}:{args.onvif_port}...")
    print(f"Saving images to: {output_dir}")
    ptz, profile_token = connect_ptz(args.host, args.onvif_port, args.user, args.password)

    if args.start_from_home:
        try:
            ptz.GotoHomePosition({"ProfileToken": profile_token})
            time.sleep(settle)
        except Exception:
            print("Home position not available; continuing from current camera angle.")

    try:
        print("Panning to first view...")
        pan_for_seconds(ptz, profile_token, -speed, half_sweep)
        time.sleep(settle)
        left_frame = capture_frame(rtsp_url, args.warmup_frames)
        cv2.imwrite(str(left_path), left_frame)
        print(f"Saved first snapshot: {left_path}")

        print("Panning to second view...")
        pan_for_seconds(ptz, profile_token, speed, half_sweep * 2.0)
        time.sleep(settle)
        right_frame = capture_frame(rtsp_url, args.warmup_frames)
        cv2.imwrite(str(right_path), right_frame)
        print(f"Saved second snapshot: {right_path}")

        left_frame, right_frame = normalize_height(left_frame, right_frame)
        panorama = cv2.hconcat([left_frame, right_frame])
        cv2.imwrite(str(pano_path), panorama)
        print(f"Saved panorama: {pano_path}")
    finally:
        stop_pan(ptz, profile_token)
        if args.return_home:
            try:
                ptz.GotoHomePosition({"ProfileToken": profile_token})
            except Exception:
                pass


if __name__ == "__main__":
    main()
