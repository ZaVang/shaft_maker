#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试命令行生成器的使用示例
"""

from cli_generator import generate_image_from_config, generate_image_from_json

def test_direct_config():
    """测试直接使用字典配置生成图片"""
    print("测试1: 使用字典配置生成图片...")
    
    config = {
        "background": {
            "width": 1280,
            "height": 720,
            "main_color": "#1a1a2e",
            "border_color": "#16213e",
            "border_height": 30
        },
        "lines": {
            "enabled": True,
            "opacity": 20,
            "color": "#0f3460",
            "spacing": 4
        },
        "text_layers": [
            {
                "content": "Python脚本测试",
                "size": 60,
                "color": "#e94560",
                "font_path": "fonts/Songti.ttc",
                "x_offset": 0,
                "y_offset": -50,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "0°"
            },
            {
                "content": "CLI Generator",
                "size": 30,
                "color": "#f5f5f5",
                "font_path": "fonts/Songti.ttc",
                "x_offset": 0,
                "y_offset": 30,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "0°"
            }
        ]
    }
    
    # 生成图片
    image = generate_image_from_config(config, "test_direct.png")
    print("✅ 图片已生成: test_direct.png")
    return image

def test_json_config():
    """测试使用JSON文件配置生成图片"""
    print("\n测试2: 使用JSON配置文件生成图片...")
    
    # 使用已存在的示例配置文件
    try:
        image = generate_image_from_json("example_config.json", "test_from_json.png")
        print("✅ 图片已生成: test_from_json.png")
        return image
    except FileNotFoundError:
        print("❌ 找不到 example_config.json，请先运行 'python cli_generator.py --example'")
        return None

def test_vertical_text():
    """测试垂直文字效果"""
    print("\n测试3: 垂直文字效果...")
    
    config = {
        "background": {
            "width": 800,
            "height": 1200,
            "main_color": "#2c2c54",
            "border_color": "#40407a",
            "border_height": 40
        },
        "lines": {
            "enabled": False
        },
        "text_layers": [
            {
                "content": "垂直排列文字测试",
                "size": 50,
                "color": "#ffc048",
                "font_path": "fonts/Songti.ttc",
                "x_offset": -150,
                "y_offset": 0,
                "direction": "垂直 (上→下)",
                "flip": "无",
                "rotation": "0°"
            },
            {
                "content": "VERTICAL TEXT",
                "size": 40,
                "color": "#ff6b6b",
                "font_path": "fonts/Songti.ttc",
                "x_offset": 150,
                "y_offset": 0,
                "direction": "垂直 (上→下)",
                "flip": "水平翻转",
                "rotation": "0°"
            }
        ]
    }
    
    image = generate_image_from_config(config, "test_vertical.png")
    print("✅ 图片已生成: test_vertical.png")
    return image

def test_rotation_effects():
    """测试旋转效果"""
    print("\n测试4: 旋转效果...")
    
    config = {
        "background": {
            "width": 1000,
            "height": 1000,
            "main_color": "#1e3c72",
            "border_color": "#2a5298",
            "border_height": 0
        },
        "lines": {
            "enabled": True,
            "opacity": 15,
            "color": "#ffffff",
            "spacing": 5
        },
        "text_layers": [
            {
                "content": "0°",
                "size": 40,
                "color": "#ffffff",
                "font_path": "fonts/Songti.ttc",
                "x_offset": 0,
                "y_offset": -200,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "0°"
            },
            {
                "content": "45°",
                "size": 40,
                "color": "#ff6b6b",
                "font_path": "fonts/Songti.ttc",
                "x_offset": 150,
                "y_offset": -150,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "45°"
            },
            {
                "content": "90°",
                "size": 40,
                "color": "#4ecdc4",
                "font_path": "fonts/Songti.ttc",
                "x_offset": 200,
                "y_offset": 0,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "90°"
            },
            {
                "content": "135°",
                "size": 40,
                "color": "#45b7d1",
                "font_path": "fonts/Songti.ttc",
                "x_offset": 150,
                "y_offset": 150,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "135°"
            },
            {
                "content": "旋转测试",
                "size": 60,
                "color": "#ffc048",
                "font_path": "fonts/Songti.ttc",
                "x_offset": 0,
                "y_offset": 0,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "315°"
            }
        ]
    }
    
    image = generate_image_from_config(config, "test_rotation.png")
    print("✅ 图片已生成: test_rotation.png")
    return image

def main():
    """主测试函数"""
    print("🚀 开始测试命令行生成器...")
    print("=" * 50)
    
    try:
        # 运行所有测试
        test_direct_config()
        test_json_config()
        test_vertical_text()
        test_rotation_effects()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！")
        print("\n生成的测试图片：")
        print("- test_direct.png      (基础字典配置测试)")
        print("- test_from_json.png   (JSON文件配置测试)")
        print("- test_vertical.png    (垂直文字测试)")
        print("- test_rotation.png    (旋转效果测试)")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main() 