import time
import sys
from onvif import ONVIFCamera

# ==== CONFIG ====
HOST = "172.20.10.3"   # camera IP (same one you use in VLC)
PORT = 2020             # ONVIF service port
USER = "marsworks"         # Camera Account user (not your TP-Link cloud login)
PWD  = "marsworks"       # Camera Account password

# Movement defaults (tweak live with keys)
SPEED = 0.8             # 0.1 .. 1.0  (how fast to pan/tilt)
PULSE = 0.6             # seconds     (how long each keypress moves)

# ==== KEY INPUT (cross-platform) ====
def getch():
    """Return one character without Enter. Works on Windows & Unix."""
    try:  # Windows
        import msvcrt
        ch = msvcrt.getch()
        # decode bytes; handle arrow keys which come as b'\xe0'+code
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            arrows = {b'H':'w', b'P':'s', b'K':'a', b'M':'d'}  # up,down,left,right
            return arrows.get(ch2, '')
        return ch.decode('utf-8', errors='ignore')
    except ImportError:  # Unix
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            # crude arrow mapping (reads ESC [ A/B/C/D)
            if ch == '\x1b':
                seq = sys.stdin.read(2)  # [ + code
                arrows = {'A':'w', 'B':'s', 'D':'a', 'C':'d'}
                return arrows.get(seq[1], '')
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ==== PTZ CONTROL ====
def ptz_services():
    cam = ONVIFCamera(HOST, PORT, USER, PWD)
    media = cam.create_media_service()
    profile = media.GetProfiles()[0]  # main profile; PTZ token is shared
    ptz = cam.create_ptz_service()
    return ptz, profile

def nudge(ptz, profile, x, y, pulse):
    """ContinuousMove for `pulse` seconds at speed (x,y), then Stop."""
    try:
        ptz.ContinuousMove({
            'ProfileToken': profile.token,
            'Velocity': {'PanTilt': {'x': x, 'y': y}}
        })
        time.sleep(max(0.05, pulse))
    finally:
        try:
            ptz.Stop({'ProfileToken': profile.token, 'PanTilt': True})
        except Exception:
            pass

def go_home(ptz, profile):
    try:
        ptz.GotoHomePosition({'ProfileToken': profile.token})
    except Exception:
        # If no home set, fall back to absolute center (0,0) if supported
        try:
            ptz.AbsoluteMove({
                'ProfileToken': profile.token,
                'Position': {'PanTilt': {'x': 0.0, 'y': 0.0}}
            })
        except Exception:
            print("No home/absolute move available on this model.")

def main():
    print("Connecting to camera…")
    ptz, profile = ptz_services()
    print("✅ Connected. Open video at:")
    print(f"   rtsp://{USER}:{PWD}@{HOST}:554/stream2  (360p@15fps)")
    print("\nControls:")
    print("  W/A/S/D  = up/left/down/right")
    print("  Q/E      = up-left / up-right")
    print("  Z/C      = down-left / down-right")
    print("  H        = go Home (if supported)")
    print("  +/-      = speed  (current affects magnitude)")
    print("  [/ ]     = pulse  (move duration per key)")
    print("  X        = STOP now (emergency)")
    print("  ESC or Q = quit\n")

    speed = SPEED
    pulse = PULSE

    while True:
        ch = getch().lower()
        if ch in ('\x1b', 'q'):  # ESC or q
            print("👋 Bye")
            break
        elif ch == 'x':
            try:
                ptz.Stop({'ProfileToken': profile.token, 'PanTilt': True})
            except Exception:
                pass
            print("⛔ STOP")
        elif ch == 'h':
            print("🏠 Home")
            go_home(ptz, profile)
        elif ch == '+':
            speed = min(1.0, round(speed + 0.1, 2))
            print(f"⚡ speed = {speed}")
        elif ch == '-':
            speed = max(0.1, round(speed - 0.1, 2))
            print(f"⚡ speed = {speed}")
        elif ch == ']':
            pulse = min(3.0, round(pulse + 0.1, 2))
            print(f"⏱ pulse = {pulse}s")
        elif ch == '[':
            pulse = max(0.1, round(pulse - 0.1, 2))
            print(f"⏱ pulse = {pulse}s")
        elif ch in ('w','a','s','d','q','e','z','c'):
            # map keys to x/y
            dirs = {
                'w': ( 0.0,  1.0),
                's': ( 0.0, -1.0),
                'a': (-1.0,  0.0),
                'd': ( 1.0,  0.0),
                'q': (-0.707,  0.707),
                'e': ( 0.707,  0.707),
                'z': (-0.707, -0.707),
                'c': ( 0.707, -0.707),
            }
            dx, dy = dirs[ch]
            x = round(dx * speed, 3)
            y = round(dy * speed, 3)
            print(f"→ move x={x} y={y} for {pulse}s")
            nudge(ptz, profile, x, y, pulse)
        else:
            # ignore other keys to keep it smooth
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bye")
