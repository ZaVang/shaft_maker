# 视频制作工具使用指南

## 概述

`make_video.sh` 是一个专门为新房风格背景生成器设计的视频制作工具，可以将图片文件夹快速打包成MP4视频。

## 功能特点

- 🎬 **自动排序** - 按文件名自然顺序排列图片
- ⏱️ **可调时长** - 自定义每张图片的显示时间
- 📊 **进度显示** - 实时显示处理进度和统计信息
- 🔧 **智能检查** - 自动验证依赖和输入参数
- 📱 **高质量输出** - H.264编码，兼容各种播放器

## 系统要求

- **ffmpeg** - 必需的视频处理工具
- **bash** - Shell环境（macOS/Linux默认支持）

### 安装ffmpeg

```bash
# macOS (使用Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载安装
```

## 使用方法

### 基本语法

```bash
./make_video.sh <图片文件夹> [帧间隔时间] [输出文件名] [BGM音频文件]
```

### 参数说明

1. **图片文件夹** (必需)
   - 包含PNG、JPG、JPEG图片的文件夹路径
   - 支持相对路径和绝对路径

2. **帧间隔时间** (可选，默认: 2.0秒)
   - 每张图片显示的时间（秒）
   - 支持小数，如 1.5、3.5 等

3. **输出文件名** (可选，默认: output_video.mp4)
   - 输出视频的文件名
   - 自动添加.mp4扩展名

4. **BGM音频文件** (可选)
   - 背景音乐文件路径
   - 支持MP3、WAV、AAC、FLAC、OGG等格式
   - 音频长度会自动调整到与视频相同

## 使用示例

### 基础用法

```bash
# 使用默认设置（每张图片2秒）
./make_video.sh monogatari_scenes

# 指定帧间隔时间
./make_video.sh monogatari_scenes 1.5

# 完整参数
./make_video.sh monogatari_scenes 1.5 monogatari.mp4

# 添加BGM背景音乐
./make_video.sh monogatari_scenes 2.0 monogatari_with_bgm.mp4 music/bgm.mp3
```

### 实际场景

```bash
# 快速浏览模式（0.8秒/张）
./make_video.sh batch_scenes 0.8 quick_preview.mp4

# 阅读模式（3秒/张，适合文字内容）
./make_video.sh monogatari_scenes 3.0 story_reading.mp4

# 展示模式（5秒/张，适合详细欣赏）
./make_video.sh artwork_scenes 5.0 gallery_showcase.mp4

# 带背景音乐的动漫场景（2.5秒/张）
./make_video.sh anime_scenes 2.5 anime_with_music.mp4 soundtrack.mp3

# 作品集展示配乐版
./make_video.sh portfolio 4.0 portfolio_music.mp4 ambient_music.wav
```

## 输出特性

### 视频格式

- **视频编码**: H.264 (高兼容性)
- **音频编码**: AAC (通用格式)
- **像素格式**: yuv420p (标准格式)
- **视频质量**: CRF 18 (高质量)
- **音频质量**: 128kbps (高品质)
- **容器**: MP4 (通用格式)

### 文件优化

- **Fast Start**: 优化网络播放
- **压缩比**: 在质量和文件大小间平衡
- **兼容性**: 支持所有主流播放器

## 工作流程

1. **检查依赖** - 验证ffmpeg是否安装
2. **验证输入** - 检查文件夹和参数有效性
3. **图片清单** - 按顺序列出所有图片
4. **参数计算** - 计算总时长和帧率
5. **视频生成** - 调用ffmpeg进行转换
6. **结果报告** - 显示视频信息和统计

## 实际用例

### 动漫场景视频

```bash
# 为《终物语》场景制作视频
./make_video.sh monogatari_scenes 2.5 monogatari_episode.mp4
```

**适用场景**:
- 动漫剧情展示
- 台词朗读配合
- 场景氛围营造

### 作品展示

```bash
# 艺术作品集
./make_video.sh portfolio_images 4.0 portfolio_demo.mp4
```

**适用场景**:
- 设计作品集
- 摄影作品展示
- 创作过程记录

### 快速预览

