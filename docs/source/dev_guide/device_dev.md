## 1 总览
### 1.1 功能

智路OS设备接入层包含信号机、RSU、Camera、Lidar设备的接入，接入模块的主要功能包括：
* 基于硬件厂商提供的设备SDK或规定的通信协议进行通信，获取数据或者写入数据。
* 将从设备中获取到的数据转换为智路OS规定的标准protobuf格式或者数据并调用框架提供的回调写入
* 将智路OS规定的标准protobuf格式数据转换为设备规定的数据格式并发送给设备

### 1.2 设计理念
车路协同系统包含多种传感器及通信设备，例如信号机、枪机、鱼眼相机、激光雷达、毫米波雷达、RSU等，各类设备与路侧边缘计算单元(RSCU)之间的协议并没有一个统一的接入标准。同种设备不同厂商可能支持不同的标准协议或者私有协议，开发者需要对各类厂商设备进行重度适配，针对标准协议的理解各厂商也存在偏差，导致数据表现存在差异。

为降低开发门槛，支持生态繁荣，智路OS定义了标准的路侧设备接入架构，为开发者提供了：

* 统一的设备接入标准协议，可自定义设备接入
* 业内广泛使用的标准接入实现，便捷复用
* 低耦合设计原则，显著简化开发、切换和升级过程

**设备接入框架**

设备接入框架基于抽象工厂设计模式实现，自定义设备接入实现相关流程如下所示：
1. 引用设备的基类头文件，该文件定义了设备的抽象基类。
2. 继承设备基类，实现自定义设备的Init等接口
3. 引用设备的工厂头文件，该文件定义了设备接入智路OS的接口
4. 在自定义设备实现的源文件中使用V2XOS_XXXX_REG_FACTORY接口注册设备
5. 在自定义实现的函数中将从设备获取的数据使用CallBack发送到智路OS框架
6. 编译时链接系统库libairos_device_pb.so和libairos_base.so
7. 将编译产出和产出描述打包并进行安装
8. 完成安装后，智路OS框架通过动态加载，调用开发者的设备具体实现

智路OS提供了包管理工具简化了以上开发流程，可以实现更便捷的开发

## 2 类说明
### 2.1 RSU
#### RSUDevice

RSU设备接入基类，开发者需要继承该类并实现对应的接口，由智路OS框架加载模块后调用。

**构造函数**
```c++
RSUDevice(const RSUCallBack& cb)
```
创建一个RSU设备接入对象，传入智路OS提供的回调，RSU设备接入可使用回调发送规定格式的数据

**Init**
```c++
bool Init(const std::string& conf_file)
```
初始化接口，在RSU设备接入初始化时调用，框架在描述文件中读取配置文件路径后传入接口，默认为绝对路径。

|name |value| describe |
|--------------|----------|----------|
| 参数         | conf_file  | 框架传入的配置文件绝对路径，在开发者具体实现中读取 |
|  返回值  | bool | 初始化正常时返回true，初始化失败时返回false |

**Start**
```c++
void Start()
```
应用主逻辑入口，理论上内部为循环数据处理

**WriteToDevice**
```c++
void WriteToDevice( const std::shared_ptr<const RSUData>& re_proto)
```
将消息写入RSU设备的接口，经过ASN.1编码后的数据通过该接口写入，最终通过RSU发送

**GetState**
```c++
RSUDeviceState GetState()
```

获取RSU设备状态接口，由上层调用，判断RSU设备状态，设备状态定义如下
```c++
enum class RSUDeviceState {
  UNKNOWN,  // 未知
  NORMAL,   // 正常
  OFFLINE   // 离线
};
```

