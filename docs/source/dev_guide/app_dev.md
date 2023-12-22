## 1 总览
### 1.1 功能

智路OS的应用基于框架提供的服务数据，实现场景理解、指标计算、V2X核心功能实现，应用包括但不限于：

* V2X应用场景实现
* 交通事件检测
* 交通流指标计算
* 系统监控
* 路径规划控制

开发者可以基于智路OS框架和数据，实现自定义的应用。

### 1.2 设计理念

在车路协同系统中，应用是高度自定义的模块，智路OS提供的特性包括：

* 自定义应用可以按照标准流程注册到智路OS中
* 智路OS应用框架支持多个应用同时运行，每个应用为单独的进程调度，互不影响
* 应用可订阅多种服务数据进行业务处理，并且可以使用任意协议与云端通信
* 智路OS提供了两种标准的应用输出格式，经过RSU发送给OBU的数据定义、发送到标准云控平台的数据定义，组装消息并且调用发送回调即可实现。输出到车的数据为标准格式消息，即《合作式智能运输系统 车用通信系统应用层及应用数据交互标准》系列标准规定的格式，输出到云的格式基于《智能网联汽车云控系统 第3部分 路云数据交互规范》

## 2 类说明

### Application

**AirOSApplication**

应用的基类，开发者需要继承该类并实现对应的接口，由智路OS框架加载模块后调用。

**构造函数**
```c++
AirOSApplication(const ApplicationCallBack& cb)
```
创建一个应用对象，传入智路OS提供的回调，应用可使用回调发送规定格式的数据

**Init**
```c++
bool Init(const AppliactionConfig& conf)
```
初始化接口，在应用初始化时调用，框架在描述文件中读取配置文件相对路径，增加前缀路径后传入接口。

|name |value| describe |
|--------------|----------|----------|
| 参数         | conf  | 框架传入的配置，在开发者具体实现中读取，如下所示 |
|  返回值  | bool | 初始化正常时返回true，初始化失败时返回false |

```protobuf
message AppliactionConfig {
  optional string app_name = 1;      // app名字
  optional string app_package_path = 2; // app安装路径
  optional string app_config_path = 3;  // app配置文件路径
}
```

**Start**
```c++
void Start()
```
应用主逻辑入口，理论上内部为循环数据处理，如果无相关需求可以直接返回，应用仍持续运行。

### 应用数据
```protobuf
message ApplicationData {
  oneof payload {
    v2xpb.asn.MessageFrame road_side_frame = 1;
    airos.cloud.CloudFrame cloud_message_frame = 2;
  }
}
```

智路OS规定的应用输出数据，发送给路侧通信设备或者发送给云端平台。其中，v2xpb.asn.MessageFrame为V2X标准消息对应的protobuf格式，airos.cloud.CloudFrame为根据路云数据交互规范标准制定的protobuf格式，

开发者在继承抽象基类AirOSApplication后，调用内部的ApplicationCallBack将数据发送给智路OS框架，框架根据相应数据类型转发给路侧通信设备或者云端平台。

## 3 开发流程
### 3.1 代码及配置修改
**创建包**
```bash
airospkg create -name new_app -type app
```
修改源文件

![](/image/app_src.png)

在源文件中修改接口注册信息
```c++
AIROS_APPLICATION_REG_FACTORY(NewApp, "new_app")
```

进行编码，开发相关规则如下：

* Init须为非阻塞实现，Start可以是阻塞或者非阻塞实现
* 通过app_middleware.h提供的RegisterOSMessage接口，可以订阅来自智路OS框架的消息，具体可以参考开源组件代码
* 接收到数据进行处理后，可以使用sender_发送数据
* sender_中填充标准V2X数据后会通过智路OS协议栈发送到RSU设备，进而发送给安装OBU设备的车辆
* sender_中填充定义的云端数据会通过标准协议发送给默认的云控平台

参考[组件开发基础](/dev_guide/dev_guide.md)修改对应编译脚本。同时需要修改配置供框架加载，例如编译的动态库名为libnew_app.so，对应的conf/app_lib_cfg.pb需要修改为
```protobuf
so_name: "libnew_app.so"
app_name: "new_app"
```
`注意：需要将智路OS-SDK和第三方库之外的依赖库放置到包目录下的lib文件夹中，避免发布或者安装包后，运行出现找不到依赖库的情况。`

### 3.2 编译及运行
```bash
airospkg make -name new_app -type cmake  #编译
airospkg release -name new_app -out new_app.tar.gz  # 发布
airospkg install -file /home/airos/projs/new_app/new_app.tar.gz  # 安装
airospkg run -name new_app -type app  # 运行
```