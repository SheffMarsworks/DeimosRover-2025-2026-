#!/usr/bin/env python3
"""Dump ONVIF media profiles and encoder options."""

import argparse
import os

from onvif import ONVIFCamera


def parse_args():
    parser = argparse.ArgumentParser(
        description="Print ONVIF media profiles and encoder options.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default=os.getenv("TAPOCAM_HOST", "192.168.1.102"), help="Camera IP/hostname")
    parser.add_argument("--onvif-port", type=int, default=int(os.getenv("TAPOCAM_ONVIF_PORT", "2020")), help="ONVIF service port")
    parser.add_argument("--user", default=os.getenv("TAPOCAM_USER", ""), help="Camera account username")
    parser.add_argument("--password", default=os.getenv("TAPOCAM_PASSWORD", ""), help="Camera account password")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.user or not args.password:
        raise ValueError("Missing credentials. Set --user/--password or TAPOCAM_USER/TAPOCAM_PASSWORD.")

    cam = ONVIFCamera(args.host, args.onvif_port, args.user, args.password)
    media = cam.create_media_service()

    profiles = media.GetProfiles()
    print(f"Profiles: {[p.token for p in profiles]}")
    for profile in profiles:
        print(f"\n== Profile: {profile.token}")
        enc = media.GetVideoEncoderConfiguration(
            {"ConfigurationToken": profile.VideoEncoderConfiguration.token}
        )
        print(f"Current: {enc}")
        try:
            opts = media.GetVideoEncoderConfigurationOptions(
                {"ConfigurationToken": profile.VideoEncoderConfiguration.token}
            )
            print(f"Options: {opts}")
        except Exception as exc:
            print(f"Options not available: {exc}")


if __name__ == "__main__":
    main()

