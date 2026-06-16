# onvif_dump_options.py
from onvif import ONVIFCamera
HOST="192.168.0.67"; PORT=2020; USER="armank"; PWD="Test1234"

cam = ONVIFCamera(HOST, PORT, USER, PWD)
media = cam.create_media_service()

profiles = media.GetProfiles()
print("Profiles:", [p.token for p in profiles])
for p in profiles:
    print("\n== Profile:", p.token)
    enc = media.GetVideoEncoderConfiguration({'ConfigurationToken': p.VideoEncoderConfiguration.token})
    print("Current:", enc)
    try:
        opts = media.GetVideoEncoderConfigurationOptions({'ConfigurationToken': p.VideoEncoderConfiguration.token})
        print("Options:", opts)
    except Exception as e:
        print("Options not available:", e)
