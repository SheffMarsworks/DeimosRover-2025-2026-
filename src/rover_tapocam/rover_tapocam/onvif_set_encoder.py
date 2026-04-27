#!/usr/bin/env python3
"""Adjust ONVIF encoder settings."""

import argparse
import os

from onvif import ONVIFCamera


def parse_args():
    parser = argparse.ArgumentParser(
        description="Set ONVIF video encoder bitrate/framerate for one profile.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default=os.getenv("TAPOCAM_HOST", "192.168.1.102"), help="Camera IP/hostname")
    parser.add_argument("--onvif-port", type=int, default=int(os.getenv("TAPOCAM_ONVIF_PORT", "2020")), help="ONVIF service port")
    parser.add_argument("--user", default=os.getenv("TAPOCAM_USER", ""), help="Camera account username")
    parser.add_argument("--password", default=os.getenv("TAPOCAM_PASSWORD", ""), help="Camera account password")
    parser.add_argument("--profile-index", type=int, default=0, help="Media profile index to update")
    parser.add_argument("--bitrate", type=int, default=1024, help="Bitrate in kbps")
    parser.add_argument("--framerate", type=int, default=15, help="Frame rate in fps")
    parser.add_argument("--persist", action="store_true", help="Set ForcePersistence=True")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.user or not args.password:
        raise ValueError("Missing credentials. Set --user/--password or TAPOCAM_USER/TAPOCAM_PASSWORD.")

    cam = ONVIFCamera(args.host, args.onvif_port, args.user, args.password)
    media = cam.create_media_service()
    profiles = media.GetProfiles()

    if args.profile_index < 0 or args.profile_index >= len(profiles):
        raise ValueError(f"Invalid --profile-index {args.profile_index}; available [0..{len(profiles) - 1}]")

    profile = profiles[args.profile_index]
    token = profile.VideoEncoderConfiguration.token
    enc = media.GetVideoEncoderConfiguration({"ConfigurationToken": token})
    print(f"Before: {enc}")

    enc.RateControl.BitrateLimit = args.bitrate
    enc.RateControl.FrameRateLimit = args.framerate

    media.SetVideoEncoderConfiguration(
        {"Configuration": enc, "ForcePersistence": bool(args.persist)}
    )
    enc_after = media.GetVideoEncoderConfiguration({"ConfigurationToken": enc.token})
    print(f"After: {enc_after}")


if __name__ == "__main__":
    main()