#### RSU数据
```protobuf
message RSUData {
  required RSUDataType type = 1;    // 数据类型
  required bytes data = 2;          // ASN编码数据
  required uint64 time_stamp = 3;   // UNIX时间戳，精确到ms
  optional uint32 sequence_num = 4; // 消息序列码
  optional MessageVersion version = 5; // 版本
}
```
智路OS规定的写入RSU接入模块和RSU模块输出的数据格式，开发者在继承抽象基类RSUDevice后，调用内部的RSUCallBack将数据发送给智路OS框架，数据为从RSU接收的数据，例如BSM，智路OS框架会将需要RSU发送的数据通过WriteToDevice写入设备接入模块，接入程序解析数据并将编码后的数据发送给RSU。


### 2.2 信号灯
#### TrafficLightDevice
信号灯设备接入基类，开发者需要继承该类并实现对应的接口，由智路OS框架加载模块后调用。

**构造函数**
```c++
TrafficLightDevice(const TrafficLightCallBack& cb)
```

创建一个信号灯设备接入对象，传入智路OS提供的回调，信号灯设备接入可使用回调发送规定格式的数据

**Init**
```c++
bool Init(const std::string& conf_file)
```
初始化接口，在信号灯设备接入初始化时调用，框架在描述文件中读取配置文件路径后传入接口，默认为绝对路径。

|name |value| describe |
|--------------|----------|----------|
| 参数         | conf_file  | 框架传入的配置文件绝对路径，在开发者具体实现中读取 |
|  返回值  | bool | 初始化正常时返回true，初始化失败时返回false |

**Start**

```c++
void Start()
```
应用主逻辑入口，理论上内部为循环数据处理

**WriteToDevice**
```c++
void WriteToDevice(const std::shared_ptr<const TrafficLightReceiveData>& re_proto)
```

将消息写入信号灯设备的接口，一般为控制指令，用于上层应用对信号灯进行控制。

**GetState**
```c++
TrafficLightDeviceState GetState()
```

获取信号灯设备状态接口，由上层调用，判断信号灯设备状态，设备状态定义如下

```c++
enum class TrafficLightDeviceState { 
    UNKNOWN, 
    RUNNING, 
    STOP
};
```

#### 信号灯数据
```protobuf
message TrafficLightBaseData
{
    repeated OneLightInfo light_info_list = 1;   // 信号灯上所有灯组的步色信息列表
    required uint64 time_stamp = 2;              // UNIX时间戳，精确到ms
    optional int32 period = 3;                   // 红绿灯方案总周期（秒数）
    optional double confidence = 4;              // 置信度，取值为0和1之间的小数，0代表红绿灯信息完全不准确，1代表红绿灯信息完全准确
    optional string vendor = 5;                  // 信号机厂商
    optional string model = 6;                   // 信号机型号
    optional string software_version = 7;        // 信号机软件/固件版本
    required DataSource data_source = 8;         // 输入源类型
    required DeviceWorkState work_status = 9;    // 信号机运行状态
    required ControlMode control_mode = 10;      // 信号机控制模式
    repeated bytes original_data_list = 11;      // 信号机原始报文帧数据
    optional uint32 sequence_num = 12;           // 消息序列码
};
```

智路OS规定的信号灯接入模块输出的数据格式，开发者在继承抽象基类TrafficLightDevice后，调用内部的TrafficLightCallBack将数据发送给智路OS框架，数据为从信号机接收的实时数据。


### 2.3 Camera
#### CameraDevice
相机设备接入基类，开发者需要继承该类并实现对应的接口，由智路OS框架加载模块后调用。

**构造函数**
```c++
explicit CameraDevice(const CameraImageCallBack& cb)
```
创建一个相机设备接入对象，传入智路OS提供的回调，相机设备接入可使用回调发送规定格式的图像数据

**Init**
```c++
bool Init(const CameraInitConfig& config)
```
初始化接口，在相机设备接入初始化时调用，框架在描述文件中读取配置文件路径后传入接口

|name |value| describe |
|--------------|----------|----------|
| 参数         | config  | 框架传入的配置参数，如下所示 |
|  返回值  | bool | 初始化正常时返回true，初始化失败时返回false |

