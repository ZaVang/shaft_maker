#!/bin/bash

# 新房风格背景生成器 - 视频制作脚本
# 支持两种模式:
# 1. 文件夹模式: 将图片文件夹打包成视频
# 2. 台本模式: 根据台本文件灵活编排视频

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
    echo -e "${YELLOW}用法:${NC}"
    echo "  $0 <图片文件夹> [帧间隔] [输出文件] [BGM]  (文件夹模式)"
    echo "  $0 <台本文件.txt> [输出文件]              (台本模式)"
    echo
    echo -e "${YELLOW}模式一: 文件夹模式${NC}"
    echo "  从图片文件夹快速生成视频。"
    echo "  参数:"
    echo "    图片文件夹      包含图片序列的文件夹路径"
    echo "    帧间隔          每张图片显示的时间（秒），默认: 2.0"
    echo "    输出文件        输出视频文件名，默认: output_video.mp4"
    echo "    BGM             可选的背景音乐文件路径"
    echo "  示例:"
    echo "    $0 monogatari_scenes 1.5 monogatari.mp4"
    echo
    echo -e "${YELLOW}模式二: 台本模式${NC}"
    echo "  根据文本台本精确控制图片和音频。"
    echo "  台本格式:"
    echo "    [SETTINGS]"
    echo "    1920x1080  30  60  # 分辨率 帧率 总时长"
    echo "    [IMAGES]"
    echo "    # 开始时间  文件路径                      持续时间"
    echo "    0           monogatari_scenes/scene_01.png  5"
    echo "    [AUDIO]"
    echo "    # 开始时间  文件路径          持续时间(可选)"
    echo "    0           test_bg.mp3       15"
    echo "    10          sfx/sound.wav     2.5"
    echo "  参数:"
    echo "    台本文件.txt    描述视频结构的文本文件"
    echo "    输出文件        输出视频文件名，默认: storyboard_output.mp4"
    echo "  示例:"
    echo "    $0 storyboard.txt final_video.mp4"
    echo
    echo -e "${YELLOW}通用选项:${NC}"
    echo "  -h, --help      显示此帮助信息"
    echo
    echo "注意事项:"
    echo "  - 需要安装ffmpeg 和 bc"
    echo "  - 建议图片尺寸一致以获得最佳效果"
}

# 检查依赖是否安装
check_dependencies() {
    if ! command -v ffmpeg &> /dev/null; then
        echo -e "${RED}错误: 未找到ffmpeg，请先安装ffmpeg${NC}"
        exit 1
    fi
    if ! command -v bc &> /dev/null; then
        echo -e "${RED}错误: 未找到bc，请先安装bc${NC}"
        echo "(bc是用于进行浮点数运算的命令行工具)"
        exit 1
    fi
}

#==============================================================================
# 模式二: 台本模式 (使用BASH READ重写，更稳定)
#==============================================================================

