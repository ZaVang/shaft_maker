from PIL import Image, ImageDraw
import math
from typing import List, Tuple, Union
from abc import ABC, abstractmethod

class Shape(ABC):
    """抽象形状基类"""
    def __init__(self, x, y, color, alpha=255, stroke_color=None, stroke_width=0):
        self.x = x
        self.y = y
        self.color = color
        self.alpha = alpha
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
    
    @abstractmethod
    def draw(self, draw: ImageDraw.Draw):
        pass
    
    def get_fill_color(self):
        """获取带透明度的填充颜色"""
        if len(self.color) == 3:
            return (*self.color, self.alpha)
        return self.color
    
    def get_stroke_color(self):
        """获取描边颜色"""
        if self.stroke_color:
            if len(self.stroke_color) == 3:
                return (*self.stroke_color, self.alpha)
            return self.stroke_color
        return None

class Circle(Shape):
    """圆形"""
    def __init__(self, x, y, radius, color, alpha=255, stroke_color=None, stroke_width=0):
        super().__init__(x, y, color, alpha, stroke_color, stroke_width)
        self.radius = radius
    
    def draw(self, draw: ImageDraw.Draw):
        bbox = [
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        ]
        
        # 直接使用RGBA颜色绘制（PIL会自动处理透明度）
        draw.ellipse(bbox, fill=self.get_fill_color(), 
                    outline=self.get_stroke_color(), width=self.stroke_width)

class Rectangle(Shape):
    """矩形"""
    def __init__(self, x, y, width, height, color, alpha=255, stroke_color=None, stroke_width=0, rotation=0):
        super().__init__(x, y, color, alpha, stroke_color, stroke_width)
        self.width = width
        self.height = height
        self.rotation = rotation
    
    def draw(self, draw: ImageDraw.Draw):
        if self.rotation == 0:
            bbox = [self.x, self.y, self.x + self.width, self.y + self.height]
            draw.rectangle(bbox, fill=self.get_fill_color(), 
                         outline=self.get_stroke_color(), width=self.stroke_width)
        else:
            # 旋转矩形需要计算四个角的坐标
            self._draw_rotated_rectangle(draw)
    
    def _draw_rotated_rectangle(self, draw):
        """绘制旋转的矩形"""
        angle = math.radians(self.rotation)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # 计算四个角相对于中心的坐标
        cx, cy = self.x + self.width/2, self.y + self.height/2
        corners = [
            (-self.width/2, -self.height/2),
            (self.width/2, -self.height/2),
            (self.width/2, self.height/2),
            (-self.width/2, self.height/2)
        ]
        
        # 旋转并转换为绝对坐标
        rotated_corners = []
        for x, y in corners:
            new_x = cx + x * cos_a - y * sin_a
            new_y = cy + x * sin_a + y * cos_a
            rotated_corners.append((new_x, new_y))
        
        draw.polygon(rotated_corners, fill=self.get_fill_color(), 
                    outline=self.get_stroke_color(), width=self.stroke_width)

class Triangle(Shape):
    """三角形"""
    def __init__(self, x1, y1, x2, y2, x3, y3, color, alpha=255, stroke_color=None, stroke_width=0):
        # 使用第一个点作为基准位置
        super().__init__(x1, y1, color, alpha, stroke_color, stroke_width)
        self.points = [(x1, y1), (x2, y2), (x3, y3)]
    
    def draw(self, draw: ImageDraw.Draw):
        draw.polygon(self.points, fill=self.get_fill_color(), 
                    outline=self.get_stroke_color(), width=self.stroke_width)

class RegularPolygon(Shape):
    """正多边形"""
    def __init__(self, x, y, radius, sides, color, alpha=255, stroke_color=None, stroke_width=0, rotation=0):
        super().__init__(x, y, color, alpha, stroke_color, stroke_width)
        self.radius = radius
        self.sides = sides
        self.rotation = rotation
    
    def draw(self, draw: ImageDraw.Draw):
        points = []
        angle_step = 2 * math.pi / self.sides
        start_angle = math.radians(self.rotation)
        
        for i in range(self.sides):
            angle = start_angle + i * angle_step
            x = self.x + self.radius * math.cos(angle)
            y = self.y + self.radius * math.sin(angle)
            points.append((x, y))
        
        draw.polygon(points, fill=self.get_fill_color(), 
                    outline=self.get_stroke_color(), width=self.stroke_width)

class Line(Shape):
    """线条"""
    def __init__(self, x1, y1, x2, y2, color, width=1, alpha=255):
        super().__init__(x1, y1, color, alpha)
        self.x2 = x2
        self.y2 = y2
        self.width = width
    
    def draw(self, draw: ImageDraw.Draw):
        draw.line([(self.x, self.y), (self.x2, self.y2)], 
                 fill=self.get_fill_color(), width=self.width)

