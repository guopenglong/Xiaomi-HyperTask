import argparse
import sys
from miio import MiotDevice
from miio.exceptions import DeviceException

# ==========================================
# --- 配置区 (请根据实际情况修改) ---
# ==========================================
# 设备 IP 地址 (在米家 App 或路由器后台查看)
DEVICE_IP = "your_device_ip_here"

# 设备 Token (使用 Xiaomi-cloud-tokens-extractor 获取)
DEVICE_TOKEN = "your_device_token_here"

# ==========================================
# --- 设备控制逻辑 ---
# ==========================================

def control_device(action):
    """
    控制米家设备 (本地局域网模式)
    """
    try:
        # 初始化设备 (lazy_discover=True 减少初始化时间)
        device = MiotDevice(ip=DEVICE_IP, token=DEVICE_TOKEN, lazy_discover=True)
        
        # 示例: 控制氛围灯 (siid=3, piid=10 为示例，请根据实际设备修改)
        # 提示: 不同设备的 siid 和 piid 不同，请查阅 miio 文档或使用 miiocli 探测
        if action == "on":
            device.set_property_by(siid=3, piid=10, value=True)
            print(f"✅ 设备已开启 (IP: {DEVICE_IP})")
        elif action == "off":
            device.set_property_by(siid=3, piid=10, value=False)
            print(f"✅ 设备已关闭 (IP: {DEVICE_IP})")
            
    except DeviceException as e:
        print(f"❌ 设备控制失败: {e}")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

# ==========================================
# --- 主程序入口 ---
# ==========================================

if __name__ == "__main__":
    # 检查配置是否已修改
    if DEVICE_IP == "your_device_ip_here" or DEVICE_TOKEN == "your_device_token_here":
        print("❌ 错误: 请先在 local_control.py 中配置您的 DEVICE_IP 和 DEVICE_TOKEN")
        sys.exit(1)

    # 命令行参数解析
    parser = argparse.ArgumentParser(description="Xiaomi Device Local Control Template")
    parser.add_argument("action", choices=["on", "off"], help="on: 开启设备, off: 关闭设备")
    args = parser.parse_args()

    # 执行控制逻辑
    control_device(args.action)
