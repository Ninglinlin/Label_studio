# 🔍 在Label Studio 标注工具中接入多模态大模型，用于图片数据的自动标注（Windows）

本项目用于在 Windows 系统中，通过 Label Studio 接入多模态大模型（如 Doubao），对图片内容进行智能标注。适用于需要批量处理图像数据的标注任务，支持配置模板与本地 HTTP 服务。

## 📦 项目功能

- 接入 Doubao 多模态大模型，实现自动图像理解与标注
- 基于 Label Studio 提供可视化标注界面
- 支持本地 HTTP 服务读取图片文件夹内容
- 模板化配置，快速部署

## 🛠️ 环境准备

在开始之前，请确保以下环境和配置已完成：

1. 已安装并配置好 [Label Studio](https://labelstud.io/)
2. 已获取并配置 Doubao 大模型相关的许可与密钥  
   👉 请参考火山引擎官方文档完成模型接入与鉴权设置

## 📁 文件说明

| 文件名                     | 说明                                                                 |
|--------------------------|----------------------------------------------------------------------|
| `label_studio_template.xml` | Label Studio 的任务模板文件，用于定义标注界面与数据结构               |
| `http_server.py`           | 本地 HTTP 服务脚本，用于读取待标注图片所在文件夹                      |
| `Label_studio_start.bat`   | 启动 Label Studio 的批处理脚本，自动加载配置并运行服务                |

## 🚀 使用步骤

1. **配置模型与服务密钥**  
   按照火山引擎文档，完成 Doubao 模型的接入与鉴权设置

2. **设置模板文件**  
   在 Label Studio 项目中，将 `label_studio_template.xml` 作为任务模板导入

3. **放置 HTTP 服务脚本**  
   将 `http_server.py` 放置在与待标注图片文件夹同一级目录下  
   例如：  
   - 图片路径：`D:\datasets\data\images.jpg`  
   - 脚本路径：`D:\datasets\http_server.py`

4. **启动服务**  
   双击运行 `Label_studio_start.bat`，启动标注服务并加载配置

## 📌 注意事项

- 请确保图片文件夹路径中不包含中文或特殊字符，以避免编码问题
- 推荐使用 Python 3.8+ 环境运行 `http_server.py`
- 若遇到端口冲突，请修改 `http_server.py` 中的端口号配置

## 📄 许可证

本项目遵循 MIT License
