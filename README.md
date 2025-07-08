# 新房风背景生成器 - Shinbo Style Background Generator

这是一个用于生成新房昭之（Shinbo Akiyuki）动画风格背景的工具。它提供了图形用户界面（GUI）、命令行界面（CLI）和批量处理功能，可以灵活地创建和定制背景图像。

## 功能特性

- **多种操作模式**:
  - **GUI**: 通过图形界面直观地调整背景、几何图形和文字层。**注意**: GUI 版本不包含视频制作功能。
  - **CLI**: 通过命令行和 JSON 配置文件生成图像。
  - **批量生成**: 根据配置文件批量创建多个场景。
- **高度可定制**:
  - **背景**: 设置尺寸、颜色、边框和模仿新房风格的背景纹理。
  - **几何图形**: 添加和编辑圆形、矩形、三角形等多种几何形状。
  - **文字**: 支持多层文字，可自定义内容、字体、颜色、大小、方向、翻转和旋转。
- **实时预览**: 在 GUI 中可以实时看到修改后的效果。
- **多种输出选项**: 支持 PNG 和 JPEG 格式，并可以批量保存为常用尺寸。

## 项目结构

```
shaft_maker/
├── src/
│   ├── core/              # 核心图像生成逻辑
│   ├── gui/               # GUI界面组件
│   ├── batch_generator.py # 批量生成器脚本
│   ├── cli_generator.py   # 命令行生成器脚本
│   └── gui_app.py         # GUI程序入口
├── assets/                  # 存放所有素材文件 (字体, 图像, 等)
├── configs/                 # 存放 JSON 配置文件
├── scripts/                 # 存放 Shell 脚本 (.sh)
├── docs/                    # 存放项目文档和指南
├── output/                  # 默认的输出目录
├── .gitignore
├── LICENSE
└── README.md
```

## GUI 简易教程

1.  **启动程序**: 运行 `gui_app.py` 启动图形界面。
    ```bash
    python src/gui_app.py
    ```
2.  **设置背景**: 在 **背景设置** 标签页中，调整画布尺寸、背景颜色和边框。
3.  **添加文字**: 切换到 **文字设置** 标签页，点击 **新增文字层**，在弹出的窗口中输入文字内容、调整字体大小和颜色，然后保存。
4.  **预览效果**: 切换到 **预览和保存** 标签页，程序会自动生成预览图。你可以在这里缩放预览，或开启 **交互编辑模式** 直接在画布上拖拽和双击编辑文字。
5.  **保存图片**: 在 **预览和保存** 标签页中，选择你想要的格式（PNG 或 JPEG），然后点击 **保存图像**。

## 完整工作流：从图片到视频

这是一个从创建配置文件到最终生成视频的完整流程示例。

### 1. 创建批量配置文件

首先，创建一个 JSON 文件，例如 `configs/my_scenes.json`，用于定义一系列场景。你可以参考 `configs/batch_config_example.json` 来创建自己的文件。

### 2. 批量生成图片

运行 `batch_generator.py` 脚本，并指定你的配置文件和输出目录。图片序列将生成在 `output/my_video_scenes/` 目录下。

```bash
python src/batch_generator.py --config configs/my_scenes.json --output output/my_video_scenes
```

### 3. 编写 Storyboard

创建一个文本文件，例如 `configs/storyboard.txt`。这个文件定义了视频中每个场景的显示顺序和持续时间。每一行的格式是 `file '图片文件名' duration 时长（秒）`。

```
file 'output/my_video_scenes/scene_01.png'
duration 3
file 'output/my_video_scenes/scene_02.png'
duration 2.5
file 'output/my_video_scenes/scene_03.png'
duration 4
```

### 4. 生成视频

最后，运行 `make_video.sh` 脚本。它会读取 `storyboard.txt` 并使用 FFmpeg 将图片序列合成为一个名为 `storyboard_output.mp4` 的视频文件。

```bash
./scripts/make_video.sh
```

除此之外，`make_video.sh`文件还提供了别的使用方法，详情可参考文档.

## 文档

更详细的指南和说明文档已经移至 `docs/` 目录。

- **[批量生成器指南](docs/BATCH_GENERATOR_GUIDE.md)**
- **[命令行使用指南](docs/CLI_USAGE.md)**
- **[几何图形功能指南](docs/GEOMETRY_GUIDE.md)**
- **[视频制作指南](docs/VIDEO_MAKER_GUIDE.md)**

## 依赖

在运行前，请确保已安装所有必要的 Python 库：

```bash
pip install -r requirements.txt
```