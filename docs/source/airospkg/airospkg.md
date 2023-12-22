## 功能概述

智路OS包支持部署在智路OS开源版本和智路OS发行版。

智路OS发行版（airos distribution）是基于智路OS的商业化版本。包括智路OS内核层、系统工具、库、软件包管理系统等的集合，符合智路OS接口标准。

airospkg是一个命令行工具，预置在集成开发环境中，提供模板**创建、编译、发布、安装、运行、删除** 等功能。

airospkg提供了便捷的组件开发能力，让开发者只关注需要开发的模块，而不需要了解整个智路OS源码，提高开发效率。

工具使用方式如下所示：

![airospkg](/image/pkg_help.png)

## 创建: create
详细参数

![create](/image/pkg_create_help.png)

创建的模板类型包括：
![type_desc](/image/type_desc.png)

使用airospkg create可以创建一个组件包模板工程，以应用为例，创建命令为：

```bash
airospkg create -name test_app -type app
```

创建的包会默认放置在/home/airos/proj目录，创建的模板包含以下文件：

```bash
|-- .bazelrc              # Bazel默认构建参数
|-- .bazelversion         # 配置bazel的版本，默认5.0.0
|-- BUILD                 # Bazel的构建脚本
|-- CMakeLists.txt        # CMake构建脚本
|-- WORKSPACE             # Bazel工作空间标识
|-- conf                  # 配置目录
|   `-- app_lib_cfg.pb    # 框架加载配置
|-- example_app.cc        # 默认源文件
|-- example_app.h         # 默认头文件
|-- lib                   # 智路OS-SDK和第三方库之外的依赖库
`-- version.txt           # 包版本
```

## 编译: make
详细参数

![make](/image/pkg_make_help.png)

工具支持CMake和Bazel编译，并且在创建时提供了基础的模板，可以在模板基础上修改或者增加。

以CMake为例：开发完成后可以调用以下命令进行编译：

```bash
airospkg make -type cmake     # 在包内运行
airospkg make -name test_app -type cmake    # 任意目录运行，确保包在/home/airos/projs下
```
`注意：需要将智路OS-SDK和第三方库之外的依赖库放置到包目录下的lib文件夹中，避免发布或者安装包后，运行出现找不到依赖库的情况。`

## 发布: release
详细参数

![release](/image/pkg_release_help.png)

编译完成后，可以使用airospkg release将包的产出进行打包发布，从而可以安装到本地，或者发布给其他使用者安装到具备智路OS的机器上。

以test_app为例：
```bash
airospkg release  # 在包内运行
airospkg release -name test_app -out app.tar.gz  # 任意目录运行，确保包在/home/airos/projs下
```
结束后会在包内生成产出包app.tar.gz

## 安装: install
详细参数

![install](/image/pkg_install_help.png)

SDK镜像支持本地安装并运行，默认安装目录为：
* 应用：/home/airos/os/app/lib
* 设备接入：/home/airos/os/device/lib
* 服务：/home/airos/os/modules/lib

以test_app为例：

```bash
airospkg install -file /home/airos/projs/test_app/app.tar.gz
```
应用包会被安装在/home/airos/os/app/lib/test_app下。

## 运行: run
详细参数

![run](/image/pkg_run_help.png)

SDK镜像支持本地运行测试

以test_app为例：

```bash
airospkg run app
```

智路OS框架会加载并且运行test_app包，可以根据输出或者日志确认是否正常运行。

![run](/image/pkg_run_res.png)

如果运行错误，请根据以下提示进行排查：
* 提示缺少库，确认打包时所有依赖已经放在lib文件夹
* 缺少符号，确认编译方式是否正确，运行日志存放在/home/airos/log文件夹
* 缺少cuda，确认环境准备是否正常

## 删除: remove
详细参数

![remove](/image/pkg_remove_help.png)

```bash
airospkg remove -name test_app
```
删除应用的安装包