```c++
struct CameraInitConfig {
  std::string camera_name;      ///< 相机名称
  std::string camera_manufactor;///< 相机厂商
  CameraLensType lens_type;     ///< 镜头类型
  int gpu_id;                   ///< 解码设备id
  airos::base::Color img_mode;  ///< 图像模式
  std::string user;             ///< 相机登录时用户名
  std::string password;         ///< 相机登录时密码
  std::string ip;               ///< ip 地址[:端口号]
  int channel_num;              ///< 相机通道索引
  int stream_num;               ///< 相机流索引
};
```

#### 图像数据
```c++
struct CameraImageData {
  std::shared_ptr<airos::base::Image8U> image;  ///< 图片指针
  std::shared_ptr<void> gpu_ptr;
  uint32_t device_id;                           ///< 设备ID
  std::string camera_name;                      ///< 相机名称
  std::string camera_manufactor;                ///< 相机厂商
  CameraLensType lens_type;                     ///< 镜头类型
  airos::base::Color mode;                      ///< 图像模式
  uint32_t height;                              ///< 高度
  uint32_t width;                               ///< 宽度
  uint64_t timestamp;                           ///< 时间戳
  uint32_t sequence_num;                        ///< 序列号
};
```

当设备接入模块从相机获取到数据并且解码为图片后，通过CameraImageCallBack回调传入智路OS


### 2.4 Lidar
#### LidarDevice
Lidar设备接入基类，开发者需要继承该类并实现对应的接口，由智路OS框架加载模块后调用。

**构造函数**
```c++
explicit LidarDevice(const LidarCallBack& cb)
```

创建一个Lidar设备接入对象，传入智路OS提供的回调，Lidar设备接入可使用回调发送规定格式的点云数据

**Init**

```c++
bool Init(const LidarInitConfig& config)
```

初始化接口，在Lidar设备接入初始化时调用，框架在描述文件中读取配置文件路径后传入接口

|name |value| describe |
|--------------|----------|----------|
| 参数         | config  | 框架传入的配置参数，如下所示 |
|  返回值  | bool | 初始化正常时返回true，初始化失败时返回false |

```c++
struct LidarInitConfig {
  std::string lidar_name;       ///< Lidar名称
  std::string lidar_manufactor; ///< Lidar厂商
  std::string model;            ///< Lidar类型
  std::string ip;               ///< ip 地址
};
```

初始化正常时返回true，初始化失败时返回false

#### 点云数据
```protobuf
message PointCloud {
  optional LidarHeader header = 1;       // 点云数据头
  optional string frame_id = 2;          // 帧ID
  optional bool is_dense = 3;            // 是否稠密点云
  repeated PointXYZIT point = 4;         // 点云数据
  optional double measurement_time = 5;  // 测量时间
  optional uint32 width = 6;             // 宽度
  optional uint32 height = 7;            // 高度
  repeated FusionInfo fusion_info = 8;   // 融合信息
}
```
当设备接入模块从Lidar获取到点云数据后，通过LidarCallBack回调传入智路OS

## 3 开发流程
以camera开发为例，其他设备实现类似

### 3.1 代码及配置修改
**创建包**
```bash
airospkg create -name new_camera -type camera
```
**修改源文件**

![SDK List](/image/camera_src.png)

在源文件中修改接口注册信息
```c++
AIROS_CAMERA_REG_FACTORY(NewCamera, "new_camera");
```

进行编码，Init须为非阻塞实现，可以在Init中启动线程进行相机数据接收操作，解析后使用image_sender_发送图像数据。
参考[组件开发基础](/dev_guide/dev_guide.md)修改对应编译脚本。同时需要修改配置供框架加载，例如编译的动态库名为libnew_camera.so，对应的conf/device_lib_cfg.pb需要修改为:
```protobuf
so_name: "libnew_camera.so"
device_name: "new_camera"
```
`注意：需要将智路OS-SDK和第三方库之外的依赖库放置到包目录下的lib文件夹中，避免发布或者安装包后，运行出现找不到依赖库的情况。  `

