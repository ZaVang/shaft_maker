#!/bin/bash

# 新房风格背景生成器 - 视频制作脚本
# 将图片文件夹打包成视频

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示使用帮助
show_help() {
    echo -e "${BLUE}新房风格背景生成器 - 视频制作工具${NC}"
    echo
    echo "用法: $0 <图片文件夹> [帧间隔时间] [输出文件名] [BGM音频文件]"
    echo
    echo "参数:"
    echo "  图片文件夹      包含图片序列的文件夹路径"
    echo "  帧间隔时间      每张图片显示的时间（秒），默认: 2.0"
    echo "  输出文件名      输出视频文件名，默认: output_video.mp4"
    echo "  BGM音频文件     可选的背景音乐文件路径"
    echo
    echo "示例:"
    echo "  $0 monogatari_scenes 1.5 monogatari.mp4"
    echo "  $0 batch_scenes 3.0"
    echo "  $0 ./my_images 2.0 video.mp4 bgm.mp3"
    echo "  $0 scenes 1.5 output.mp4 music/background.wav"
    echo
    echo "支持的图片格式: PNG, JPG, JPEG"
    echo "支持的音频格式: MP3, WAV, AAC, FLAC, OGG"
    echo "输出格式: MP4 (H.264编码 + AAC音频)"
    echo
    echo "注意事项:"
    echo "  - 需要安装ffmpeg"
    echo "  - 图片会按文件名自然排序"
    echo "  - 建议图片尺寸一致以获得最佳效果"
    echo "  - BGM长度会自动调整到与视频相同"
    echo "  - 如果BGM太长会被截断，太短会循环播放"
}

# 检查ffmpeg是否安装
check_ffmpeg() {
    if ! command -v ffmpeg &> /dev/null; then
        echo -e "${RED}错误: 未找到ffmpeg，请先安装ffmpeg${NC}"
        echo "安装方法:"
        echo "  macOS: brew install ffmpeg"
        echo "  Ubuntu: sudo apt install ffmpeg"
        echo "  Windows: 下载并安装 https://ffmpeg.org/download.html"
        exit 1
    fi
}

# 验证输入参数
validate_inputs() {
    # 检查图片文件夹
    if [ ! -d "$IMAGE_DIR" ]; then
        echo -e "${RED}错误: 图片文件夹不存在: $IMAGE_DIR${NC}"
        exit 1
    fi
    
    # 检查文件夹中是否有图片
    IMAGE_COUNT=$(find "$IMAGE_DIR" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) | wc -l)
    if [ "$IMAGE_COUNT" -eq 0 ]; then
        echo -e "${RED}错误: 文件夹中未找到支持的图片文件 (PNG, JPG, JPEG)${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}找到 $IMAGE_COUNT 张图片${NC}"
    
    # 验证帧间隔时间
    if ! [[ $FRAME_DURATION =~ ^[0-9]*\.?[0-9]+$ ]]; then
        echo -e "${RED}错误: 帧间隔时间必须是正数: $FRAME_DURATION${NC}"
        exit 1
    fi
    
    # 检查BGM音频文件（如果提供了的话）
    if [ -n "$BGM_FILE" ]; then
        if [ ! -f "$BGM_FILE" ]; then
            echo -e "${RED}错误: BGM音频文件不存在: $BGM_FILE${NC}"
            exit 1
        fi
        
        # 检查音频文件格式
        BGM_EXT=$(echo "${BGM_FILE##*.}" | tr '[:upper:]' '[:lower:]')
        if [[ ! "$BGM_EXT" =~ ^(mp3|wav|aac|flac|ogg|m4a)$ ]]; then
            echo -e "${YELLOW}警告: 音频格式 .$BGM_EXT 可能不被支持${NC}"
            echo "推荐格式: MP3, WAV, AAC, FLAC, OGG"
        fi
        
        echo -e "${GREEN}BGM文件: $(basename "$BGM_FILE")${NC}"
    else
        echo -e "${BLUE}无BGM音频${NC}"
    fi
    
    # 检查输出文件是否存在
    if [ -f "$OUTPUT_FILE" ]; then
        echo -e "${YELLOW}警告: 输出文件已存在: $OUTPUT_FILE${NC}"
        read -p "是否覆盖? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "操作已取消"
            exit 0
        fi
    fi
}

# 创建图片列表文件
create_image_list() {
    TEMP_LIST_FILE=$(mktemp)
    
    echo -e "${BLUE}创建图片列表...${NC}"
    
    # 按自然顺序排序图片文件，使用绝对路径
    find "$(realpath "$IMAGE_DIR")" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) | sort -V > "$TEMP_LIST_FILE"
    
    # 显示前几个文件名
    echo "图片序列预览:"
    head -5 "$TEMP_LIST_FILE" | while read -r file; do
        echo "  $(basename "$file")"
    done
    
    if [ "$IMAGE_COUNT" -gt 5 ]; then
        echo "  ... (共 $IMAGE_COUNT 张图片)"
    fi
}

