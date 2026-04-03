import paho.mqtt.client as mqtt
import os
import sys

# ==========================================
# --- 配置区 (请根据实际情况修改) ---
# ==========================================
# 巴法云 UID (在控制台获取)
BEMFA_UID = "your_bemfa_uid_here"

# 订阅的主题列表 (在巴法云创建的主题)
# 建议格式: ["topic1", "topic2"]
TOPICS = ["your_topic_1", "your_topic_2"]

# MQTT 服务器配置
MQTT_BROKER = "bemfa.com"
MQTT_PORT = 9501
KEEPALIVE = 60

# ==========================================
# --- 业务逻辑处理函数 ---
# ==========================================

def handle_task_1(payload):
    """
    处理主题 1 的逻辑 (例如: 自动化脚本执行)
    """
    if payload == "on":
        print("🚀 正在执行任务 1: [开启] 逻辑...")
        # 示例: 执行本地脚本
        # os.system("python3 your_script.py")
    elif payload == "off":
        print("💤 正在执行任务 1: [关闭] 逻辑...")

def handle_task_2(payload):
    """
    处理主题 2 的逻辑 (例如: 米家设备控制)
    """
    if payload == "on":
        print("🚀 正在执行任务 2: [开启] 逻辑...")
        # 示例: 使用 MiService 控制云端设备
        # os.system("MI_DID=your_did python3 MiService/micli.py 2=#60")
    elif payload == "off":
        print("💤 正在执行任务 2: [关闭] 逻辑...")

# ==========================================
# --- MQTT 回调函数 ---
# ==========================================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ 已成功连接巴法云 (UID: {BEMFA_UID})")
        # 动态订阅所有配置的主题
        subscribe_list = [(topic, 0) for topic in TOPICS]
        client.subscribe(subscribe_list)
        print(f"📡 已开始监听主题: {', '.join(TOPICS)}")
    else:
        print(f"❌ 连接失败，错误码: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    # 解析数据并清洗
    payload = msg.payload.decode().strip().lower()
    
    print(f"🔔 收到指令: 主题[{topic}] -> 内容[{payload}]")

    # 根据主题分发任务
    if topic == TOPICS[0]:
        handle_task_1(payload)
    elif len(TOPICS) > 1 and topic == TOPICS[1]:
        handle_task_2(payload)
    else:
        print(f"⚠️ 收到未知主题 [{topic}] 的消息，请检查配置。")

def on_subscribe(client, userdata, mid, granted_qos):
    print("✨ 所有主题已成功订阅，设备已在云端上线。")

# ==========================================
# --- 主程序入口 ---
# ==========================================

if __name__ == "__main__":
    if BEMFA_UID == "your_bemfa_uid_here":
        print("❌ 错误: 请先在 HyperTask.py 中配置您的 BEMFA_UID")
        sys.exit(1)

    client = mqtt.Client(client_id=BEMFA_UID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    try:
        print(f"🔄 正在连接 {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, MQTT_PORT, KEEPALIVE)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n👋 程序已手动停止。")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        sys.exit(1)