```bash
# 大量图片快速浏览
./make_video.sh large_dataset 0.5 quick_scan.mp4
```

**适用场景**:
- 批量图片预览
- 数据集检查
- 快速内容概览

## 技术细节

### 帧率计算

帧率 = 1 / 帧间隔时间

- 2.0秒 → 0.5 fps
- 1.5秒 → 0.67 fps  
- 1.0秒 → 1.0 fps

### 文件排序

使用自然排序(`sort -V`)，正确处理数字序列：

```
scene_1.png
scene_2.png
scene_10.png
scene_11.png
```

### 音频处理

**BGM长度调整**:
- 如果BGM短于视频：自动循环播放BGM直到视频结束
- 如果BGM长于视频：自动截断BGM到视频长度
- 使用 `-shortest` 参数确保视频和音频同步结束

**音频格式转换**:
- 所有输入音频格式都会转换为AAC编码
- 比特率设置为128kbps，平衡质量和文件大小
- 支持立体声和单声道输入

### 临时文件

脚本会创建临时文件进行处理，完成后自动清理：
- 图片列表文件
- FFmpeg concat文件

## 故障排除

### 常见问题

1. **ffmpeg未找到**
   ```
   错误: 未找到ffmpeg，请先安装ffmpeg
   ```
   **解决**: 安装ffmpeg并确保在PATH中

2. **图片文件夹为空**
   ```
   错误: 文件夹中未找到支持的图片文件
   ```
   **解决**: 检查文件夹中是否有PNG/JPG/JPEG文件

3. **帧间隔时间无效**
   ```
   错误: 帧间隔时间必须是正数
   ```
   **解决**: 使用正数，如1.5、2.0等

4. **文件权限问题**
   ```
   permission denied: ./make_video.sh
   ```
   **解决**: 添加执行权限 `chmod +x make_video.sh`

5. **BGM音频问题**
   ```
   错误: BGM音频文件不存在: music.mp3
   ```
   **解决**: 检查音频文件路径是否正确

   ```
   警告: 音频格式 .wma 可能不被支持
   推荐格式: MP3, WAV, AAC, FLAC, OGG
   ```
   **解决**: 转换为支持的格式
   ```bash
   ffmpeg -i input.wma -c:a mp3 output.mp3
   ```

### 调试技巧

1. **查看详细信息**: 脚本会显示图片预览和参数设置
2. **检查输入**: 确认图片文件名和数量
3. **测试小数据集**: 先用少量图片测试
4. **检查输出**: 查看生成的视频信息

## 性能考虑

### 文件大小优化

- **CRF值**: 18（高质量），可调整为20-23降低文件大小
- **预设**: medium（平衡速度和质量）
- **像素格式**: yuv420p（最佳兼容性）

### 处理速度

影响因素：
- 图片数量和分辨率
- 帧间隔时间（影响总时长）
- 系统CPU性能
- 存储设备速度

## 扩展用法

### 与批量生成器结合

```bash
# 1. 批量生成场景
python batch_generator.py --config scenes.json --output my_scenes

# 2. 制作视频（无音频版）
./make_video.sh my_scenes 2.0 final_video.mp4

# 3. 制作视频（配乐版）
./make_video.sh my_scenes 2.0 final_video_with_bgm.mp4 soundtrack.mp3
```

### 多版本输出

```bash
# 创建不同时长的版本
./make_video.sh scenes 1.0 fast_version.mp4
./make_video.sh scenes 3.0 slow_version.mp4
./make_video.sh scenes 0.5 preview_version.mp4

# 创建有音频和无音频版本
./make_video.sh scenes 2.0 silent_version.mp4
./make_video.sh scenes 2.0 music_version.mp4 bgm.mp3
```

### 自动化脚本

```bash
#!/bin/bash
# 自动处理多个文件夹
for folder in */; do
    if [ -d "$folder" ]; then
        ./make_video.sh "$folder" 2.0 "${folder%/}_video.mp4"
    fi
done
```

这个视频制作工具完美地补充了新房风格背景生成器，让您能够轻松地将静态图片转换为动态的视频内容！ 