generate_video_from_storyboard() {
    STORYBOARD_FILE="$1"
    OUTPUT_FILE="${2:-storyboard_output.mp4}"

    echo -e "${BLUE}台本模式: 开始处理台本文件...${NC}"
    echo "  台本: $STORYBOARD_FILE"
    echo "  输出: $OUTPUT_FILE"

    if [ ! -f "$STORYBOARD_FILE" ]; then
        echo -e "${RED}错误: 台本文件不存在: $STORYBOARD_FILE${NC}"
        exit 1
    fi

    # --- Bash-based Parser ---
    local mode="none"
    local resolution="1920x1080"
    local fps="30"
    local total_duration="10" # Default duration

    local image_files=()
    local image_start_times=()
    local image_durations=()
    
    local audio_files=()
    local audio_start_times=()
    local audio_durations=()

    # Read the storyboard file line by line
    while IFS= read -r line; do
        # Trim leading/trailing whitespace and remove carriage returns
        line=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/\r$//')

        if [[ -z "$line" || "$line" =~ ^# ]]; then
            continue
        fi

        if [[ "$line" =~ ^\[SETTINGS\]$ ]]; then mode="settings"; continue; fi
        if [[ "$line" =~ ^\[IMAGES\]$ ]]; then mode="images"; continue; fi
        if [[ "$line" =~ ^\[AUDIO\]$ ]]; then mode="audio"; continue; fi

        case "$mode" in
            settings)
                read -r res_val fps_val dur_val <<< "$line"
                resolution=${res_val:-$resolution}
                fps=${fps_val:-$fps}
                total_duration=${dur_val:-$total_duration}
                ;;
            images)
                read -r start_time path duration <<< "$line"
                image_files+=("$path")
                image_start_times+=("$start_time")
                image_durations+=("$duration")
                ;;
            audio)
                read -r start_time path duration <<< "$line"
                audio_files+=("$path")
                audio_start_times+=("$start_time")
                audio_durations+=("$duration") # Duration can be empty
                ;;
        esac
    done < "$STORYBOARD_FILE"

    echo
    echo "视频设置:"
    echo "  分辨率: $resolution"
    echo "  帧率: $fps"
    echo "  总时长: ${total_duration}s"

    # --- FFMPEG Command Assembly ---
    local FFMPEG_INPUTS=""
    local FILTER_COMPLEX=""
    local VIDEO_INPUT_COUNT=0
    local AUDIO_INPUT_COUNT=0

    # Base canvas
    FILTER_COMPLEX="color=c=black:s=$resolution:d=$total_duration:r=$fps [base];"

    echo
    echo "处理图片序列..."
    local overlay_stream="base"
    for i in "${!image_files[@]}"; do
        local path="${image_files[$i]}"
        local start_time="${image_start_times[$i]}"
        local duration="${image_durations[$i]}"

        if [ ! -f "$path" ]; then
            echo -e "${YELLOW}警告: 图片文件不存在，已跳过: $path${NC}"
            continue
        fi
        echo "  + 图片: $path (开始: ${start_time}s, 持续: ${duration}s)"
        FFMPEG_INPUTS+=" -i \"$path\""
        VIDEO_INPUT_COUNT=$((VIDEO_INPUT_COUNT + 1))
        
        local next_overlay_stream="v${i}" 
        FILTER_COMPLEX+="[${overlay_stream}][${i}:v] overlay=x=(W-w)/2:y=(H-h)/2:enable='between(t,${start_time},$(echo "$start_time+$duration" | bc))' [${next_overlay_stream}];"
        overlay_stream=$next_overlay_stream
    done

    echo
    echo "处理音频轨道..."
    local audio_mix_inputs=""
    for i in "${!audio_files[@]}"; do
        local path="${audio_files[$i]}"
        local start_time="${audio_start_times[$i]}"
        local duration="${audio_durations[$i]}"

        if [ ! -f "$path" ]; then
            echo -e "${YELLOW}警告: 音频文件不存在，已跳过: $path${NC}"
            continue
        fi

        FFMPEG_INPUTS+=" -i \"$path\""
        AUDIO_INPUT_COUNT=$((AUDIO_INPUT_COUNT + 1))
        local audio_input_index=$((VIDEO_INPUT_COUNT + AUDIO_INPUT_COUNT - 1))
        
        local trim_filter=""
        if [[ "$duration" =~ ^[0-9] ]]; then
            echo "  + 音频: $path (开始: ${start_time}s, 持续: ${duration}s)"
            trim_filter=",atrim=duration=${duration}"
        else
            echo "  + 音频: $path (开始: ${start_time}s, 持续: 完整)"
        fi
        
        local delay_ms=$(echo "$start_time * 1000" | bc)
        FILTER_COMPLEX+="[${audio_input_index}:a]adelay=${delay_ms}|${delay_ms}${trim_filter}[a${i}];"
        audio_mix_inputs+="[a${i}]"
    done

    local FINAL_CMD="ffmpeg $FFMPEG_INPUTS"
    
    if [ $AUDIO_INPUT_COUNT -gt 0 ]; then
        FILTER_COMPLEX+="${audio_mix_inputs}amix=inputs=${AUDIO_INPUT_COUNT}[final_a];"
        FINAL_CMD+=" -filter_complex \"${FILTER_COMPLEX%?}\" -map \"[$overlay_stream]\" -map \"[final_a]\""
    else
        FINAL_CMD+=" -filter_complex \"${FILTER_COMPLEX%?}\" -map \"[$overlay_stream]\""
    fi

    FINAL_CMD+=" -c:v libx264 -pix_fmt yuv420p -r $fps -t $total_duration -c:a aac -b:a 192k -y \"$OUTPUT_FILE\""

    echo
    echo -e "${BLUE}执行ffmpeg命令...${NC}"
    eval $FINAL_CMD

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 台本视频生成成功!${NC}"
        echo "   输出文件: $OUTPUT_FILE"
    else
        echo -e "${RED}❌ 台本视频生成失败${NC}"
        exit 1
    fi
}


