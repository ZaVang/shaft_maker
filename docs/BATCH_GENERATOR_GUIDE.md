# 批量场景生成器使用指南

## 概述

批量场景生成器 (`batch_generator.py`) 是基于 `cli_generator.py` 开发的工具，专门用于批量生成多个相关场景的新房风格背景图片。它特别适合制作动漫、小说插图或一系列相关的视觉内容。

## 快速开始

### 1. 生成示例配置

```bash
python src/batch_generator.py --example
```

这将创建 `batch_config_example.json` 文件。

### 2. 使用配置文件批量生成

```bash
python src/batch_generator.py -c monogatari_scenes.json -o output/test
```

## 配置文件格式

### 基本结构

```json
{
  "base_template": {
    "width": 1280,
    "height": 720,
    "border_height": 50,
    "line_density": 3,
    "line_opacity": 0.3
  },
  "scenes": [
    {
      "name": "scene_01",
      "background_color": "#2c1810",
      "border_color": "#8b4513", 
      "line_color": "#d2b48c",
      "text_layers": [...]
    }
  ]
}
```

### base_template 配置

- `width/height`: 图片尺寸
- `border_height`: 上下边框高度
- `line_density`: 横线密度（对应GUI中的spacing）
- `line_opacity`: 横线透明度（0.0-1.0，对应GUI中的0-100%）

### scenes 配置

每个场景包含：
- `name`: 场景名称（用作文件名）
- `background_color`: 背景颜色
- `border_color`: 边框颜色  
- `line_color`: 横线颜色
- `text_layers`: 文字层数组

### text_layers 配置

```json
{
  "text": "文字内容",
  "size": 40,
  "color": "#FFFFFF",
  "font_path": "fonts/Songti.ttc",
  "x_offset": 0,
  "y_offset": -100,
  "direction": "horizontal_lr",
  "flip": "none", 
  "rotation": 0
}
```

**方向选项**:
- `horizontal_lr` / `horizontal_ltr`: 水平（左→右）
- `horizontal_rl` / `horizontal_rtl`: 水平（右→左）
- `vertical`: 垂直（上→下）

**翻转选项**:
- `none`: 无翻转
- `horizontal`: 水平翻转
- `vertical`: 垂直翻转
- `both`: 水平+垂直翻转

**旋转**: 0-360度的数值

## 命令行参数

```bash
python batch_generator.py [options]
```

- `--config, -c`: 配置文件路径（必需）
- `--output, -o`: 输出目录（默认: batch_scenes）
- `--example`: 生成示例配置文件
- `--example-output`: 示例配置文件路径（默认: batch_config_example.json）

## 使用示例

### 生成《物语》场景

```bash
# 使用提供的物语配置
python batch_generator.py --config monogatari_scenes.json --output monogatari_scenes
```

### 创建自定义场景

```bash
# 1. 生成基础配置模板
python batch_generator.py --example --example-output my_scenes.json

# 2. 编辑 my_scenes.json，修改场景内容

# 3. 批量生成
python batch_generator.py --config my_scenes.json --output my_output
```

## 与单图生成器的关系

批量生成器与 `cli_generator.py` 的关系：

1. **内部使用** - 批量生成器内部调用 `generate_image_from_config()`
2. **配置转换** - 自动将批量格式转换为单图格式
3. **功能一致** - 支持所有单图生成器的功能
4. **扩展性** - 可以轻松添加批量专用功能

## 输出结果

- 每个场景生成一个PNG文件
- 文件名格式: `{scene_name}.png`
- 显示详细的生成进度和统计信息
- 失败场景会被记录和报告

## 典型用途

1. **动漫场景** - 生成一系列相关的动漫风格场景
2. **小说插图** - 为小说章节创建配套插图
3. **社交媒体** - 批量制作主题一致的社交媒体内容
4. **演示文稿** - 为PPT或演示创建风格统一的背景

## 性能优化

- 复用字体加载逻辑
- 批量创建输出目录
- 详细的错误报告
- 内存友好的逐个生成模式

## 故障排除

**常见问题**:

1. **字体加载失败** - 检查 `fonts/` 目录中的字体文件
2. **配置格式错误** - 使用 JSON 验证器检查语法
3. **输出目录权限** - 确保有写入权限
4. **内存不足** - 减少同时生成的场景数量

**调试技巧**:
- 先用小配置测试
- 检查单个场景是否能正常生成
- 查看错误信息中的具体失败原因

## 扩展可能

未来可以考虑的扩展：
- 并行生成支持
- 视频序列生成
- 批量尺寸变换
- 模板继承机制 