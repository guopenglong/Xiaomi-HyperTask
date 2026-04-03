# Xiaomi-HyperTask
 This helps users execute custom Python scripts to operate Mi Home devices using Xiaomi Car Super Task.
前提条件  1.可以执行 python 脚本的环境服务器或者本地 NAS 2. 小爱音箱
 借助巴法云平台可以实现小米汽车超级任务执行 python 脚本 操作米家设备等等也可以控制底盘氛围灯
HyperTask.py中TOPIC1 是使用执行python脚本
HyperTask.py中TOPIC2 是我使用MiService来执行远端控制
首先要注册个巴法云平台账号获取到UID 然后创建MQTT 设备云 我这里选择的是 006 的插座 也可以选其他的自测 创建后会有TOPIC name 填到HyperTask.py脚本中就行
创建之后在米家添加设备-> 连接第三方平台->巴法->同步设备
因米家限制 就算同步后设备也无法 在米家页面也无法看到 所以需要借助到小爱音箱
在小爱音箱里全部功能->小爱训练->个人训练-> 添加说法写关键词“打开 xxx 的灯” 然后添加操作就可以看到刚刚的巴法云的设备 打开可以对应打开开关  同理可以创建关闭 xxx 的灯
然后在米家创建手动控制 选择家居设备 小爱音箱自定义指令 这里指令填写上一步 关键词“打开 xxx 的灯” 选择静默执行 然后保存就可以了 这个时候米家首页就有“打开 xxx 灯”的手动控制
在小米汽车上同步该手动操作即可
 如果要操作云端米家设备 需要使用[MiService](https://github.com/Yonsm/MiService)（云端操控比较复杂）
 如果要操作局域网米家设备 直接使用local_control.py 即可（需要通过[Xiaomi-cloud-tokens-extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor) 获取DEVICE_IP，DEVICE_TOKEN）