#==============================================================================
# 模式一: 文件夹模式
#==============================================================================

validate_folder_inputs() {
    if [ ! -d "$IMAGE_DIR" ]; then
        echo -e "${RED}错误: 图片文件夹不存在: $IMAGE_DIR${NC}"
        exit 1
    fi

    IMAGE_COUNT=$(find "$IMAGE_DIR" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) | wc -l)
    if [ "$IMAGE_COUNT" -eq 0 ]; then
        echo -e "${RED}错误: 文件夹中未找到支持的图片文件 (PNG, JPG, JPEG)${NC}"
        exit 1
    fi
    echo -e "${GREEN}找到 $IMAGE_COUNT 张图片${NC}"

    if ! [[ $FRAME_DURATION =~ ^[0-9]*\.?[0-9]+$ ]]; then
        echo -e "${RED}错误: 帧间隔时间必须是正数: $FRAME_DURATION${NC}"
        exit 1
    fi

    if [ -n "$BGM_FILE" ] && [ ! -f "$BGM_FILE" ]; then
        echo -e "${RED}错误: BGM音频文件不存在: $BGM_FILE${NC}"
        exit 1
    fi
}

generate_video_from_folder() {
    IMAGE_DIR="$1"
    FRAME_DURATION="${2:-2.0}"
    OUTPUT_FILE="${3:-output_video.mp4}"
    BGM_FILE="$4"

    echo -e "${BLUE}文件夹模式: 开始生成视频...${NC}"
    validate_folder_inputs

    TEMP_LIST_FILE=$(mktemp)
    # Use realpath to get absolute paths for ffmpeg
    find "$(realpath "$IMAGE_DIR")" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) | sort -V > "$TEMP_LIST_FILE"

    CONCAT_FILE=$(mktemp)
    while read -r image_file; do
        echo "file '$image_file'" >> "$CONCAT_FILE"
        echo "duration $FRAME_DURATION" >> "$CONCAT_FILE"
    done < "$TEMP_LIST_FILE"
    # The last image needs to be duplicated for the concat demuxer to work correctly
    tail -1 "$TEMP_LIST_FILE" | while read -r last_image; do echo "file '$last_image'" >> "$CONCAT_FILE"; done

    FFMPEG_CMD="ffmpeg -f concat -safe 0 -i \"$CONCAT_FILE\""

    if [ -n "$BGM_FILE" ]; then
        FFMPEG_CMD+=" -stream_loop -1 -i \"$BGM_FILE\" -c:a aac -b:a 128k -shortest"
    fi

    FFMPEG_CMD+=" -c:v libx264 -r 25 -pix_fmt yuv420p -crf 18 -movflags +faststart -y \"$OUTPUT_FILE\""

    echo -e "${BLUE}执行ffmpeg命令...${NC}"
    eval $FFMPEG_CMD

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 文件夹视频生成成功!${NC}"
        echo "   输出文件: $OUTPUT_FILE"
    else
        echo -e "${RED}❌ 文件夹视频生成失败${NC}"
        echo "请检查concat文件内容:"
        cat "$CONCAT_FILE"
        exit 1
    fi

    rm -f "$TEMP_LIST_FILE" "$CONCAT_FILE"
}


#==============================================================================
# 主函数
#==============================================================================
main() {
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi

    check_dependencies

    echo -e "${BLUE}🎬 新房风格背景生成器 - 视频制作工具${NC}"
    echo "=================================================="

    INPUT_PATH="$1"

    # Check if input is a file (storyboard mode) or a directory (folder mode)
    if [ -f "$INPUT_PATH" ]; then
        # Storyboard mode
        generate_video_from_storyboard "$1" "$2"
    elif [ -d "$INPUT_PATH" ]; then
        # Folder mode
        generate_video_from_folder "$1" "$2" "$3" "$4"
    else
        echo -e "${RED}错误: 输入路径既不是文件也不是文件夹: $INPUT_PATH${NC}"
        show_help
        exit 1
    fi

    echo
    echo -e "${GREEN}🎉 任务完成！${NC}"
}

# Execute main function
main "$@"