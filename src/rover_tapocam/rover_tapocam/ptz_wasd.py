#!/usr/bin/env python3
"""Keyboard PTZ control for ONVIF-compatible Tapo cameras."""

import argparse
import os
import sys
import time

from onvif import ONVIFCamera


def getch():
    """Return one character without Enter. Works on Windows and Unix."""
    try:
        import msvcrt

        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            ch2 = msvcrt.getch()
            arrows = {b"H": "w", b"P": "s", b"K": "a", b"M": "d"}
            return arrows.get(ch2, "")
        return ch.decode("utf-8", errors="ignore")
    except ImportError:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                seq = sys.stdin.read(2)
                arrows = {"A": "w", "B": "s", "D": "a", "C": "d"}
                return arrows.get(seq[1], "")
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def ptz_services(host: str, port: int, user: str, password: str):
    cam = ONVIFCamera(host, port, user, password)
    media = cam.create_media_service()
    profile = media.GetProfiles()[0]
    ptz = cam.create_ptz_service()
    return ptz, profile


def nudge(ptz, profile, x: float, y: float, pulse: float):
    """ContinuousMove for pulse seconds at speed (x,y), then Stop."""
    try:
        ptz.ContinuousMove(
            {
                "ProfileToken": profile.token,
                "Velocity": {"PanTilt": {"x": x, "y": y}},
            }
        )
        time.sleep(max(0.05, pulse))
    finally:
        try:
            ptz.Stop({"ProfileToken": profile.token, "PanTilt": True})
        except Exception:
            pass


def go_home(ptz, profile):
    try:
        ptz.GotoHomePosition({"ProfileToken": profile.token})
    except Exception:
        try:
            ptz.AbsoluteMove(
                {
                    "ProfileToken": profile.token,
                    "Position": {"PanTilt": {"x": 0.0, "y": 0.0}},
                }
            )
        except Exception:
            print("No home/absolute move available on this model.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Interactive keyboard PTZ control for ONVIF cameras.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default=os.getenv("TAPOCAM_HOST", "192.168.1.102"), help="Camera IP/hostname")
    parser.add_argument("--onvif-port", type=int, default=int(os.getenv("TAPOCAM_ONVIF_PORT", "2020")), help="ONVIF service port")
    parser.add_argument("--rtsp-port", type=int, default=int(os.getenv("TAPOCAM_RTSP_PORT", "554")), help="RTSP port")
    parser.add_argument("--user", default=os.getenv("TAPOCAM_USER", ""), help="Camera account username")
    parser.add_argument("--password", default=os.getenv("TAPOCAM_PASSWORD", ""), help="Camera account password")
    parser.add_argument("--stream", choices=["stream1", "stream2"], default=os.getenv("TAPOCAM_RTSP_STREAM", "stream2"), help="RTSP stream path for operator preview")
    parser.add_argument("--speed", type=float, default=0.8, help="Initial movement speed [0.1..1.0]")
    parser.add_argument("--pulse", type=float, default=0.6, help="Initial move duration in seconds")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.user or not args.password:
        raise ValueError("Missing credentials. Set --user/--password or TAPOCAM_USER/TAPOCAM_PASSWORD.")

    print("Connecting to camera...")
    ptz, profile = ptz_services(args.host, args.onvif_port, args.user, args.password)
    print("Connected.")
    print(f"Preview stream URL: rtsp://{args.user}:{args.password}@{args.host}:{args.rtsp_port}/{args.stream}")
    print("")
    print("Controls:")
    print("  W/A/S/D = up/left/down/right")
    print("  Q/E     = up-left/up-right")
    print("  Z/C     = down-left/down-right")
    print("  H       = go Home")
    print("  +/-     = speed")
    print("  [ / ]   = pulse duration")
    print("  X       = stop now")
    print("  ESC     = quit")
    print("")

    speed = max(0.1, min(1.0, args.speed))
    pulse = max(0.1, args.pulse)

    while True:
        ch = getch().lower()
        if ch == "\x1b":
            print("Bye")
            break
        if ch == "x":
            try:
                ptz.Stop({"ProfileToken": profile.token, "PanTilt": True})
            except Exception:
                pass
            print("STOP")
            continue
        if ch == "h":
            print("Home")
            go_home(ptz, profile)
            continue
        if ch == "+":
            speed = min(1.0, round(speed + 0.1, 2))
            print(f"speed={speed}")
            continue
        if ch == "-":
            speed = max(0.1, round(speed - 0.1, 2))
            print(f"speed={speed}")
            continue
        if ch == "]":
            pulse = min(3.0, round(pulse + 0.1, 2))
            print(f"pulse={pulse}s")
            continue
        if ch == "[":
            pulse = max(0.1, round(pulse - 0.1, 2))
            print(f"pulse={pulse}s")
            continue

        directions = {
            "w": (0.0, 1.0),
            "s": (0.0, -1.0),
            "a": (-1.0, 0.0),
            "d": (1.0, 0.0),
            "q": (-0.707, 0.707),
            "e": (0.707, 0.707),
            "z": (-0.707, -0.707),
            "c": (0.707, -0.707),
        }
        if ch in directions:
            dx, dy = directions[ch]
            x = round(dx * speed, 3)
            y = round(dy * speed, 3)
            print(f"move x={x} y={y} for {pulse}s")
            nudge(ptz, profile, x, y, pulse)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye")

