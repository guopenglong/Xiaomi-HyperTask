import paho.mqtt.client as mqtt
import os

# --- 配置区 ---
UID = "xxxxxxxxxxxxxx"
# 假设你在巴法云创建了两个主题，分别对应不同的功能
TOPIC_1 = "xxxxxxxx"  # 比如：进京证续签
TOPIC_2 = "xxxxxxxx"    # 比如：氛围灯开关

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ 已成功连接巴法云")
        # 同时订阅两个个主题
        client.subscribe([(TOPIC_1, 0), (TOPIC_2, 0)])
        print(f"📡 已开始同时监听: {TOPIC_1}, {TOPIC_2}")
    else:
        print(f"❌ 连接失败，错误码: {rc}")

def on_message(client, userdata, msg):
    # 1. 解析数据（务必加上 .strip() 防止不可见字符干扰）
    topic = msg.topic
    payload = msg.payload.decode().strip().lower()
    
    print(f"🔔 收到指令: 主题[{topic}] -> 内容[{payload}]")

    # --- 逻辑分发：根据不同主题执行不同任务 ---
    
    # 任务 A (TOPIC_1)
    if topic == TOPIC_1:
        if payload == "on":
            print(f"🚀 执行 {topic} 的【开启】逻辑")
            os.system("python3 test.py")
            # 这里写你开启 A 的代码
        elif payload == "off":
            print(f"💤 执行 {topic} 的【关闭】逻辑")
            # 这里写你关闭 A 的代码

    # 任务 B (TOPIC_2)
    elif topic == TOPIC_2:
        if payload == "on":
            print(f"🚀 执行 {topic} 的【开启】逻辑")
            os.system("MI_DID=xxxx python3 MiService/micli.py 3-10=true")
            # 这里写你开启 B 的代码
        elif payload == "off":
            print(f"💤 执行 {topic} 的【关闭】逻辑")
            os.system("MI_DID=xxxxx python3 MiService/micli.py 3-10=false")
            # 这里写你关闭 B 的代码

def on_subscribe(client, userdata, mid, granted_qos):
    print("确认：所有主题已成功订阅，设备已全部在云端上线")

client = mqtt.Client(client_id=UID)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

# 保持连接
client.connect("bemfa.com", 9501, 60)
client.loop_forever()
