import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from core.generate_geometry import Circle, Rectangle, Triangle, RegularPolygon, Line

class GeometryTab:
    def __init__(self, parent, generator):
        self.parent = parent
        self.generator = generator
        
        # 创建主框架
        self.frame = ttk.Frame(parent)
        
        # 创建滚动框架
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.setup_ui(scrollable_frame)
        
        # 配置滚动
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 初始化几何形状列表
        if not hasattr(self.generator, 'geometry_shapes'):
            self.generator.geometry_shapes = []
        
        self.update_shape_list()
    
    def setup_ui(self, parent):
        """设置用户界面"""
        # 形状添加区域
        add_frame = ttk.LabelFrame(parent, text="添加几何形状", padding="10")
        add_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # 形状类型选择
        ttk.Label(add_frame, text="形状类型:").grid(row=0, column=0, sticky="w")
        self.shape_type_var = tk.StringVar(value="circle")
        shape_combo = ttk.Combobox(add_frame, textvariable=self.shape_type_var,
                                  values=["circle", "rectangle", "triangle", "polygon", "line"],
                                  state="readonly", width=15)
        shape_combo.grid(row=0, column=1, padx=5)
        shape_combo.bind('<<ComboboxSelected>>', self.on_shape_type_changed)
        
        # 快速添加按钮
        button_frame = ttk.Frame(add_frame)
        button_frame.grid(row=0, column=2, columnspan=2, padx=10)
        
        ttk.Button(button_frame, text="添加形状", command=self.add_shape).pack(side="left", padx=2)
        ttk.Button(button_frame, text="添加随机形状", command=self.add_random_shape).pack(side="left", padx=2)
        
        # 形状参数设置
        param_frame = ttk.LabelFrame(parent, text="形状参数", padding="10")
        param_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.setup_parameter_widgets(param_frame)
        
        # 形状列表管理
        list_frame = ttk.LabelFrame(parent, text="形状列表", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # 形状列表
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=0, column=0, columnspan=4, sticky="ew", pady=5)
        
        self.shape_listbox = tk.Listbox(list_container, height=8, width=70)
        list_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.shape_listbox.yview)
        self.shape_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.shape_listbox.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")
        
        # 列表操作按钮
        list_button_frame = ttk.Frame(list_frame)
        list_button_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        ttk.Button(list_button_frame, text="编辑选中", command=self.edit_selected_shape).pack(side="left", padx=5)
        ttk.Button(list_button_frame, text="删除选中", command=self.delete_selected_shape).pack(side="left", padx=5)
        ttk.Button(list_button_frame, text="清空所有", command=self.clear_all_shapes).pack(side="left", padx=5)
        ttk.Button(list_button_frame, text="上移", command=self.move_shape_up).pack(side="left", padx=5)
        ttk.Button(list_button_frame, text="下移", command=self.move_shape_down).pack(side="left", padx=5)
        
        # 渐变背景设置
        gradient_frame = ttk.LabelFrame(parent, text="渐变背景", padding="10")
        gradient_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.enable_gradient_var = tk.BooleanVar()
        ttk.Checkbutton(gradient_frame, text="启用渐变背景", 
                       variable=self.enable_gradient_var,
                       command=self.sync_gradient_settings).grid(row=0, column=0, sticky="w")
        
        ttk.Label(gradient_frame, text="起始颜色:").grid(row=1, column=0, sticky="w")
        self.gradient_color1 = "#f8f9fa"
        self.gradient_btn1 = tk.Button(gradient_frame, text="选择颜色", bg=self.gradient_color1,
                                      command=lambda: self.choose_gradient_color(1))
        self.gradient_btn1.grid(row=1, column=1, padx=5)
        
        ttk.Label(gradient_frame, text="结束颜色:").grid(row=1, column=2, sticky="w")
        self.gradient_color2 = "#e9ecef"
        self.gradient_btn2 = tk.Button(gradient_frame, text="选择颜色", bg=self.gradient_color2,
                                      command=lambda: self.choose_gradient_color(2))
        self.gradient_btn2.grid(row=1, column=3, padx=5)
        
        ttk.Label(gradient_frame, text="方向:").grid(row=2, column=0, sticky="w")
        self.gradient_direction_var = tk.StringVar(value="horizontal")
        direction_combo = ttk.Combobox(gradient_frame, textvariable=self.gradient_direction_var,
                                     values=["horizontal", "vertical", "diagonal"],
                                     state="readonly", width=10)
        direction_combo.grid(row=2, column=1, padx=5)
        direction_combo.bind('<<ComboboxSelected>>', lambda e: self.sync_gradient_settings())
        
        # 预设样式
        preset_frame = ttk.LabelFrame(parent, text="快速预设", padding="10")
        preset_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        preset_buttons = ttk.Frame(preset_frame)
        preset_buttons.grid(row=0, column=0, sticky="w")
        
        ttk.Button(preset_buttons, text="简约几何", command=self.preset_minimal).pack(side="left", padx=5)
        ttk.Button(preset_buttons, text="彩色形状", command=self.preset_colorful).pack(side="left", padx=5)
        ttk.Button(preset_buttons, text="线条艺术", command=self.preset_lines).pack(side="left", padx=5)
        ttk.Button(preset_buttons, text="几何网格", command=self.preset_grid).pack(side="left", padx=5)
        
        # 使用说明
        help_frame = ttk.LabelFrame(parent, text="使用说明", padding="10")
        help_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        help_text = """
        ✨ 几何形状功能说明:
        
        📐 支持形状: 圆形、矩形、三角形、正多边形、线条
        🎨 颜色设置: 填充色、描边色、透明度控制
        📍 位置调节: 精确设置X、Y坐标
        🔄 旋转效果: 支持任意角度旋转
        📏 尺寸控制: 灵活调整大小参数
        
        💡 使用提示:
        • 形状按添加顺序层叠显示（后添加的在上层）
        • 可以通过上移/下移调整层级关系
        • 透明度设置让形状可以相互重叠产生混合效果
        • 渐变背景可以让整体效果更丰富
        • 在"预览和保存"中查看最终效果
        """
        help_label = ttk.Label(help_frame, text=help_text, justify="left", font=("", 9))
        help_label.grid(row=0, column=0, sticky="w")
    
    def setup_parameter_widgets(self, parent):
        """设置参数控件"""
        # 基础位置参数
        basic_frame = ttk.Frame(parent)
        basic_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=5)
        
        ttk.Label(basic_frame, text="X坐标:").grid(row=0, column=0, sticky="w", padx=2)
        self.x_var = tk.StringVar(value="100")
        ttk.Entry(basic_frame, textvariable=self.x_var, width=8).grid(row=0, column=1, padx=2)
        
        ttk.Label(basic_frame, text="Y坐标:").grid(row=0, column=2, sticky="w", padx=2)
        self.y_var = tk.StringVar(value="100")
        ttk.Entry(basic_frame, textvariable=self.y_var, width=8).grid(row=0, column=3, padx=2)
        
        # 颜色参数
        color_frame = ttk.Frame(parent)
        color_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        
        ttk.Label(color_frame, text="填充色:").grid(row=0, column=0, sticky="w", padx=2)
        self.fill_color = "#6c5ce7"
        self.fill_color_btn = tk.Button(color_frame, text="选择", bg=self.fill_color, width=8,
                                       command=lambda: self.choose_color('fill'))
        self.fill_color_btn.grid(row=0, column=1, padx=2)
        
        ttk.Label(color_frame, text="描边色:").grid(row=0, column=2, sticky="w", padx=2)
        self.stroke_color = "#2d3436"
        self.stroke_color_btn = tk.Button(color_frame, text="选择", bg=self.stroke_color, width=8,
                                         command=lambda: self.choose_color('stroke'))
        self.stroke_color_btn.grid(row=0, column=3, padx=2)
        
        # 透明度和描边宽度
        alpha_frame = ttk.Frame(parent)
        alpha_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=5)
        
        ttk.Label(alpha_frame, text="透明度(0-255):").grid(row=0, column=0, sticky="w", padx=2)
        self.alpha_var = tk.StringVar(value="200")
        ttk.Entry(alpha_frame, textvariable=self.alpha_var, width=8).grid(row=0, column=1, padx=2)
        
        ttk.Label(alpha_frame, text="描边宽度:").grid(row=0, column=2, sticky="w", padx=2)
        self.stroke_width_var = tk.StringVar(value="0")
        ttk.Entry(alpha_frame, textvariable=self.stroke_width_var, width=8).grid(row=0, column=3, padx=2)
        
        # 形状特定参数容器
        self.specific_frame = ttk.Frame(parent)
        self.specific_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)
        
        # 初始化圆形参数
        self.setup_circle_params()
    
    def setup_circle_params(self):
        """设置圆形参数"""
        self.clear_specific_params()
        ttk.Label(self.specific_frame, text="半径:").grid(row=0, column=0, sticky="w", padx=2)
        self.radius_var = tk.StringVar(value="50")
        ttk.Entry(self.specific_frame, textvariable=self.radius_var, width=10).grid(row=0, column=1, padx=2)
    
    def setup_rectangle_params(self):
        """设置矩形参数"""
        self.clear_specific_params()
        ttk.Label(self.specific_frame, text="宽度:").grid(row=0, column=0, sticky="w", padx=2)
        self.width_var = tk.StringVar(value="100")
        ttk.Entry(self.specific_frame, textvariable=self.width_var, width=8).grid(row=0, column=1, padx=2)
        
        ttk.Label(self.specific_frame, text="高度:").grid(row=0, column=2, sticky="w", padx=2)
        self.height_var = tk.StringVar(value="80")
        ttk.Entry(self.specific_frame, textvariable=self.height_var, width=8).grid(row=0, column=3, padx=2)
        
        ttk.Label(self.specific_frame, text="旋转角度:").grid(row=1, column=0, sticky="w", padx=2)
        self.rotation_var = tk.StringVar(value="0")
        ttk.Entry(self.specific_frame, textvariable=self.rotation_var, width=8).grid(row=1, column=1, padx=2)
    
    def setup_triangle_params(self):
        """设置三角形参数"""
        self.clear_specific_params()
        for i, label in enumerate(["点1", "点2", "点3"]):
            ttk.Label(self.specific_frame, text=f"{label} X:").grid(row=i, column=0, sticky="w", padx=2)
            var = tk.StringVar(value=str(100 + i * 50))
            setattr(self, f"x{i+1}_var", var)
            ttk.Entry(self.specific_frame, textvariable=var, width=8).grid(row=i, column=1, padx=2)
            
            ttk.Label(self.specific_frame, text=f"{label} Y:").grid(row=i, column=2, sticky="w", padx=2)
            var = tk.StringVar(value=str(100 + (i % 2) * 50))
            setattr(self, f"y{i+1}_var", var)
            ttk.Entry(self.specific_frame, textvariable=var, width=8).grid(row=i, column=3, padx=2)
    
    def setup_polygon_params(self):
        """设置正多边形参数"""
        self.clear_specific_params()
        ttk.Label(self.specific_frame, text="边数:").grid(row=0, column=0, sticky="w", padx=2)
        self.sides_var = tk.StringVar(value="6")
        ttk.Entry(self.specific_frame, textvariable=self.sides_var, width=8).grid(row=0, column=1, padx=2)
        
        ttk.Label(self.specific_frame, text="半径:").grid(row=0, column=2, sticky="w", padx=2)
        self.poly_radius_var = tk.StringVar(value="60")
        ttk.Entry(self.specific_frame, textvariable=self.poly_radius_var, width=8).grid(row=0, column=3, padx=2)
        
        ttk.Label(self.specific_frame, text="旋转角度:").grid(row=1, column=0, sticky="w", padx=2)
        self.poly_rotation_var = tk.StringVar(value="0")
        ttk.Entry(self.specific_frame, textvariable=self.poly_rotation_var, width=8).grid(row=1, column=1, padx=2)
    
    def setup_line_params(self):
        """设置线条参数"""
        self.clear_specific_params()
        ttk.Label(self.specific_frame, text="终点X:").grid(row=0, column=0, sticky="w", padx=2)
        self.x2_var = tk.StringVar(value="200")
        ttk.Entry(self.specific_frame, textvariable=self.x2_var, width=8).grid(row=0, column=1, padx=2)
        
        ttk.Label(self.specific_frame, text="终点Y:").grid(row=0, column=2, sticky="w", padx=2)
        self.y2_var = tk.StringVar(value="100")
        ttk.Entry(self.specific_frame, textvariable=self.y2_var, width=8).grid(row=0, column=3, padx=2)
        
        ttk.Label(self.specific_frame, text="线条宽度:").grid(row=1, column=0, sticky="w", padx=2)
        self.line_width_var = tk.StringVar(value="2")
        ttk.Entry(self.specific_frame, textvariable=self.line_width_var, width=8).grid(row=1, column=1, padx=2)
    
    def clear_specific_params(self):
        """清空特定参数控件"""
        for widget in self.specific_frame.winfo_children():
            widget.destroy()
    
    def on_shape_type_changed(self, event=None):
        """形状类型改变时的回调"""
        shape_type = self.shape_type_var.get()
        if shape_type == "circle":
            self.setup_circle_params()
        elif shape_type == "rectangle":
            self.setup_rectangle_params()
        elif shape_type == "triangle":
            self.setup_triangle_params()
        elif shape_type == "polygon":
            self.setup_polygon_params()
        elif shape_type == "line":
            self.setup_line_params()
    
    def choose_color(self, color_type):
        """选择颜色"""
        if color_type == 'fill':
            color = colorchooser.askcolor(initialcolor=self.fill_color)
            if color[1]:
                self.fill_color = color[1]
                self.fill_color_btn.config(bg=self.fill_color)
        elif color_type == 'stroke':
            color = colorchooser.askcolor(initialcolor=self.stroke_color)
            if color[1]:
                self.stroke_color = color[1]
                self.stroke_color_btn.config(bg=self.stroke_color)
    
    def choose_gradient_color(self, color_num):
        """选择渐变颜色"""
        if color_num == 1:
            color = colorchooser.askcolor(initialcolor=self.gradient_color1)
            if color[1]:
                self.gradient_color1 = color[1]
                self.gradient_btn1.config(bg=self.gradient_color1)
                self.sync_gradient_settings()
        elif color_num == 2:
            color = colorchooser.askcolor(initialcolor=self.gradient_color2)
            if color[1]:
                self.gradient_color2 = color[1]
                self.gradient_btn2.config(bg=self.gradient_color2)
                self.sync_gradient_settings()
    
    def sync_gradient_settings(self):
        """同步渐变设置到图像生成器"""
        self.generator.enable_gradient = self.enable_gradient_var.get()
        self.generator.gradient_color1 = self.gradient_color1
        self.generator.gradient_color2 = self.gradient_color2
        self.generator.gradient_direction = self.gradient_direction_var.get()
    
    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def add_shape(self):
        """添加形状"""
        try:
            shape_type = self.shape_type_var.get()
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            fill_color = self.hex_to_rgb(self.fill_color)
            alpha = int(self.alpha_var.get())
            stroke_color = self.hex_to_rgb(self.stroke_color) if self.stroke_width_var.get() != "0" else None
            stroke_width = int(self.stroke_width_var.get())
            
            shape = None
            
            if shape_type == "circle":
                radius = int(self.radius_var.get())
                shape = Circle(x, y, radius, fill_color, alpha, stroke_color, stroke_width)
            
            elif shape_type == "rectangle":
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                rotation = int(self.rotation_var.get())
                shape = Rectangle(x, y, width, height, fill_color, alpha, stroke_color, stroke_width, rotation)
            
            elif shape_type == "triangle":
                x1 = int(self.x1_var.get())
                y1 = int(self.y1_var.get())
                x2 = int(self.x2_var.get())
                y2 = int(self.y2_var.get())
                x3 = int(self.x3_var.get())
                y3 = int(self.y3_var.get())
                shape = Triangle(x1, y1, x2, y2, x3, y3, fill_color, alpha, stroke_color, stroke_width)
            
            elif shape_type == "polygon":
                sides = int(self.sides_var.get())
                radius = int(self.poly_radius_var.get())
                rotation = int(self.poly_rotation_var.get())
                shape = RegularPolygon(x, y, radius, sides, fill_color, alpha, stroke_color, stroke_width, rotation)
            
            elif shape_type == "line":
                x2 = int(self.x2_var.get())
                y2 = int(self.y2_var.get())
                width = int(self.line_width_var.get())
                shape = Line(x, y, x2, y2, fill_color, width, alpha)
            
            if shape:
                self.generator.geometry_shapes.append(shape)
                self.update_shape_list()
                self.sync_preview()
                
        except ValueError as e:
            messagebox.showerror("错误", f"参数错误: {str(e)}")
    
    def add_random_shape(self):
        """添加随机形状"""
        import random
        
        # 随机选择形状类型
        shape_types = ["circle", "rectangle", "triangle", "polygon", "line"]
        shape_type = random.choice(shape_types)
        
        # 随机颜色
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22"]
        color = random.choice(colors)
        
        # 随机位置
        x = random.randint(50, self.generator.width - 150)
        y = random.randint(50, self.generator.height - 150)
        
        # 设置参数
        self.shape_type_var.set(shape_type)
        self.on_shape_type_changed()
        self.x_var.set(str(x))
        self.y_var.set(str(y))
        self.fill_color = color
        self.fill_color_btn.config(bg=color)
        self.alpha_var.set(str(random.randint(100, 255)))
        
        # 根据形状类型设置特定参数
        if shape_type == "circle":
            self.radius_var.set(str(random.randint(20, 80)))
        elif shape_type == "rectangle":
            self.width_var.set(str(random.randint(50, 150)))
            self.height_var.set(str(random.randint(50, 150)))
            self.rotation_var.set(str(random.randint(0, 360)))
        elif shape_type == "polygon":
            self.sides_var.set(str(random.randint(3, 8)))
            self.poly_radius_var.set(str(random.randint(30, 80)))
        
        # 添加形状
        self.add_shape()
    
    def update_shape_list(self):
        """更新形状列表"""
        self.shape_listbox.delete(0, tk.END)
        for i, shape in enumerate(self.generator.geometry_shapes):
            shape_type = shape.__class__.__name__
            shape_info = self.get_shape_info(shape)
            display_text = f"{i+1}. {shape_type} - {shape_info}"
            self.shape_listbox.insert(tk.END, display_text)
    
    def get_shape_info(self, shape):
        """获取形状信息字符串"""
        if isinstance(shape, Circle):
            return f"中心({shape.x}, {shape.y}), 半径{shape.radius}"
        elif isinstance(shape, Rectangle):
            return f"位置({shape.x}, {shape.y}), 尺寸{shape.width}x{shape.height}"
        elif isinstance(shape, Triangle):
            return f"三点: ({shape.points[0][0]}, {shape.points[0][1]}), ({shape.points[1][0]}, {shape.points[1][1]}), ({shape.points[2][0]}, {shape.points[2][1]})"
        elif isinstance(shape, RegularPolygon):
            return f"中心({shape.x}, {shape.y}), {shape.sides}边形, 半径{shape.radius}"
        elif isinstance(shape, Line):
            return f"从({shape.x}, {shape.y})到({shape.x2}, {shape.y2})"
        return "未知形状"
    
    def edit_selected_shape(self):
        """编辑选中的形状"""
        selection = self.shape_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的形状")
            return
        
        shape_index = selection[0]
        shape = self.generator.geometry_shapes[shape_index]
        
        # 创建编辑对话框
        self.create_edit_dialog(shape, shape_index)
    
    def create_edit_dialog(self, shape, shape_index):
        """创建编辑对话框"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("编辑形状")
        dialog.geometry("400x500")
        dialog.resizable(False, False)
        
        # 使对话框模态
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # 根据形状类型设置编辑界面
        # 这里可以扩展更详细的编辑功能
        ttk.Label(dialog, text=f"编辑 {shape.__class__.__name__}", 
                 font=("", 12, "bold")).pack(pady=10)
        
        # 基本属性编辑
        basic_frame = ttk.LabelFrame(dialog, text="基本属性", padding="10")
        basic_frame.pack(fill="x", padx=10, pady=5)
        
        # 透明度
        ttk.Label(basic_frame, text="透明度(0-255):").grid(row=0, column=0, sticky="w")
        alpha_var = tk.StringVar(value=str(shape.alpha))
        ttk.Entry(basic_frame, textvariable=alpha_var, width=10).grid(row=0, column=1, padx=5)
        
        # 保存和取消按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def save_changes():
            try:
                shape.alpha = int(alpha_var.get())
                self.update_shape_list()
                self.sync_preview()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数值")
        
        ttk.Button(button_frame, text="保存", command=save_changes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side="left", padx=5)
    
    def delete_selected_shape(self):
        """删除选中的形状"""
        selection = self.shape_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的形状")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的形状吗？"):
            shape_index = selection[0]
            del self.generator.geometry_shapes[shape_index]
            self.update_shape_list()
            self.sync_preview()
    
    def clear_all_shapes(self):
        """清空所有形状"""
        if messagebox.askyesno("确认", "确定要清空所有形状吗？"):
            self.generator.geometry_shapes.clear()
            self.update_shape_list()
            self.sync_preview()
    
    def move_shape_up(self):
        """上移形状"""
        selection = self.shape_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要移动的形状")
            return
        
        shape_index = selection[0]
        if shape_index > 0:
            shapes = self.generator.geometry_shapes
            shapes[shape_index], shapes[shape_index-1] = shapes[shape_index-1], shapes[shape_index]
            self.update_shape_list()
            self.shape_listbox.selection_set(shape_index-1)
            self.sync_preview()
    
    def move_shape_down(self):
        """下移形状"""
        selection = self.shape_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要移动的形状")
            return
        
        shape_index = selection[0]
        shapes = self.generator.geometry_shapes
        if shape_index < len(shapes) - 1:
            shapes[shape_index], shapes[shape_index+1] = shapes[shape_index+1], shapes[shape_index]
            self.update_shape_list()
            self.shape_listbox.selection_set(shape_index+1)
            self.sync_preview()
    
    def preset_minimal(self):
        """简约几何预设"""
        self.generator.geometry_shapes.clear()
        
        # 添加一些简约的形状
        self.generator.geometry_shapes.extend([
            Circle(200, 200, 80, (108, 92, 231), 150),
            Rectangle(400, 150, 120, 100, (253, 121, 168), 120),
            RegularPolygon(600, 300, 60, 6, (0, 184, 148), 100)
        ])
        
        self.update_shape_list()
        self.sync_preview()
    
    def preset_colorful(self):
        """彩色形状预设"""
        self.generator.geometry_shapes.clear()
        
        colors = [(231, 76, 60), (52, 152, 219), (46, 204, 113), (243, 156, 18), (155, 89, 182)]
        
        for i, color in enumerate(colors):
            x = 150 + i * 100
            y = 200 + (i % 2) * 100
            self.generator.geometry_shapes.append(Circle(x, y, 40, color, 180))
        
        self.update_shape_list()
        self.sync_preview()
    
    def preset_lines(self):
        """线条艺术预设"""
        self.generator.geometry_shapes.clear()
        
        # 创建线条网格
        for i in range(5):
            self.generator.geometry_shapes.append(
                Line(100 + i * 50, 100, 100 + i * 50, 400, (99, 110, 114), 2, 120)
            )
            self.generator.geometry_shapes.append(
                Line(100, 100 + i * 50, 400, 100 + i * 50, (99, 110, 114), 2, 120)
            )
        
        self.update_shape_list()
        self.sync_preview()
    
    def preset_grid(self):
        """几何网格预设"""
        self.generator.geometry_shapes.clear()
        
        # 创建网格模式
        for i in range(4):
            for j in range(3):
                x = 150 + i * 120
                y = 150 + j * 120
                if (i + j) % 2 == 0:
                    self.generator.geometry_shapes.append(Circle(x, y, 30, (108, 92, 231), 150))
                else:
                    self.generator.geometry_shapes.append(Rectangle(x-25, y-25, 50, 50, (253, 121, 168), 150))
        
        self.update_shape_list()
        self.sync_preview()
    
    def sync_preview(self):
        """同步预览"""
        # 如果存在预览标签页，通知其更新
        if hasattr(self, 'preview_tab') and self.preview_tab:
            self.preview_tab.auto_preview() 