# 生成视频 - 修正版本
generate_video() {
    echo -e "${BLUE}开始生成视频...${NC}"
    echo "参数设置:"
    echo "  输入文件夹: $IMAGE_DIR"
    echo "  每张图片持续时间: ${FRAME_DURATION}秒"
    echo "  输出文件: $OUTPUT_FILE"
    TOTAL_DURATION=$(awk "BEGIN {print $IMAGE_COUNT * $FRAME_DURATION}")
    echo "  总时长: 约${TOTAL_DURATION}秒"
    if [ -n "$BGM_FILE" ]; then
        echo "  BGM文件: $(basename "$BGM_FILE")"
    fi
    echo
    
    # 设置合理的输出帧率（推荐25fps或30fps）
    OUTPUT_FPS=25
    
    # 创建临时的concat文件
    CONCAT_FILE=$(mktemp)
    
    # 为每张图片生成concat文件内容
    echo "生成concat文件..."
    while read -r image_file; do
        echo "file '$image_file'" >> "$CONCAT_FILE"
        echo "duration $FRAME_DURATION" >> "$CONCAT_FILE"
    done < "$TEMP_LIST_FILE"
    
    # 最后一张图片需要再重复一次（ffmpeg concat要求）
    tail -1 "$TEMP_LIST_FILE" | while read -r last_image; do
        echo "file '$last_image'" >> "$CONCAT_FILE"
    done
    
    echo "Concat文件内容预览:"
    head -6 "$CONCAT_FILE"
    echo "..."
    echo
    
    # 执行ffmpeg命令
    if [ -n "$BGM_FILE" ]; then
        echo "生成带BGM的视频..."
        ffmpeg -f concat -safe 0 -i "$CONCAT_FILE" \
               -stream_loop -1 -i "$BGM_FILE" \
               -c:v libx264 \
               -r $OUTPUT_FPS \
               -pix_fmt yuv420p \
               -crf 18 \
               -preset medium \
               -c:a aac \
               -b:a 128k \
               -shortest \
               -movflags +faststart \
               -y "$OUTPUT_FILE"
    else
        echo "生成无音频视频..."
        ffmpeg -f concat -safe 0 -i "$CONCAT_FILE" \
               -c:v libx264 \
               -r $OUTPUT_FPS \
               -pix_fmt yuv420p \
               -crf 18 \
               -preset medium \
               -movflags +faststart \
               -y "$OUTPUT_FILE"
    fi
    
    # 检查ffmpeg执行结果
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 视频生成成功!${NC}"
        echo "输出文件: $OUTPUT_FILE"
        
        # 显示文件信息
        if command -v ffprobe &> /dev/null; then
            echo
            echo "视频信息:"
            
            # 获取视频信息
            VIDEO_INFO=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=s=x:p=0 "$OUTPUT_FILE" 2>/dev/null)
            DURATION_INFO=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_FILE" 2>/dev/null)
            
            if [ -n "$VIDEO_INFO" ]; then
                WIDTH_HEIGHT=$(echo "$VIDEO_INFO" | cut -d'x' -f1,2)
                FRAME_RATE=$(echo "$VIDEO_INFO" | cut -d'x' -f3)
                echo "  分辨率: $WIDTH_HEIGHT"
                echo "  帧率: $FRAME_RATE fps"
            fi
            if [ -n "$DURATION_INFO" ]; then
                DURATION_FORMATTED=$(awk "BEGIN {printf \"%.1f\", $DURATION_INFO}")
                echo "  实际时长: ${DURATION_FORMATTED}秒"
                echo "  预期时长: ${TOTAL_DURATION}秒"
                
                # 检查时长差异
                DURATION_DIFF=$(awk "BEGIN {printf \"%.1f\", $DURATION_INFO - $TOTAL_DURATION}")
                if [ $(awk "BEGIN {print ($DURATION_DIFF > 0.5 || $DURATION_DIFF < -0.5)}") -eq 1 ]; then
                    echo -e "  ${YELLOW}⚠️  时长差异较大: ${DURATION_DIFF}秒${NC}"
                fi
            fi
        fi
        
        # 显示文件大小
        FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo "  文件大小: $FILE_SIZE"
        
    else
        echo -e "${RED}❌ 视频生成失败${NC}"
        echo "请检查concat文件内容:"
        cat "$CONCAT_FILE"
        exit 1
    fi
    
    # 清理临时文件
    rm -f "$TEMP_LIST_FILE" "$CONCAT_FILE"
}

