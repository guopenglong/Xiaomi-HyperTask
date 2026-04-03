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
2. 创建一个 MQTT 设备云主题（建议选择 `006` 插座类型）。
   - 例如主题名为：`light001`
3. 记录下主题名，稍后填入脚本。

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
   pip install paho-mqtt miio
   ```
3. 修改配置：
   - 编辑 `HyperTask.py`，填入你的 `UID` 和 `TOPIC`。
   - 如需本地控制，编辑 `local_control.py` 填入设备的 `IP` 和 `Token`。
4. 运行脚本：
   ```bash
   python3 HyperTask.py
   ```

---

## 📂 文件说明

| 文件名 | 说明 |
| :--- | :--- |
| `HyperTask.py` | **核心监听脚本**。负责连接巴法云 MQTT，根据收到的指令执行相应逻辑。 |
| `local_control.py` | **本地控制示例**。展示如何使用 `miio` 库直接控制局域网内的米家设备。 |
| `README.md` | 项目说明文档。 |

---

## 🔗 相关资源

- [MiService](https://github.com/Yonsm/MiService) - 小米云端服务接口
- [Xiaomi-cloud-tokens-extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor) - 获取设备 Token 工具
- [python-miio](https://github.com/rytilahti/python-miio) - 控制米家设备的 Python 库

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

💡 **提示**：如果觉得好用，欢迎给个 Star ⭐！有任何问题欢迎提交 Issue。
