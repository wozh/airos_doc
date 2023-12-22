## 1 总览
### 1.1 功能

感知服务包含感知的整体pipeline，主要模块包括单相机感知和融合。

**单相机感知模块**

主要功能为接收IP相机RTSP视频流，解码成RGB图片，通过算法识别出视频中的障碍物，并转换到世界坐标系。智路OS提供了基础的单相机感知组件，包括2D检测、2D跟踪、RoI过滤、回3D。

* **检测：**
利用深度学习算法，识别出物体类别/2D框/长宽高/朝向角/底面中心点图像坐标等信息。
* **RoI过滤：**
主要功能是过滤掉感兴趣区域外的物体．
* **2D跟踪：**
主要任务是给定一个图像序列，找到图像序列中运动的物体，识别不同帧的同一个运动物体，给定一个确定准确的ID
* **回3D：**
根据模型预测的图像坐标系下的底面中心点的图像坐标(u,v)，利用地面方程和相机内参计算得到相机坐标系下的底面中心点的3D坐标(X, Y, Z)，利用模型预测得到的物体高度h，计算得到物体中心点在相机坐标系下的3D坐标。

**多传感器融合模块**

主要功能是接收多个传感器（相机或雷达）识别处理的结构化数据，对目标进行融合，从而提供更全面、准确的环境感知。智路OS提供了基础的多传感器融合组件实现。

* 融合关联部分基于概率分布模型来建立关联矩阵，对于关联融合所需的所有维度的信息（障碍物位置、类别、尺寸、车道信息、轨迹等），通过其概率分布来得到融合概率分布
* 3D跟踪，一般采用时间和空间相结合的卡尔曼滤波，对同一物体，不同传感器不同时刻的观测值进行滤波跟踪，进一步提升融合精度，开发者可自行实现。

### 1.2 设计理念
智路OS中，感知服务相关的组件可以由开发者自定实现并升级替换，框架提供了模块相关的抽象类、接口、注册方式，开发者需要根据定义标准实现功能开发并接入智路OS。

**单相机检测模块**

对于单相机检测模块，智路OS框架提供的输入是从camera视频解码的实时RGB图像数据，模块的输出为智路OS定义的感知障碍物结构化数据，单相机检测模块内部的算法和pipeline可以由开发者自定义。

**多传感器融合模块**

对于多传感器融合模块，智路OS框架提供的输入是多个传感器检测的感知障碍物结构化数据，模块的输出为智路OS定义的感知障碍物融合结构化数据，内部的相关的算法可以由开发者自定义。

## 2 类说明
### 2.1 Camera Perception
#### BaseCameraPerception
单相机感知的基类，开发者需要继承该类并实现对应的接口，由智路OS框架加载模块后调用。

**Init**
```c++
bool Init(const CameraPerceptionParam &param)
```
初始化接口，在单相机感知模块初始化时调用，框架在相机配置文件中读取框架配置后，传给开发者的算法使用。

|name |value| describe |
|--------------|----------|----------|
| 参数         | param  | 框架传入的配置文件结构，定义如下 |
|  返回值  | bool | 初始化正常时返回true，初始化失败时返回false |

```c++
struct CameraPerceptionParam {
  std::string camera_name;    // 相机名称
  std::string sdk_path;       // 算法SDK路径
  std::string conf_path;      // 参数路径
  unsigned int gpu_id = 0;
};
```

**Perception**
```c++
bool Perception(const base::device::CameraImageData &camera_data, PerceptionObstacles *result,TrafficLightDetection *traffic_light)
```
单相机感知主逻辑接口，输入为图像数据，输出为感知处理后的结构化数据，包含障碍物信息和视觉检测的信号灯信息，如果不提供信号灯检测能力，可以置为空。

**Name**
```c++
std::string Name()
```
获取模块的名称