class GeometricCanvas:
    """几何画布 - 管理图层和形状"""
    def __init__(self, width=1920, height=1080, background_color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.layers = []  # 图层列表，索引越大越在上层
    
    def add_shape(self, shape: Shape, layer_index=None):
        """添加形状到指定图层"""
        if layer_index is None:
            layer_index = len(self.layers)
        
        # 确保有足够的图层
        while len(self.layers) <= layer_index:
            self.layers.append([])
        
        self.layers[layer_index].append(shape)
    
    def insert_shape(self, shape: Shape, layer_index, position_in_layer):
        """在指定图层的指定位置插入形状"""
        while len(self.layers) <= layer_index:
            self.layers.append([])
        
        self.layers[layer_index].insert(position_in_layer, shape)
    
    def remove_shape(self, layer_index, shape_index):
        """移除指定形状"""
        if layer_index < len(self.layers) and shape_index < len(self.layers[layer_index]):
            self.layers[layer_index].pop(shape_index)
    
    def move_shape_to_layer(self, from_layer, shape_index, to_layer, to_position=None):
        """移动形状到另一个图层"""
        if from_layer < len(self.layers) and shape_index < len(self.layers[from_layer]):
            shape = self.layers[from_layer].pop(shape_index)
            
            if to_position is None:
                self.add_shape(shape, to_layer)
            else:
                self.insert_shape(shape, to_layer, to_position)
    
    def clear_layer(self, layer_index):
        """清空指定图层"""
        if layer_index < len(self.layers):
            self.layers[layer_index].clear()
    
    def get_layer_count(self):
        """获取图层数量"""
        return len(self.layers)
    
    def get_shapes_in_layer(self, layer_index):
        """获取指定图层的所有形状"""
        if layer_index < len(self.layers):
            return self.layers[layer_index].copy()
        return []
    
    def create_gradient_background(self, color1, color2, direction='horizontal'):
        """创建渐变背景"""
        img = Image.new('RGBA', (self.width, self.height))
        
        if direction == 'horizontal':
            for x in range(self.width):
                ratio = x / self.width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                
                for y in range(self.height):
                    img.putpixel((x, y), (r, g, b, 255))
        
        elif direction == 'vertical':
            for y in range(self.height):
                ratio = y / self.height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                
                for x in range(self.width):
                    img.putpixel((x, y), (r, g, b, 255))
        
        elif direction == 'diagonal':
            for x in range(self.width):
                for y in range(self.height):
                    ratio = (x + y) / (self.width + self.height)
                    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                    img.putpixel((x, y), (r, g, b, 255))
        
        return img
    
    def render(self, gradient_bg=None):
        """渲染画布"""
        if gradient_bg:
            img = gradient_bg.copy()
        else:
            img = Image.new('RGBA', (self.width, self.height), (*self.background_color, 255))
        
        draw = ImageDraw.Draw(img)
        
        # 按图层顺序绘制所有形状
        for layer in self.layers:
            for shape in layer:
                shape.draw(draw)
        
        return img
    
    def save(self, filename, gradient_bg=None):
        """保存图片"""
        img = self.render(gradient_bg)
        # 转换为RGB模式保存（去除alpha通道）
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, self.background_color)
            background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
            img = background
        
        img.save(filename)

# 使用示例和工具函数
def create_sample_composition():
    """创建示例组合"""
    canvas = GeometricCanvas(800, 600, (248, 249, 250))
    
    # 创建渐变背景
    gradient_bg = canvas.create_gradient_background((248, 249, 250), (233, 236, 239), 'diagonal')
    
    # 图层0：背景几何形状
    canvas.add_shape(Rectangle(50, 50, 200, 150, (108, 92, 231), alpha=80), 0)
    canvas.add_shape(Circle(500, 400, 80, (253, 121, 168), alpha=100), 0)
    
    # 图层1：中层形状
    canvas.add_shape(Triangle(200, 100, 350, 80, 275, 200, (0, 184, 148), alpha=120), 1)
    canvas.add_shape(RegularPolygon(600, 150, 60, 6, (253, 203, 110), alpha=90), 1)
    
    # 图层2：前景装饰
    canvas.add_shape(Circle(150, 400, 30, (225, 112, 85), stroke_color=(45, 52, 54), stroke_width=2), 2)
    canvas.add_shape(Line(100, 300, 700, 320, (99, 110, 114), width=2, alpha=150), 2)
    
    return canvas, gradient_bg

def interactive_example():
    """交互式示例"""
    canvas = GeometricCanvas(800, 600)
    
    # 你可以这样灵活地添加和调整形状：
    
    # 1. 创建基础形状
    circle1 = Circle(200, 200, 50, (255, 0, 0), alpha=150)
    rect1 = Rectangle(150, 150, 100, 100, (0, 255, 0), alpha=120)
    triangle1 = Triangle(100, 100, 200, 80, 150, 180, (0, 0, 255), alpha=100)
    
    # 2. 添加到不同图层（数字越大越在上层）
    canvas.add_shape(circle1, 0)      # 圆在最底层
    canvas.add_shape(rect1, 1)        # 矩形在中间
    canvas.add_shape(triangle1, 2)    # 三角形在最上层
    
    # 3. 如果你想改变层级关系，比如让圆覆盖三角形：
    canvas.move_shape_to_layer(0, 0, 3)  # 把圆从图层0移到图层3
    
    # 4. 添加更多形状
    pentagon = RegularPolygon(400, 300, 80, 5, (255, 255, 0), rotation=36)
    canvas.add_shape(pentagon, 1)
    
    # 5. 创建线条网格
    for i in range(0, 800, 100):
        line = Line(i, 0, i, 600, (200, 200, 200), alpha=50)
        canvas.add_shape(line, 0)  # 网格在底层
    
    return canvas

if __name__ == "__main__":
    # 示例1：预设组合
    canvas1, gradient_bg = create_sample_composition()
    canvas1.save('sample_composition.png', gradient_bg)
    
    # 示例2：交互式构建
    canvas2 = interactive_example()
    canvas2.save('interactive_example.png')
    
    print("示例图片已生成！")
    print(f"示例1图层数: {canvas1.get_layer_count()}")
    print(f"示例2图层数: {canvas2.get_layer_count()}")
    
    # 查看图层内容
    for i in range(canvas2.get_layer_count()):
        shapes = canvas2.get_shapes_in_layer(i)
        print(f"图层 {i}: {len(shapes)} 个形状")