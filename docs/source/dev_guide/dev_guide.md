智路OS组件开发的整体设计理念是：

- 框架提供基类及接口，开发者实现派生类
- 派生类将数据通过回调或者参数的方式传递给框架
- 框架加载组件进行运行

所有使用包管理工具创建的文件目录基本相同，以下分别是设备、应用、服务的默认包目录

![](/image/device_pkg.png) ![](/image/app_pkg.png) ![](/image/service_pkg.png)

## 1 开发

智路OS所有组件都是以继承基类的形式开发，以应用为例，其中example_app.h的内容如下所示

![](/image/app_class.png)

自定义实现的ExampleApp需要继承智路OS规定的基类AirOSApplication，并且实现Init和Start接口

框架在启动时会加载该文件编译的动态库并且调用自定义的Init和Start方法，以此实现应用在智路OS上的运行

在源文件中，需要进行模块的注册，框架会根据名称进行加载，每种组件的注册方式有区别，后续小节会详细介绍
```c++
AIROS_APPLICATION_REG_FACTORY(ExampleApp, "example_app")
```
**配置**

使用上述方式注册后，需要在conf文件夹的默认文件app_lib_cfg.pb修改注册的名称和最终编译的so的名称，使得框架能够加载
```c++
so_name: "libexample_app.so"
app_name: "example_app"
```

## 2 编译

**Bazel**

新创建的包中.bazelrc、.bazelversion、WORKSPACE、BUILD为Bazel构建相关配置，如工程使用CMake则不需要使用，构建脚本模板仅提供基础的依赖，如需修改请参考bazel官方文档

* .bazelrc：Bazel默认的构建配置，包含默认SDK的链接路径、默认链接的系统库等，相机和感知部分会增加cuda的依赖，如果实现中也使用到了cuda或者其他依赖，可以在此增加。

![](/image/bazelrc.png)

* .bazelversion： 配置bazel的版本，默认5.0.0
* BUILD：Bazel的构建脚本，需要注意以下规则：
  * 智路OS派生类的动态依赖库必须以cc_binary标签编译，否则在编译时依赖库并不寻找所有符号，导致在运行时会因符号找不到而出现问题。
  * 模板默认依赖了智路OS的SDK，其他第三方库依赖需要使用智路OS的版本，具体可以查看WORKSPACE里指定的第三方库路径
  * linkshared=True代表本规则生成动态库，linkstatic=True代表deps依赖的规则中优先以静态的方式依赖，具体使用方式参考官方文档

![](/image/bazel_build.png)

* WORKSPACE：Bazel工作空间标识，一个包为一个工作空间，标识了包的依赖路径，方便在BUILD中以@的格式进行引用

**CMake**

新创建的包中CMakeLists.txt为默认的cmake构建脚本，默认依赖了智路OS的SDK和部分第三方库供参考

![](/image/cmake_res.png)


**新增依赖库**

如果开发者需要新增SDK镜像内不存在的依赖库，需要将相应的库放置到包内的lib目录，最终才能打包发布。

如果仅安装在系统路径，即使在本机打包安装运行成功，当发布安装到其他机器会出现库缺失的情况。