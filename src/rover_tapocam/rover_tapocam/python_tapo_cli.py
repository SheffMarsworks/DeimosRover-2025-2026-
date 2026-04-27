#!/usr/bin/env python3
"""Small Tapo CLI using pytapo."""

import argparse
import json
import os
import sys
from typing import Optional, Tuple

from pytapo import Tapo


def connect(
    host: str,
    user: str,
    password: str,
    cloud_password: Optional[str],
    auth_mode: str = "auto",
) -> Tuple[Tapo, str]:
    if auth_mode in ("local", "auto"):
        try:
            cam = Tapo(host, user, password)
            _ = cam.getBasicInfo()
            return cam, "camera_account"
        except Exception:
            if auth_mode == "local":
                raise

    if auth_mode in ("cloud", "auto"):
        if not cloud_password:
            raise RuntimeError("Cloud auth selected but --cloud-pass was not provided")
        try:
            cam = Tapo(host, "admin", cloud_password)
            _ = cam.getBasicInfo()
            return cam, "cloud_fallback"
        except Exception:
            if auth_mode == "cloud":
                raise

    raise RuntimeError("Invalid authentication data (both local and cloud paths failed)")


def cmd_info(args):
    cam, mode = connect(args.host, args.user, args.password, args.cloud_pass, args.auth)
    info = cam.getBasicInfo()
    print(json.dumps({"auth_mode": mode, "basic_info": info}, indent=2))


def cmd_privacy(args):
    cam, _ = connect(args.host, args.user, args.password, args.cloud_pass, args.auth)
    try:
        if args.state.lower() in ("on", "true", "1"):
            cam.setPrivacyMode(True)
            print("Privacy mode: ON")
        elif args.state.lower() in ("off", "false", "0"):
            cam.setPrivacyMode(False)
            print("Privacy mode: OFF")
        else:
            raise ValueError("Use 'on' or 'off'.")
    except AttributeError:
        print("This model/firmware may not support privacy toggling via API.", file=sys.stderr)
        sys.exit(2)


def cmd_hint(args):
    _, mode = connect(args.host, args.user, args.password, args.cloud_pass, args.auth)
    print("Connection OK")
    print(f"Auth mode used: {mode}")
    print("")
    print("Next steps / tips:")
    print("- For local RTSP, enable Camera Account and local streaming in the Tapo app.")
    print("- If RTSP is enabled, test with:")
    print("    vlc rtsp://<USER>:<PASS>@<HOST>:554/stream1")
    print("- To fetch SD recordings, check pytapo examples (ffmpeg required).")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Tiny Tapo CLI using pytapo.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--auth", choices=["auto", "local", "cloud"], default="auto", help="Which auth path to use")
    parser.add_argument("--host", default=os.getenv("TAPOCAM_HOST", "192.168.1.102"), help="Camera IP address")
    parser.add_argument("--user", default=os.getenv("TAPOCAM_USER", ""), help="Camera account username")
    parser.add_argument("--password", default=os.getenv("TAPOCAM_PASSWORD", ""), help="Camera account password")
    parser.add_argument("--cloud-pass", default=os.getenv("TAPOCAM_CLOUD_PASSWORD", ""), help="TP-Link cloud password (optional fallback auth)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    s_info = sub.add_parser("info", help="Print basic camera info")
    s_info.set_defaults(func=cmd_info)

    s_priv = sub.add_parser("privacy", help="Toggle privacy mode on/off")
    s_priv.add_argument("state", choices=["on", "off"], help="Privacy state")
    s_priv.set_defaults(func=cmd_privacy)

    s_hint = sub.add_parser("hint", help="Print streaming/next-step hints")
    s_hint.set_defaults(func=cmd_hint)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.user or not args.password:
        raise ValueError("Missing credentials. Set --user/--password or TAPOCAM_USER/TAPOCAM_PASSWORD.")

    try:
        args.func(args)
    except Exception as exc:
        print(f"[!] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