generate_video_with_transitions() {
    echo -e "${BLUE}开始生成带过渡效果的视频...${NC}"
    echo "参数设置:"
    echo "  输入文件夹: $IMAGE_DIR"
    echo "  每张图片持续时间: ${FRAME_DURATION}秒"
    echo "  过渡效果时长: 0.5秒"
    echo "  输出文件: $OUTPUT_FILE"
    
    # 计算总时长（考虑过渡效果）
    TRANSITION_DURATION=0.5
    EFFECTIVE_DURATION=$(awk "BEGIN {print $FRAME_DURATION - $TRANSITION_DURATION}")
    TOTAL_DURATION=$(awk "BEGIN {print $IMAGE_COUNT * $FRAME_DURATION}")
    echo "  总时长: 约${TOTAL_DURATION}秒"
    echo
    
    # 设置输出帧率
    OUTPUT_FPS=30
    
    # 构建ffmpeg过滤器链
    FILTER_COMPLEX=""
    INPUTS=""
    
    # 读取所有图片
    i=0
    while read -r image_file; do
        INPUTS="$INPUTS -loop 1 -t $FRAME_DURATION -i \"$image_file\""
        
        if [ $i -eq 0 ]; then
            # 第一张图片：只有淡出
            FILTER_COMPLEX="$FILTER_COMPLEX[$i:v]fade=t=out:st=$EFFECTIVE_DURATION:d=$TRANSITION_DURATION,scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2[v$i];"
        elif [ $i -eq $((IMAGE_COUNT-1)) ]; then
            # 最后一张图片：只有淡入
            FILTER_COMPLEX="$FILTER_COMPLEX[$i:v]fade=t=in:st=0:d=$TRANSITION_DURATION,scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2[v$i];"
        else
            # 中间图片：淡入+淡出
            FILTER_COMPLEX="$FILTER_COMPLEX[$i:v]fade=t=in:st=0:d=$TRANSITION_DURATION,fade=t=out:st=$EFFECTIVE_DURATION:d=$TRANSITION_DURATION,scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2[v$i];"
        fi
        
        i=$((i+1))
    done < "$TEMP_LIST_FILE"
    
    # 构建concat部分
    CONCAT_INPUTS=""
    for ((j=0; j<i; j++)); do
        CONCAT_INPUTS="$CONCAT_INPUTS[v$j]"
    done
    FILTER_COMPLEX="$FILTER_COMPLEX${CONCAT_INPUTS}concat=n=$i:v=1:a=0[outv]"
    
    # 执行ffmpeg命令
    if [ -n "$BGM_FILE" ]; then
        echo "生成带BGM和过渡效果的视频..."
        eval "ffmpeg $INPUTS -i \"$BGM_FILE\" \
               -filter_complex \"$FILTER_COMPLEX\" \
               -map \"[outv]\" -map $i:a \
               -c:v libx264 \
               -r $OUTPUT_FPS \
               -pix_fmt yuv420p \
               -crf 18 \
               -preset medium \
               -c:a aac \
               -b:a 128k \
               -shortest \
               -movflags +faststart \
               -y \"$OUTPUT_FILE\""
    else
        echo "生成带过渡效果的视频..."
        eval "ffmpeg $INPUTS \
               -filter_complex \"$FILTER_COMPLEX\" \
               -map \"[outv]\" \
               -c:v libx264 \
               -r $OUTPUT_FPS \
               -pix_fmt yuv420p \
               -crf 18 \
               -preset medium \
               -movflags +faststart \
               -y \"$OUTPUT_FILE\""
    fi
    
    # 检查结果
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 带过渡效果的视频生成成功!${NC}"
        echo "输出文件: $OUTPUT_FILE"
    else
        echo -e "${RED}❌ 视频生成失败${NC}"
        exit 1
    fi
    
    # 清理临时文件
    rm -f "$TEMP_LIST_FILE"
}


# 主函数
main() {
    # 解析命令行参数
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi
    
    IMAGE_DIR="$1"
    FRAME_DURATION="${2:-2.0}"  # 默认2秒
    OUTPUT_FILE="${3:-output_video.mp4}"  # 默认输出文件名
    BGM_FILE="$4"  # 可选的BGM文件
    
    echo -e "${BLUE}🎬 新房风格背景生成器 - 视频制作工具${NC}"
    echo "================================================"
    
    # 执行各个步骤
    check_ffmpeg
    validate_inputs
    create_image_list
    generate_video
    
    echo
    echo -e "${GREEN}🎉 任务完成！${NC}"
}

# 执行主函数
main "$@"
