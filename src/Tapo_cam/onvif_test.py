from onvif import ONVIFCamera
from urllib.parse import urlparse, urlunparse

HOST = "192.168.0.67"       # use the IP that worked in VLC
PORT = 2020                 # ONVIF service port per TP-Link docs
USER = "armank"             # your Camera Account
PWD  = "Test1234"

# Connect
cam = ONVIFCamera(HOST, PORT, USER, PWD)

# Device info
dev_mgmt = cam.create_devicemgmt_service()
info = dev_mgmt.GetDeviceInformation()
print("Device information:", info)

# Media profiles -> RTSP URL (should match your VLC URL)
media = cam.create_media_service()
profiles = media.GetProfiles()
profile = profiles[0]
stream = media.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast','Transport': {'Protocol': 'RTSP'}},
                             'ProfileToken': profile.token})
# Ensure credentials embedded (some clients need it)
u = urlparse(stream.Uri)
rtsp_with_creds = urlunparse((u.scheme, f"{USER}:{PWD}@{u.hostname}:{u.port or 554}", u.path, u.params, u.query, u.fragment))
print("RTSP:", rtsp_with_creds)

# PTZ (only if your model supports it)
try:
    ptz = cam.create_ptz_service()
    status = ptz.GetStatus({'ProfileToken': profile.token})
    print("PTZ status ok")
    # Nudge left a bit (adjust x/y speeds as you like)
    ptz.ContinuousMove({'ProfileToken': profile.token,
                        'Velocity': {'PanTilt': {'x': -1.0, 'y': 0.0}}})
    import time; time.sleep(2.0)
    ptz.Stop({'ProfileToken': profile.token, 'PanTilt': True})
    print("PTZ moved left.")
except Exception as e:
    print("PTZ not supported or disabled:", e)
