#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量场景生成器
根据JSON配置文件批量生成新房风格背景图片
复用cli_generator.py的核心实现
"""

import json
import os
import sys
import argparse
from cli_generator import generate_image_from_config


def generate_batch_scenes(config_file, output_dir):
    """
    根据配置文件批量生成场景图片
    
    Args:
        config_file (str): JSON配置文件路径
        output_dir (str): 输出目录路径
    """
    
    # 读取配置文件
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            batch_config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误: {e}")
    except Exception as e:
        raise Exception(f"读取配置文件失败: {e}")
    
    # 获取基础模板和场景列表
    base_template = batch_config.get('base_template', {})
    scenes = batch_config.get('scenes', [])
    
    if not scenes:
        raise ValueError("配置文件中没有定义任何场景")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"开始批量生成，共 {len(scenes)} 个场景...")
    print("=" * 50)
    
    successful_count = 0
    failed_scenes = []
    
    # 生成每个场景
    for i, scene in enumerate(scenes, 1):
        scene_name = scene.get('name', f'scene_{i:03d}')
        print(f"[{i}/{len(scenes)}] 生成场景: {scene_name}")
        
        try:
            # 构建单个场景的完整配置
            scene_config = build_scene_config(base_template, scene)
            
            # 生成图片
            output_path = os.path.join(output_dir, f"{scene_name}.png")
            image = generate_image_from_config(scene_config, output_path)
            
            print(f"✅ 成功生成: {output_path}")
            successful_count += 1
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            failed_scenes.append(scene_name)
    
    # 输出统计信息
    print("\n" + "=" * 50)
    print(f"批量生成完成！")
    print(f"成功: {successful_count}/{len(scenes)} 个场景")
    
    if failed_scenes:
        print(f"失败: {len(failed_scenes)} 个场景")
        print("失败的场景:", ", ".join(failed_scenes))
    else:
        print("🎉 所有场景都生成成功！")


def build_scene_config(base_template, scene):
    """
    构建单个场景的完整配置
    
    Args:
        base_template (dict): 基础模板配置
        scene (dict): 场景特定配置
    
    Returns:
        dict: 符合cli_generator格式的配置字典
    """
    
    # 合并基础配置
    config = {
        "background": {
            "width": base_template.get('width', 1920),
            "height": base_template.get('height', 1080),
            "main_color": scene.get('background_color', '#000000'),
            "border_color": scene.get('border_color', '#FFFFFF'),
            "border_height": base_template.get('border_height', 0)
        },
        "lines": {
            "enabled": base_template.get('line_density', 0) > 0,
            "opacity": int(base_template.get('line_opacity', 0.3) * 100),  # 转换为百分比
            "color": scene.get('line_color', '#666666'),
            "spacing": max(1, base_template.get('line_density', 3))  # 确保spacing至少为1
        },
        "text_layers": []
    }
    
    # 转换文字层配置
    scene_text_layers = scene.get('text_layers', [])
    for layer in scene_text_layers:
        text_layer = {
            "content": layer.get('text', ''),
            "size": layer.get('size', 48),
            "color": layer.get('color', '#FFFFFF'),
            "font_path": layer.get('font_path', ''),
            "x_offset": layer.get('x_offset', 0),
            "y_offset": layer.get('y_offset', 0),
            "direction": _convert_direction(layer.get('direction', 'horizontal_lr')),
            "flip": _convert_flip(layer.get('flip', 'none')),
            "rotation": _convert_rotation(layer.get('rotation', 0))
        }
        config["text_layers"].append(text_layer)
    
    return config


def _convert_direction(old_direction):
    """转换旧格式的文字方向到新格式"""
    direction_map = {
        'horizontal_lr': '水平 (左→右)',
        'horizontal_rl': '水平 (右→左)',
        'vertical': '垂直 (上→下)',
        'horizontal_ltr': '水平 (左→右)',
        'horizontal_rtl': '水平 (右→左)'
    }
    return direction_map.get(old_direction, '水平 (左→右)')


def _convert_flip(old_flip):
    """转换旧格式的翻转到新格式"""
    flip_map = {
        'none': '无',
        'horizontal': '水平翻转',
        'vertical': '垂直翻转',
        'both': '水平+垂直翻转'
    }
    return flip_map.get(old_flip, '无')


def _convert_rotation(old_rotation):
    """转换旧格式的旋转到新格式"""
    if isinstance(old_rotation, (int, float)):
        return f"{int(old_rotation)}°"
    return str(old_rotation)


def create_example_batch_config():
    """创建示例批量配置"""
    return {
        "base_template": {
            "width": 1920,
            "height": 1080,
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
                "text_layers": [
                    {
                        "text": "新房风格测试",
                        "size": 60,
                        "color": "#f5deb3",
                        "font_path": "assets/fonts/Songti.ttc",
                        "x_offset": 0,
                        "y_offset": -100,
                        "direction": "horizontal_lr",
                        "flip": "none",
                        "rotation": 0
                    },
                    {
                        "text": "场景一",
                        "size": 40,
                        "color": "#daa520",
                        "font_path": "assets/fonts/Songti.ttc",
                        "x_offset": 0,
                        "y_offset": 50,
                        "direction": "horizontal_lr",
                        "flip": "none",
                        "rotation": 0
                    }
                ]
            },
            {
                "name": "scene_02",
                "background_color": "#1a0d0d",
                "border_color": "#8b0000",
                "line_color": "#cd5c5c",
                "text_layers": [
                    {
                        "text": "第二个场景",
                        "size": 65,
                        "color": "#ffb6c1",
                        "font_path": "assets/fonts/Songti.ttc",
                        "x_offset": 0,
                        "y_offset": -80,
                        "direction": "horizontal_lr",
                        "flip": "none",
                        "rotation": 0
                    },
                    {
                        "text": "测试文字",
                        "size": 35,
                        "color": "#ff69b4",
                        "font_path": "assets/fonts/Songti.ttc",
                        "x_offset": 0,
                        "y_offset": 60,
                        "direction": "horizontal_lr",
                        "flip": "none",
                        "rotation": 0
                    }
                ]
            },
            {
                "name": "scene_03",
                "background_color": "#0d0d1a",
                "border_color": "#000080",
                "line_color": "#4169e1",
                "text_layers": [
                    {
                        "text": "垂直文字测试",
                        "size": 50,
                        "color": "#87ceeb",
                        "font_path": "assets/fonts/Songti.ttc",
                        "x_offset": -200,
                        "y_offset": 0,
                        "direction": "vertical",
                        "flip": "none",
                        "rotation": 0
                    },
                    {
                        "text": "SCENE THREE",
                        "size": 40,
                        "color": "#6495ed",
                        "font_path": "assets/fonts/Songti.ttc",
                        "x_offset": 200,
                        "y_offset": 0,
                        "direction": "horizontal_lr",
                        "flip": "none",
                        "rotation": 45
                    }
                ]
            }
        ]
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量生成新房风格场景图片")
    parser.add_argument("-c", "--config", help="JSON配置文件路径")
    parser.add_argument("-o", "--output", default="output/batch_scenes", help="输出目录（默认：output/batch_scenes）")
    parser.add_argument("--example", action="store_true", help="生成示例批量配置文件")
    parser.add_argument("--example-output", default="configs/batch_config_example.json", 
                       help="示例配置文件输出路径（默认：configs/batch_config_example.json）")
    
    args = parser.parse_args()
    
    if args.example:
        # 生成示例配置文件
        example_config = create_example_batch_config()
        with open(args.example_output, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, ensure_ascii=False, indent=2)
        print(f"示例批量配置文件已生成: {args.example_output}")
        return
    
    if not args.config:
        print("错误：请提供配置文件路径 (-c/--config) 或使用 --example 生成示例配置")
        sys.exit(1)
    
    try:
        generate_batch_scenes(args.config, args.output)
    except Exception as e:
        print(f"批量生成失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 