#!/usr/bin/env python3
"""Basic ONVIF connectivity and PTZ test."""

import argparse
import os
import time
from urllib.parse import urlparse, urlunparse

from onvif import ONVIFCamera


def parse_args():
    parser = argparse.ArgumentParser(
        description="ONVIF connection test with optional PTZ nudge.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default=os.getenv("TAPOCAM_HOST", "192.168.1.102"), help="Camera IP/hostname")
    parser.add_argument("--onvif-port", type=int, default=int(os.getenv("TAPOCAM_ONVIF_PORT", "2020")), help="ONVIF service port")
    parser.add_argument("--rtsp-port", type=int, default=int(os.getenv("TAPOCAM_RTSP_PORT", "554")), help="RTSP fallback port")
    parser.add_argument("--user", default=os.getenv("TAPOCAM_USER", ""), help="Camera account username")
    parser.add_argument("--password", default=os.getenv("TAPOCAM_PASSWORD", ""), help="Camera account password")
    parser.add_argument("--move-seconds", type=float, default=2.0, help="PTZ left nudge time. Set 0 to skip PTZ move")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.user or not args.password:
        raise ValueError("Missing credentials. Set --user/--password or TAPOCAM_USER/TAPOCAM_PASSWORD.")

    cam = ONVIFCamera(args.host, args.onvif_port, args.user, args.password)
    dev_mgmt = cam.create_devicemgmt_service()
    info = dev_mgmt.GetDeviceInformation()
    print(f"Device information: {info}")

    media = cam.create_media_service()
    profiles = media.GetProfiles()
    profile = profiles[0]
    stream = media.GetStreamUri(
        {
            "StreamSetup": {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}},
            "ProfileToken": profile.token,
        }
    )

    uri = urlparse(stream.Uri)
    rtsp_with_creds = urlunparse(
        (
            uri.scheme,
            f"{args.user}:{args.password}@{uri.hostname}:{uri.port or args.rtsp_port}",
            uri.path,
            uri.params,
            uri.query,
            uri.fragment,
        )
    )
    print(f"RTSP: {rtsp_with_creds}")

    try:
        ptz = cam.create_ptz_service()
        status = ptz.GetStatus({"ProfileToken": profile.token})
        print(f"PTZ status: {status}")

        if args.move_seconds > 0:
            ptz.ContinuousMove(
                {
                    "ProfileToken": profile.token,
                    "Velocity": {"PanTilt": {"x": -1.0, "y": 0.0}},
                }
            )
            time.sleep(max(0.05, args.move_seconds))
            ptz.Stop({"ProfileToken": profile.token, "PanTilt": True})
            print("PTZ moved left.")
    except Exception as exc:
        print(f"PTZ not supported or disabled: {exc}")


if __name__ == "__main__":
    main()

