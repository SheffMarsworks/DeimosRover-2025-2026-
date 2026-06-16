import argparse
import json
import sys
from pytapo import Tapo

def connect(host: str, user: str, password: str, cloud_password: str | None, auth_mode: str = "auto"):
    if auth_mode in ("local", "auto"):
        try:
            cam = Tapo(host, user, password)
            _ = cam.getBasicInfo()
            return cam, "camera_account"
        except Exception as e_local:
            if auth_mode == "local":
                raise

    if auth_mode in ("cloud", "auto"):
        if not cloud_password:
            raise RuntimeError("Cloud auth selected but --cloud-pass was not provided")
        try:
            cam = Tapo(host, "admin", cloud_password)
            _ = cam.getBasicInfo()
            return cam, "cloud_fallback"
        except Exception as e_cloud:
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
    cam, mode = connect(args.host, args.user, args.password, args.cloud_pass, args.auth)
    print("Connection OK ✅")
    print(f"Auth mode used: {mode}")
    print()
    print("Next steps / tips:")
    print("- You can view a live stream via the Tapo app. For local RTSP, some models expose it only after enabling 'Camera Account' and allowing local streaming in the app.")
    print("- If your model supports RTSP and it's enabled, try a player like VLC:")
    print("    vlc rtsp://<USER>:<PASS>@<HOST>:554/stream1")
    print("  (Exact RTSP path varies by model; check the app or vendor docs.)")
    print("- To fetch SD recordings, see pytapo repo’s example script (you’ll need ffmpeg and your TP-Link cloud password).")

def build_parser():
    p = argparse.ArgumentParser(
        description="Tiny Tapo CLI using pytapo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ✅ add --auth *inside* build_parser()
    p.add_argument("--auth", choices=["auto", "local", "cloud"], default="auto",
                   help="Which auth path to use")

    p.add_argument("--host", required=True, help="Camera IP address (e.g., 192.168.0.123)")
    p.add_argument("--user", required=True, help="Camera Account username (from Tapo app > Advanced settings > Camera account)")
    p.add_argument("--password", required=True, help="Camera Account password")
    p.add_argument("--cloud-pass", help="TP-Link cloud password (fallback auth for some models)")

    sub = p.add_subparsers(dest="cmd", required=True)

    s_info = sub.add_parser("info", help="Print basic camera info")
    s_info.set_defaults(func=cmd_info)

    s_priv = sub.add_parser("privacy", help="Toggle privacy mode on/off")
    s_priv.add_argument("state", choices=["on", "off"], help="Privacy state")
    s_priv.set_defaults(func=cmd_privacy)

    s_hint = sub.add_parser("hint", help="Print streaming/next-step hints")
    s_hint.set_defaults(func=cmd_hint)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"[!] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
