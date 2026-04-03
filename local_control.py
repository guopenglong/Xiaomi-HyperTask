import argparse
from miio import MiotDevice
from miio.exceptions import DeviceException

# ===== 填入你的设备信息 =====
DEVICE_IP = "xxxxxx"
DEVICE_TOKEN = "xxxxxxx"
# ===========================

device = MiotDevice(ip=DEVICE_IP, token=DEVICE_TOKEN, lazy_discover=True)

def turn_on_ambient_light():
    device.set_property_by(siid=3, piid=10, value=True)
    print("✅ light turned ON")

def turn_off_ambient_light():
    device.set_property_by(siid=3, piid=10, value=False)
    print("✅ light turned OFF")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control Xiaomi  light")
    parser.add_argument("action", choices=["on", "off"], help="on: turn on, off: turn off")
    args = parser.parse_args()

    if args.action == "on":
        turn_on_ambient_light()
    elif args.action == "off":
        turn_off_ambient_light()
