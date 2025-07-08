import json
import argparse
import os
from PIL import Image
from core.image_generator import ImageGenerator


def generate_image_from_config(config, output_path=None):
    """
    根据配置字典生成图片
    
    Args:
        config (dict): 包含图片生成配置的字典
        output_path (str, optional): 输出文件路径，如果不提供则使用配置中的路径
    
    Returns:
        PIL.Image: 生成的图片对象
    """
    
    # 创建图片生成器实例
    generator = ImageGenerator()
    
    # 设置背景参数
    background = config.get('background', {})
    generator.width = background.get('width', 1920)
    generator.height = background.get('height', 1080)
    generator.main_color = background.get('main_color', '#000000')
    generator.border_color = background.get('border_color', '#FFFFFF')
    generator.border_height = background.get('border_height', 0)
    
    # 设置横线效果参数
    lines = config.get('lines', {})
    generator.add_lines = lines.get('enabled', False)
    generator.line_opacity = lines.get('opacity', 30)
    generator.line_color = lines.get('color', '#666666')
    generator.line_spacing = lines.get('spacing', 3)
    
    # 设置文字层
    text_layers = config.get('text_layers', [])
    generator.text_layers = []
    
    for layer_config in text_layers:
        layer = {
            'content': layer_config.get('content', ''),
            'size': layer_config.get('size', 48),
            'color': layer_config.get('color', '#FFFFFF'),
            'font_path': layer_config.get('font_path', ''),
            'x_offset': layer_config.get('x_offset', 0),
            'y_offset': layer_config.get('y_offset', 0),
            'direction': _map_direction(layer_config.get('direction', '水平 (左→右)')),
            'flip': _map_flip(layer_config.get('flip', '无')),
            'rotation': _map_rotation(layer_config.get('rotation', '0°'))
        }
        generator.text_layers.append(layer)
    
    # 生成图片
    image = generator.create_image()
    
    # 如果提供了输出路径，保存图片
    if output_path:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:  # 只有当有目录路径时才创建
            os.makedirs(output_dir, exist_ok=True)
        
        # 根据文件扩展名确定格式
        if output_path.lower().endswith('.png'):
            image.save(output_path, 'PNG')
        elif output_path.lower().endswith(('.jpg', '.jpeg')):
            # JPEG不支持透明度，转换为RGB
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # 使用alpha通道作为mask
                image = background
            image.save(output_path, 'JPEG', quality=95)
        else:
            # 默认保存为PNG
            image.save(output_path, 'PNG')
        
        print(f"图片已保存到: {output_path}")
    
    return image


def generate_image_from_json(json_path, output_path=None):
    """
    从JSON文件生成图片
    
    Args:
        json_path (str): JSON配置文件路径
        output_path (str, optional): 输出文件路径
    
    Returns:
        PIL.Image: 生成的图片对象
    """
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON配置文件不存在: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误: {e}")
    except Exception as e:
        raise Exception(f"读取JSON文件失败: {e}")
    
    # 如果没有指定输出路径，从配置文件中获取
    if not output_path:
        output_path = config.get('output_path')
        if not output_path:
            # 如果配置文件中也没有，则根据输入文件名生成一个默认路径
            base_name = os.path.basename(json_path)
            file_name, _ = os.path.splitext(base_name)
            output_path = os.path.join("output", f"{file_name}.png")
    
    return generate_image_from_config(config, output_path)


def _map_direction(direction_str):
    """映射文字方向字符串到内部格式"""
    direction_map = {
        '水平 (左→右)': 'horizontal_ltr',
        '垂直 (上→下)': 'vertical',
        '水平 (右→左)': 'horizontal_rtl'
    }
    return direction_map.get(direction_str, 'horizontal_ltr')


def _map_flip(flip_str):
    """映射翻转字符串到内部格式"""
    flip_map = {
        '无': 'none',
        '水平翻转': 'horizontal',
        '垂直翻转': 'vertical',
        '水平+垂直翻转': 'both'
    }
    return flip_map.get(flip_str, 'none')


def _map_rotation(rotation_str):
    """映射旋转字符串到角度值"""
    rotation_map = {
        '0°': 0,
        '45°': 45,
        '90°': 90,
        '135°': 135,
        '180°': 180,
        '225°': 225,
        '270°': 270,
        '315°': 315
    }
    return rotation_map.get(rotation_str, 0)


def create_example_config():
    """创建示例配置"""
    return {
        "background": {
            "width": 1920,
            "height": 1080,
            "main_color": "#000000",
            "border_color": "#FFFFFF",
            "border_height": 50
        },
        "lines": {
            "enabled": True,
            "opacity": 30,
            "color": "#666666",
            "spacing": 3
        },
        "text_layers": [
            {
                "content": "新房风格",
                "size": 80,
                "color": "#FFFFFF",
                "font_path": "assets/fonts/Songti.ttc",
                "x_offset": 0,
                "y_offset": -100,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "0°"
            },
            {
                "content": "SUBTITLE",
                "size": 40,
                "color": "#CCCCCC",
                "font_path": "assets/fonts/Songti.ttc",
                "x_offset": 0,
                "y_offset": 50,
                "direction": "水平 (左→右)",
                "flip": "无",
                "rotation": "0°"
            }
        ],
        "output_path": "output/example.png"
    }


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='新房风格背景生成器 - 命令行版本')
    parser.add_argument('--config', '-c', type=str, help='JSON配置文件路径')
    parser.add_argument('--output', '-o', type=str, help='输出图片路径')
    parser.add_argument('--example', action='store_true', help='生成示例配置文件')
    parser.add_argument('--example-output', type=str, default='configs/example_config.json', 
                       help='示例配置文件输出路径 (默认: configs/example_config.json)')
    
    args = parser.parse_args()
    
    if args.example:
        # 生成示例配置文件
        example_config = create_example_config()
        with open(args.example_output, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, ensure_ascii=False, indent=2)
        print(f"示例配置文件已生成: {args.example_output}")
        return
    
    if not args.config:
        print("错误: 请提供配置文件路径 (-c/--config) 或使用 --example 生成示例配置")
        return
    
    try:
        # 从JSON文件生成图片
        image = generate_image_from_json(args.config, args.output)
        print("图片生成成功!")
        
    except Exception as e:
        print(f"生成图片失败: {e}")


if __name__ == '__main__':
    main() 