from PIL import Image, ImageDraw, ImageFont
import os

class ImageGenerator:
    def __init__(self):
        # 默认设置
        self.width = 1920
        self.height = 1080
        self.main_color = "#000000"
        self.border_color = "#FFFFFF"
        self.border_height = 0
        self.add_lines = False
        self.line_opacity = 30
        self.line_color = "#666666"
        self.line_spacing = 3
        
        # 文字层列表
        self.text_layers = []
        
        # 文字方向和效果选项
        self.text_directions = ['水平 (左→右)', '垂直 (上→下)', '水平 (右→左)']
        self.flip_options = ['无', '水平翻转', '垂直翻转', '水平+垂直翻转']
        self.rotation_options = ['0°', '45°', '90°', '135°', '180°', '225°', '270°', '315°']
    
    def create_image(self):
        """创建完整的图像"""
        # 创建图像
        img = Image.new('RGB', (self.width, self.height), self.main_color)
        draw = ImageDraw.Draw(img)
        
        # 添加上下边框
        if self.border_height > 0:
            # 上边框
            draw.rectangle([0, 0, self.width, self.border_height], fill=self.border_color)
            # 下边框
            draw.rectangle([0, self.height-self.border_height, self.width, self.height], fill=self.border_color)
        
        # 添加横线效果
        if self.add_lines and self.line_spacing > 0:
            # 计算横线颜色（应用透明度）
            main_rgb = self.hex_to_rgb(self.main_color)
            line_rgb = self.hex_to_rgb(self.line_color)
            
            # 混合颜色（模拟透明度效果）
            alpha = self.line_opacity / 100.0
            blended_rgb = tuple(
                int(line_rgb[i] * alpha + main_rgb[i] * (1 - alpha))
                for i in range(3)
            )
            blended_color = f"#{blended_rgb[0]:02x}{blended_rgb[1]:02x}{blended_rgb[2]:02x}"
            
            # 绘制细横线，使用用户设定的间隔
            for y in range(self.border_height, self.height - self.border_height, self.line_spacing):
                draw.line([0, y, self.width, y], fill=blended_color, width=1)
        
        # 渲染所有文字层
        for layer in self.text_layers:
            text_img = self.create_text_layer_image(layer)
            if text_img:
                # 计算粘贴位置
                text_width, text_height = text_img.size
                x = (self.width - text_width) // 2 + layer['x_offset']
                y = (self.height - text_height) // 2 + layer['y_offset']
                
                # 粘贴文字图像
                if text_img.mode == 'RGBA':
                    img.paste(text_img, (x, y), text_img)
                else:
                    img.paste(text_img, (x, y))
        
        return img
    
    def create_text_layer_image(self, layer):
        """创建单个文字层的图像"""
        text_content = layer['content']
        if not text_content.strip():
            return None
        
        text_size = layer['size']
        text_color = layer['color']
        font_path = layer['font_path']
        direction = layer.get('direction', 'horizontal_ltr')
        flip = layer.get('flip', 'none')
        rotation = layer.get('rotation', 0)
        
        # 加载字体
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, text_size)
            else:
                # 优先使用本地中文字体
                try:
                    # 尝试加载本地songti.ttc字体
                    local_font_path = os.path.join("fonts", "Songti.ttc")
                    if os.path.exists(local_font_path):
                        font = ImageFont.truetype(local_font_path, text_size)
                    else:
                        raise FileNotFoundError("本地字体文件不存在")
                except:
                    try:
                        # Windows系统字体
                        font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", text_size)
                    except:
                        try:
                            # macOS中文字体
                            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", text_size)
                        except:
                            try:
                                # 备用macOS字体
                                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", text_size)
                            except:
                                try:
                                    # Linux
                                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", text_size)
                                except:
                                    # 默认字体
                                    font = ImageFont.load_default()
        except Exception as e:
            print(f"字体加载失败: {e}")
            font = ImageFont.load_default()
        
        # 根据文字方向创建基础文字图像
        if direction == 'vertical':
            text_img = self.create_vertical_text(text_content, font, text_color)
        elif direction == 'horizontal_rtl':
            text_img = self.create_rtl_text(text_content, font, text_color)
        else:  # horizontal_ltr
            text_img = self.create_horizontal_text(text_content, font, text_color)
        
        if text_img is None:
            return None
        
        # 应用旋转
        if rotation != 0:
            text_img = text_img.rotate(-rotation, expand=True)  # 注意方向
        
        # 应用翻转
        if flip == 'horizontal':
            text_img = text_img.transpose(Image.FLIP_LEFT_RIGHT)
        elif flip == 'vertical':
            text_img = text_img.transpose(Image.FLIP_TOP_BOTTOM)
        elif flip == 'both':
            text_img = text_img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        
        return text_img
    
    def create_horizontal_text(self, text, font, color):
        """创建水平文字图像"""
        # 计算文字尺寸
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if text_width <= 0 or text_height <= 0:
            return None
        
        # 增加足够的边距以避免文字被截断，特别是基线以下的部分
        padding_x = 30
        padding_y = max(40, text_height // 2)  # 增加垂直边距
        
        # 创建文字图像
        text_img = Image.new('RGBA', (text_width + padding_x * 2, text_height + padding_y * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        
        # 使用更大的偏移量，确保文字不被截断
        text_x = padding_x - bbox[0]  # 补偿bbox的左偏移
        text_y = padding_y - bbox[1]  # 补偿bbox的上偏移
        text_draw.text((text_x, text_y), text, fill=color, font=font)
        
        return text_img
    
    def create_vertical_text(self, text, font, color):
        """创建垂直文字图像（从上到下）"""
        if not text:
            return None
        
        # 计算单个字符的最大尺寸和边界信息
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        max_char_width = 0
        char_info = []  # 存储每个字符的尺寸和边界信息
        
        for char in text:
            bbox = temp_draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            max_char_width = max(max_char_width, char_width)
            char_info.append({
                'char': char,
                'bbox': bbox,
                'width': char_width,
                'height': char_height
            })
        
        # 改进间距计算
        line_spacing = max(8, int(max([info['height'] for info in char_info]) * 0.3))
        total_height = sum([info['height'] for info in char_info]) + (len(text) - 1) * line_spacing
        
        if max_char_width <= 0 or total_height <= 0:
            return None
        
        # 增加足够的边距
        padding_x = max(30, max_char_width // 2)
        padding_y = 40
        
        # 创建垂直文字图像
        text_img = Image.new('RGBA', (max_char_width + padding_x * 2, total_height + padding_y * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        
        current_y = padding_y
        for i, info in enumerate(char_info):
            char = info['char']
            bbox = info['bbox']
            char_width = info['width']
            char_height = info['height']
            
            # 计算字符居中位置，并补偿边界偏移
            char_x = (max_char_width - char_width) // 2 + padding_x - bbox[0]
            char_y = current_y - bbox[1]  # 补偿bbox的上偏移
            
            text_draw.text((char_x, char_y), char, fill=color, font=font)
            current_y += char_height
            
            # 添加间距（除了最后一个字符）
            if i < len(text) - 1:
                current_y += line_spacing
        
        return text_img
    
    def create_rtl_text(self, text, font, color):
        """创建从右到左的文字图像"""
        # 对于基础实现，我们反转字符串
        # 更复杂的实现可能需要考虑双向文字算法(Bidi)
        reversed_text = text[::-1]
        return self.create_horizontal_text(reversed_text, font, color)
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def hex_to_rgba(self, hex_color, opacity):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        alpha = int(255 * opacity / 100)
        return (r, g, b, alpha) 