### 3.2 编译及运行
```bash
airospkg make -name new_camera -type cmake  #编译
airospkg release -name new_camera -out new_camera.tar.gz  # 发布
airospkg install -file /home/airos/projs/new_camera/new_camera.tar.gz  # 安装
airospkg run -name new_camera -type camera  # 运行
```
**运行说明：**

在SDK镜像中，设备的相关参数可以查看/home/airos/param/device，具体格式参考[设备接入开发](/dev_guide/device_dev.md)中`设备公共参数`小节，开发者可以修改设备默认配置用来测试硬件设备

当包管理工具运行设备接入时，RSU和信号灯设备以进程的方式独立运行，输入正常的情况下，输出可以通过目前默认中间件cyberRT提供的工具cyber_monitor和cyber_channel查看
```bash
cyber_channel echo /airos/service/traffic_light/data # 信号灯设备输出的数据
cyber_channel echo /airos/device/rsu_out # RSU设备输出的数据
```

Camera和Lidar等传感器设备由于数据量较大，框架采用指针方式传递数据，由感知进程加载启动，因此当包管理工具运行传感器设备时会拉起感知进程进行加载

当设备输入正常的情况下，可以通过以下命令查看感知的输出
```bash
cyber_channel echo /airos/perception/obstacles_camera1 # 相机感知处理后的结构化数据
cyber_channel echo /airos/lidar/obstacles_lidar1 # 雷达感知处理后的结构化数据
```

## 4 设备公共参数

公共参数配置了每个路口的RSU、信号灯、相机、Lidar等设备的参数，在自定义实现中可以读取设备参数进行设备连接，智路OS会在调用Init接口时传入参数路径或结构数据。

目前的SDK镜像中默认存放了对应的参数，默认路径为/home/airos/param/device

在编码中推荐使用airos::base::Environment::GetPublicParamPath()接口获得公共参数路径

### 4.1 RSU设备参数
RSU设备参数为yaml格式，具体描述如下
```yaml
ip: 127.0.0.1         # RSU设备IP
port: 8888            # RSU设备端口
local_ip: 127.0.0.1   # RSCU IP
local_port: 11262     # RSCU发送端口
version: 3            # 协议版本,三跨:1,四跨:2,新四跨:3
```
### 4.2 信号灯设备参数
信号灯设备参数为yaml格式，具体描述如下
```yaml
ip: 10.128.159.51     # 信号灯设备IP
port: 8384            # 信号灯设备端口
local_port: 6000      # RSCU发送端口
```
### 4.3 相机设备参数
相机设备参数存放位置为param/device/camera/camera.yaml，格式如下，描述了相机的基本信息
```yaml
camera1:
  ip: 10.128.71.101           // 连接IP
  user: admin                 // 连接用户名
  password: xxx               // 连接密码
  camera_manufactor: simulation_camera    // 注册名称/厂商
  lens_type: PinholeLens      // 镜头类型
  img_mode: BGR               // 图像模式
```
param/device/camera下还保存了默认的相机的标定参数，用于感知2D转3D时使用

相机内参：camera1_intrinsics.yaml

相机外参：camera2_extrinsics.yaml

接地点坐标：camera1_coffe_ground.yaml

### 4.4 Lidar设备参数
框架传入的Lidar设备参数为结构体的形式，如2.2.4小节中描述。
Lidar设备参数存放位置为param/device/lidar/lidar.yaml，格式如下，描述了Lidar的基本信息
```yaml
lidar1:
  ip: 192.168.10.150
  lidar_manufactor: dummy_lidar
  model: rev_e
```
param/device/lidar下还保存了默认的Lidar的标定参数lidar1_extrinsics.yaml