#### 组件输入
```c++
struct CameraImageData {
  std::shared_ptr<airos::base::Image8U> image;  ///< 图片指针
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

智路OS规定的传入感知组件的数据格式，开发者实现Perception接口时，根据传入的图像指针和其他信息进行2D目标检测、跟踪等处理最终输出感知数据。

#### 组件输出
相机感知组件输出的结构化数据

PerceptionObstacles
```protobuf
// airos_perception_obstacle.proto
message PerceptionObstacles {
    repeated PerceptionObstacle perception_obstacle = 1;  // An array of obstacles
    optional airos.header.Header header = 2;         // Header
    optional PerceptionErrorCode error_code = 3 [default = ERROR_NONE]; //Error code
    repeated PerceptionObstacle unobserved_obstacle = 4;
}
```
TrafficLightDetection
```protobuf
// airos_visual_traffic_light.proto
message TrafficLightDetection {
    repeated TrafficLightByDirection traffic_light_by_direction = 1;
    repeated TrafficLightByDirection traffic_light_by_projection = 2;
    repeated TrafficLightByDirection traffic_light_by_detection = 3;
}
```

### 2.2 Lidar Perception
#### BaseLidarPerception

Lidar感知的基类，开发者需要继承该类并实现对应的接口，由智路OS框架加载模块后调用。

**Init**
```c++
bool Init(const LidarPerceptionParam &param)
```
初始化接口，在Lidar感知模块初始化时调用，框架在Lidar配置文件中读取框架配置后，传给开发者的算法使用。

|name |value| describe |
|--------------|----------|----------|
| 参数         | param  | 框架传入的配置文件结构，定义如下 |
| 返回值  | bool | 初始化正常时返回true，初始化失败时返回false |

```c++
struct LidarPerceptionParam {
  std::string lidar_name;    // Lidar名称
  std::string alg_path;      // 算法SDK路径
  std::string conf_path;     // 参数路径
};
```
**Perception**
```c++
bool Perception(const LidarPonitCloud &lidar_data, PerceptionObstacles *result)
```
Lidar感知主逻辑接口，输入为点云数据，输出为感知处理后的结构化障碍物信息

**Name**
```c++
std::string Name()
```

获取模块的名称

#### 组件输入
PointCloud
```protobuf
// lidar_data.proto
message PointCloud {
  optional LidarHeader header = 1;
  optional string frame_id = 2;
  optional bool is_dense = 3;
  repeated PointXYZIT point = 4;
  optional double measurement_time = 5;
  optional uint32 width = 6;
  optional uint32 height = 7;
  repeated FusionInfo fusion_info = 8;
}
```
智路OS规定的传入Lidar感知的数据格式，开发者实现Perception接口时，根据传入的点云进行目标检测、跟踪等处理最终输出感知数据。
#### 组件输出
Lidar感知组件输出的结构化数据

PerceptionObstacles
```protobuf
// airos_perception_obstacle.proto
message PerceptionObstacles {
    repeated PerceptionObstacle perception_obstacle = 1;  // An array of obstacles
    optional airos.header.Header header = 2;         // Header
    optional PerceptionErrorCode error_code = 3 [default = ERROR_NONE]; //Error code
    repeated PerceptionObstacle unobserved_obstacle = 4;
}
```

### 2.3 Fusion
#### BasePerceptionFusion
感知融合基类，开发者需要继承该类并实现对应的接口，由智路OS框架加载模块后调用。
**Init**
```c++
bool Init(const PerceptionFusionParam &param)
```
初始化接口，在融合模块初始化时调用，框架在相机配置文件中读取自定义配置后，传给开发者的算法使用。

|name |value| describe |
|--------------|----------|----------|
| 参数         | param  | 框架传入的配置文件结构，定义如下 |
| 返回值  | bool | 初始化正常时返回true，初始化失败时返回false |

```protobuf
message PerceptionFusionParam {
    repeated SingleInput input = 1;
    required string perception_channel = 2 [default = "/airos/perception_obstacles"];
    optional double output_frequency = 3 [default = 15.0];
    optional int32 viz_mode = 4 [default = 0];
    optional string node_name = 5 [default = "v2x_msf_roadside"];
    optional string alg_name = 6;
    optional string alg_path = 7;
    optional string conf_path = 8;
}
```

**Process**
```c++
bool Process( const std::vector<std::shared_ptr<const PerceptionObstacles>> &input, PerceptionObstacles *result)
```
融合主逻辑接口，输入为多个传感器感知处理后的结构化数据，输出为融合后的结构化数据。

**Name**
```c++
std::string Name()
```
获取模块的名称

#### 组件输入
感知融合组件输入的结构化数据，由相机感知或者Lidar感知输出

PerceptionObstacles
```protobuf
// airos_perception_obstacle.proto
message PerceptionObstacles {
    repeated PerceptionObstacle perception_obstacle = 1;  // An array of obstacles
    optional airos.header.Header header = 2;         // Header
    optional PerceptionErrorCode error_code = 3 [default = ERROR_NONE]; //Error code
    repeated PerceptionObstacle unobserved_obstacle = 4;
}
```

#### 组件输出
感知融合组件输出的结构化数据与输入结构相同，为PerceptionObstacles结构数据

## 3 开发流程
### 3.1 代码及配置修改
**创建包**
```bash
airospkg create -name new_lidar_perception -type lidar_perception
```
修改源文件

![](/image/lidar_src.png)

在源文件中修改接口注册信息
```c++
REGISTER_LIDAR_PERCEPTION(NewPerceptionLidar);
```
进行编码，Init和Perception须为非阻塞实现
参考[组件开发基础](/dev_guide/dev_guide.md)修改对应编译脚本。同时需要修改配置供框架加载，例如编译的动态库名为libnew_perception_lidar.so，对应的conf/dynamic_module.cfg需要修改为

```protobuf
lib_name : "libnew_perception_lidar.so"
module_type : "BaseLidarPerception"
module_name : "NewPerceptionLidar"
```

`注意：需要将智路OS-SDK和第三方库之外的依赖库放置到包目录下的lib文件夹中，避免发布或者安装包后，运行出现找不到依赖库的情况。`

### 3.2 编译及运行
```bash
airospkg make -name new_lidar_perception -type cmake  #编译
airospkg release -name new_lidar_perception -out new_lidar_perception.tar.gz  # 发布
airospkg install -file /home/airos/projs/new_lidar_perception/new_lidar_perception.tar.gz  # 安装
airospkg run -name new_lidar_perception -type lidar_perception  # 运行
```