# 新房风格背景生成器 - 命令行版本

这个工具允许您通过命令行使用JSON配置文件或Python字典来生成新房风格的背景图片，无需启动GUI界面。

## 快速开始

### 1. 生成示例配置文件

```bash
python cli_generator.py --example
```

这将创建一个 `example_config.json` 文件，包含完整的配置示例。

### 2. 使用配置文件生成图片

```bash
python cli_generator.py --config example_config.json
```

### 3. 指定输出路径

```bash
python cli_generator.py --config my_config.json --output my_image.png
```

## 命令行参数

- `--config, -c`: JSON配置文件路径 (必需)
- `--output, -o`: 输出图片路径 (可选，会覆盖配置文件中的路径)
- `--example`: 生成示例配置文件
- `--example-output`: 指定示例配置文件的输出路径 (默认: example_config.json)

## JSON配置格式

```json
{
  "background": {
    "width": 1920,           // 图片宽度
    "height": 1080,          // 图片高度
    "main_color": "#000000", // 主背景色
    "border_color": "#FFFFFF", // 边框颜色
    "border_height": 50      // 边框高度
  },
  "lines": {
    "enabled": true,         // 是否启用横线效果
    "opacity": 30,           // 横线透明度 (0-100)
    "color": "#666666",      // 横线颜色
    "spacing": 3             // 横线间距
  },
  "text_layers": [
    {
      "content": "新房风格",           // 文字内容
      "size": 80,                   // 字体大小
      "color": "#FFFFFF",           // 文字颜色
      "font_path": "fonts/Songti.ttc", // 字体文件路径
      "x_offset": 0,                // X轴偏移
      "y_offset": -100,             // Y轴偏移
      "direction": "水平 (左→右)",   // 文字方向
      "flip": "无",                 // 翻转方式
      "rotation": "0°"              // 旋转角度
    }
  ],
  "output_path": "output/example.png"  // 输出文件路径
}
```

## 文字方向选项

- `"水平 (左→右)"`: 标准水平文字
- `"垂直 (上→下)"`: 垂直排列文字
- `"水平 (右→左)"`: 从右到左的水平文字

## 翻转选项

- `"无"`: 不翻转
- `"水平翻转"`: 水平镜像
- `"垂直翻转"`: 垂直镜像
- `"水平+垂直翻转"`: 同时水平和垂直翻转

## 旋转角度选项

- `"0°"`, `"45°"`, `"90°"`, `"135°"`, `"180°"`, `"225°"`, `"270°"`, `"315°"`

## Python代码中使用

您也可以在Python代码中直接调用生成函数：

```python
from cli_generator import generate_image_from_config, generate_image_from_json

# 使用字典配置
config = {
    "background": {
        "width": 1920,
        "height": 1080,
        "main_color": "#000000"
    },
    "text_layers": [
        {
            "content": "Hello World",
            "size": 60,
            "color": "#FFFFFF",
            "x_offset": 0,
            "y_offset": 0
        }
    ]
}

# 生成图片
image = generate_image_from_config(config, "output.png")

# 或者从JSON文件
image = generate_image_from_json("config.json", "output.png")
```

## 支持的输出格式

- PNG (推荐，支持透明度)
- JPEG/JPG (不支持透明度，会自动转换为白色背景)

## 示例用法

### 创建简单的标题图

```bash
# 1. 生成基础配置
python cli_generator.py --example --example-output title_config.json

# 2. 编辑 title_config.json 文件，修改文字内容

# 3. 生成图片
python cli_generator.py --config title_config.json --output title.png
```

### 批量生成不同尺寸

您可以创建多个配置文件，分别设置不同的尺寸：

```json
// config_1080p.json
{"background": {"width": 1920, "height": 1080}, ...}

// config_4k.json  
{"background": {"width": 3840, "height": 2160}, ...}

// config_square.json
{"background": {"width": 1080, "height": 1080}, ...}
```

然后批量生成：

```bash
python cli_generator.py --config config_1080p.json --output image_1080p.png
python cli_generator.py --config config_4k.json --output image_4k.png
python cli_generator.py --config config_square.json --output image_square.png
```

## 注意事项

1. 确保字体文件路径正确，推荐使用项目内的 `fonts/` 目录下的字体
2. 输出目录会自动创建，无需手动创建
3. 如果配置文件中已指定输出路径，可以不使用 `--output` 参数
4. JSON文件必须使用UTF-8编码以正确显示中文字符

## 错误处理

- 如果JSON格式错误，会显示具体的错误信息
- 如果字体文件不存在，会自动使用系统默认字体
- 如果输出目录不存在，会自动创建 