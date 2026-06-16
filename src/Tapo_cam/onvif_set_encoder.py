# onvif_set_encoder.py
from onvif import ONVIFCamera

HOST="192.168.0.67"; PORT=2020; USER="armank"; PWD="Test1234"
cam = ONVIFCamera(HOST, PORT, USER, PWD)
media = cam.create_media_service()
profiles = media.GetProfiles()
prof = profiles[0]

# See current encoder config
enc = media.GetVideoEncoderConfiguration({'ConfigurationToken': prof.VideoEncoderConfiguration.token})
print("Before:", enc)

# Try adjust (values are examples)
enc.RateControl.BitrateLimit = 1024   # kbps
enc.RateControl.FrameRateLimit = 15   # fps
# If H264: enc.H264.GovLength = 30     # GOP
try:
    media.SetVideoEncoderConfiguration({'Configuration': enc, 'ForcePersistence': True})
    enc2 = media.GetVideoEncoderConfiguration({'ConfigurationToken': enc.token})
    print("After:", enc2)
except Exception as e:
    print("Camera refused encoder changes:", e)
