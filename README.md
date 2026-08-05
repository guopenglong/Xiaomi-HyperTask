# 🚗 Xiaomi-HyperTask

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![MQTT](https://img.shields.io/badge/Protocol-MQTT-orange.svg)](http://mqtt.org/)
[![Xiaomi](https://img.shields.io/badge/Platform-Xiaomi%20HyperOS-green.svg)](https://www.mi.com/)
[![Bemfa](https://img.shields.io/badge/Cloud-Bemfa-blue.svg)](https://cloud.bemfa.com/)

**Xiaomi-HyperTask** 是一个专为小米汽车用户设计的自动化扩展方案。通过本项目，你可以利用小米汽车的“超级任务”功能，远程触发执行自定义 Python 脚本，从而实现对米家设备、本地 NAS 任务或任何云端服务的深度控制。

---

## 🌟 核心功能

- **自定义脚本触发**：在车机端一键运行服务器/NAS 上的 Python 脚本（如：进京证自动续签、自动化签到等）。
- **跨平台设备联动**：通过巴法云（Bemfa）作为中转，打破米家生态限制，实现更复杂的控制逻辑。
- **本地/云端双模式**：
  - **本地控制**：基于 `python-miio` 直接操作局域网内的米家设备（低延迟）。
  - **云端控制**：集成 `MiService` 实现远程跨地域设备操控。

---

## 🛠️ 工作原理

本项目通过一套巧妙的链路，将车机端的指令传递至你的执行终端：

1. **车机端**：触发“超级任务”（手动执行）。
2. **米家 App**：执行手动任务，向小爱音箱发送“自定义指令”。
3. **小爱音箱**：通过“小爱训练”触发绑定的**巴法云**虚拟设备。
4. **巴法云**：通过 MQTT 协议将指令推送至你的服务器。
5. **执行终端**：`HyperTask.py` 接收指令并运行对应的 Python 逻辑。

---

## 🚀 快速开始

### 1. 环境准备
- 一台可运行 Python 的服务器或本地 NAS（如群晖、威联通）。
- 小爱音箱（用于指令中转）。
- [巴法云](https://cloud.bemfa.com/) 账号。

### 2. 巴法云配置
1. 注册并登录巴法云，获取你的 **UID**。
2. 创建一个或多个 MQTT 设备云主题（建议选择 `006` 插座类型）。
   - 例如主题名为：`light_control`、`auto_checkin` 等。
3. 记录下主题名，稍后填入 `HyperTask.py` 脚本。

### 3. 米家与小爱配置
1. **同步设备**：在米家 App 中点击 `我的` -> `连接第三方平台` -> `添加巴法`，同步你的虚拟设备。
2. **小爱训练**：
   - 打开小爱音箱 App -> `小爱训练` -> `个人训练`。
   - 添加说法：“执行超级任务”（或其他关键词）。
   - 添加操作：选择刚才同步的巴法云设备，设置为“开启”。
3. **创建手动任务**：
   - 在米家 App 创建手动执行场景。
   - 动作选择：`小爱音箱` -> `自定义指令` -> 输入“执行超级任务” -> 选择`静默执行`。
4. **车机同步**：在小米汽车超级任务中同步该手动任务即可。

### 4. 脚本部署
1. 克隆本项目：
   ```bash
   git clone https://github.com/guopenglong/Xiaomi-HyperTask.git
   cd Xiaomi-HyperTask
   ```
2. 安装依赖：
   ```bash
   pip install paho-mqtt python-miio requests qrcode
   ```
3. **修改配置 (重要!)**：
   - **`HyperTask.py`**: 
     - 将 `BEMFA_UID` 替换为你的巴法云 UID。
     - 修改 `TOPICS` 列表，填入你在巴法云创建的主题名。你可以配置多个主题，并在 `on_message` 函数中根据 `topic` 分发不同的任务逻辑。
     - 在 `handle_task_1` 和 `handle_task_2` 函数中，根据你的需求编写或调用实际的 Python 脚本或命令。
   - **`xiaomi_qr_miot.py`**: 
     - 通过python xiaomi_qr_miot.py devices 执行后扫码登录 获取你的设备did。
     - `siid` 和 `piid` 参数需要根据你的具体设备型号进行调整，可以通过 `miiocli device --ip <IP> --token <TOKEN> info` 命令获取设备服务信息。
    脚本介绍
    
## 1. 扫码登录

首次使用先登录：

```bash
python xiaomi_qr_miot.py login
```

执行后会：

1. 请求二维码
2. 终端显示二维码或登录链接
3. 用小米汽车 App 扫码
4. 自动保存登录 token

如果你想忽略本地 token，强制重新扫码：

```bash
python xiaomi_qr_miot.py --force-qr login
```

---

## 2. 查询设备列表

查询当前账号下的设备：

```bash
python xiaomi_qr_miot.py devices
```

按名字过滤：

```bash
python xiaomi_qr_miot.py devices --name 台灯
```

输出完整原始设备信息：

```bash
python xiaomi_qr_miot.py devices --full
```

指定区域：

```bash
python xiaomi_qr_miot.py devices --region cn
```

返回里通常会看到：

- `name`
- `model`
- `did`
- `token`

其中后续读写属性最重要的是：

- `did`

---

## 3. 读取属性

### 用 `iid` 方式

```bash
python xiaomi_qr_miot.py get --did 123456789 --iid 2-1
```

这里：

- `2` = `siid`
- `1` = `piid`

### 用 `siid/piid` 方式

```bash
python xiaomi_qr_miot.py get --did 123456789 --siid 2 --piid 1
```

---

## 4. 设置属性

### 用 `iid` 方式

```bash
python xiaomi_qr_miot.py set --did 123456789 --iid 2-1 --value 60
```

### 用 `siid/piid` 方式

```bash
python xiaomi_qr_miot.py set --did 123456789 --siid 2 --piid 1 --value 60
```

---

## 5. value 参数说明

`--value` 默认会优先按 JSON 解析，所以这些都可以：

数字：

```bash
python xiaomi_qr_miot.py set --did 123456789 --iid 2-1 --value 1
```

布尔值：

```bash
python xiaomi_qr_miot.py set --did 123456789 --iid 2-1 --value true
```

字符串：

```bash
python xiaomi_qr_miot.py set --did 123456789 --iid 2-1 --value '"auto"'
```

如果不是合法 JSON，会按普通字符串处理。

---

## 6. 自动刷新登录态

脚本会优先复用本地 token。

如果请求时发现登录态失效，会自动按顺序尝试：

1. 用本地 `passToken` 刷新 `xiaomiio` token
2. 如果还不行，重新扫码登录

所以一般不需要手工删 token 文件。

---

## 7. 常见使用流程

### 第一步：扫码登录

```bash
python xiaomi_qr_miot.py login
```

### 第二步：查设备 DID

```bash
python xiaomi_qr_miot.py devices
```

### 第三步：读取属性

```bash
python xiaomi_qr_miot.py get --did 123456789 --iid 2-1
```

### 第四步：设置属性

```bash
python xiaomi_qr_miot.py set --did 123456789 --iid 2-1 --value 60
```

---
4. 运行 `HyperTask.py` 脚本：
   ```bash
   python3 HyperTask.py
   ```
   该脚本将持续监听巴法云 MQTT 消息，并在收到指令时执行相应的任务。

---

## 📂 文件说明

| 文件名 | 说明 |
| :--- | :--- |
| `HyperTask.py` | **核心 MQTT 监听脚本**。连接巴法云，接收来自小米汽车的指令，并根据主题分发执行预设的 Python 任务逻辑。这是一个高度可配置的模板，用户需根据自身需求修改 `BEMFA_UID`、`TOPICS` 以及 `handle_task_x` 函数中的具体实现。 |
| `xiaomi_qr_miot.py` | **米家设备云端控制脚本**。演示如何使用 `python-miio` 库直接在局域网内控制米家设备。用户需填入 `DEVICE_IP` 和 `DEVICE_TOKEN`，并根据设备类型调整 `siid` 和 `piid` 参数。 |
| `README.md` | 项目说明文档。 |
| `LICENSE` | 项目开源许可证。 |

---

## 🔗 相关资源

- [MiService](https://github.com/Yonsm/MiService) - 小米云端服务接口 (可用于 `HyperTask.py` 中的云端控制逻辑)
- [Xiaomi-cloud-tokens-extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor) - 获取米家设备 Token 工具
- [python-miio](https://github.com/rytilahti/python-miio) - 控制米家设备的 Python 库 (用于 `local_control.py`)

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

💡 **提示**：如果觉得好用，欢迎给个 Star ⭐！有任何问题欢迎提交 Issue。
