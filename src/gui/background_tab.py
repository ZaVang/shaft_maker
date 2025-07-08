import tkinter as tk
from tkinter import ttk, colorchooser

class BackgroundTab:
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
    
    def setup_ui(self, parent):
        # 基本设置
        basic_frame = ttk.LabelFrame(parent, text="基本设置", padding="10")
        basic_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # 尺寸设置
        ttk.Label(basic_frame, text="宽度:").grid(row=0, column=0, sticky="w")
        self.width_var = tk.StringVar(value=str(self.generator.width))
        self.width_entry = ttk.Entry(basic_frame, textvariable=self.width_var, width=10)
        self.width_entry.grid(row=0, column=1, padx=5)
        self.width_entry.bind('<FocusOut>', self.update_width)
        
        ttk.Label(basic_frame, text="高度:").grid(row=0, column=2, sticky="w")
        self.height_var = tk.StringVar(value=str(self.generator.height))
        self.height_entry = ttk.Entry(basic_frame, textvariable=self.height_var, width=10)
        self.height_entry.grid(row=0, column=3, padx=5)
        self.height_entry.bind('<FocusOut>', self.update_height)
        
        # 颜色设置
        color_frame = ttk.LabelFrame(parent, text="颜色设置", padding="10")
        color_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # 主背景色
        ttk.Label(color_frame, text="主背景色:").grid(row=0, column=0, sticky="w")
        self.main_color_btn = tk.Button(color_frame, text="选择颜色", bg=self.generator.main_color,
                                       command=lambda: self.choose_color('main'))
        self.main_color_btn.grid(row=0, column=1, padx=5)
        
        # 边框色
        ttk.Label(color_frame, text="上下边框色:").grid(row=1, column=0, sticky="w")
        self.border_color_btn = tk.Button(color_frame, text="选择颜色", bg=self.generator.border_color,
                                         command=lambda: self.choose_color('border'))
        self.border_color_btn.grid(row=1, column=1, padx=5)
        
        # 边框高度
        ttk.Label(color_frame, text="边框高度 (像素):").grid(row=2, column=0, sticky="w")
        self.border_height_var = tk.StringVar(value=str(self.generator.border_height))
        self.border_height_entry = ttk.Entry(color_frame, textvariable=self.border_height_var, width=10)
        self.border_height_entry.grid(row=2, column=1, padx=5)
        self.border_height_entry.bind('<FocusOut>', self.update_border_height)
        
        # 横线设置
        line_frame = ttk.LabelFrame(parent, text="横线效果 (可选)", padding="10")
        line_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.lines_var = tk.BooleanVar(value=self.generator.add_lines)
        ttk.Checkbutton(line_frame, text="添加横线", variable=self.lines_var, 
                       command=self.update_lines).grid(row=0, column=0, sticky="w")
        
        ttk.Label(line_frame, text="横线颜色:").grid(row=1, column=0, sticky="w")
        self.line_color_btn = tk.Button(line_frame, text="选择颜色", bg=self.generator.line_color,
                                       command=lambda: self.choose_color('line'))
        self.line_color_btn.grid(row=1, column=1, padx=5)
        
        ttk.Label(line_frame, text="横线透明度 (0-100):").grid(row=2, column=0, sticky="w")
        self.line_opacity_var = tk.StringVar(value=str(self.generator.line_opacity))
        self.line_opacity_entry = ttk.Entry(line_frame, textvariable=self.line_opacity_var, width=10)
        self.line_opacity_entry.grid(row=2, column=1, padx=5)
        self.line_opacity_entry.bind('<FocusOut>', self.update_line_opacity)
        
        ttk.Label(line_frame, text="横线间隔 (像素):").grid(row=3, column=0, sticky="w")
        self.line_spacing_var = tk.StringVar(value=str(self.generator.line_spacing))
        self.line_spacing_entry = ttk.Entry(line_frame, textvariable=self.line_spacing_var, width=10)
        self.line_spacing_entry.grid(row=3, column=1, padx=5)
        self.line_spacing_entry.bind('<FocusOut>', self.update_line_spacing)
        
        # 预设按钮
        preset_frame = ttk.LabelFrame(parent, text="快速预设", padding="10")
        preset_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Button(preset_frame, text="黑底白字", command=lambda: self.apply_preset('black_white')).grid(row=0, column=0, padx=5)
        ttk.Button(preset_frame, text="白底黑字", command=lambda: self.apply_preset('white_black')).grid(row=0, column=1, padx=5)
        ttk.Button(preset_frame, text="红底白字", command=lambda: self.apply_preset('red_white')).grid(row=0, column=2, padx=5)
        ttk.Button(preset_frame, text="深蓝白字", command=lambda: self.apply_preset('blue_white')).grid(row=0, column=3, padx=5)
        
        # 功能说明
        help_frame = ttk.LabelFrame(parent, text="背景设置说明", padding="10")
        help_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        help_text = """
        ✨ 尺寸设置: 设置生成图片的宽度和高度
        🎨 颜色设置: 选择主背景色和边框颜色
        📏 边框设置: 可选的上下边框，设置高度为0则不显示
        📐 横线效果: 可选的横向细线，模仿新房风格的背景纹理
        🎯 预设样式: 快速应用常用的颜色搭配
        """
        help_label = ttk.Label(help_frame, text=help_text, justify="left", font=("", 9))
        help_label.grid(row=0, column=0, sticky="w")
    
    def update_width(self, event=None):
        try:
            self.generator.width = int(self.width_var.get())
        except ValueError:
            self.width_var.set(str(self.generator.width))
    
    def update_height(self, event=None):
        try:
            self.generator.height = int(self.height_var.get())
        except ValueError:
            self.height_var.set(str(self.generator.height))
    
    def update_border_height(self, event=None):
        try:
            self.generator.border_height = int(self.border_height_var.get())
        except ValueError:
            self.border_height_var.set(str(self.generator.border_height))
    
    def update_lines(self):
        self.generator.add_lines = self.lines_var.get()
    
    def update_line_opacity(self, event=None):
        try:
            self.generator.line_opacity = int(self.line_opacity_var.get())
        except ValueError:
            self.line_opacity_var.set(str(self.generator.line_opacity))
    
    def update_line_spacing(self, event=None):
        try:
            self.generator.line_spacing = int(self.line_spacing_var.get())
        except ValueError:
            self.line_spacing_var.set(str(self.generator.line_spacing))
    
    def choose_color(self, color_type):
        if color_type == 'main':
            color = colorchooser.askcolor(initialcolor=self.generator.main_color)
            if color[1]:
                self.generator.main_color = color[1]
                self.main_color_btn.config(bg=self.generator.main_color)
        elif color_type == 'border':
            color = colorchooser.askcolor(initialcolor=self.generator.border_color)
            if color[1]:
                self.generator.border_color = color[1]
                self.border_color_btn.config(bg=self.generator.border_color)
        elif color_type == 'line':
            color = colorchooser.askcolor(initialcolor=self.generator.line_color)
            if color[1]:
                self.generator.line_color = color[1]
                self.line_color_btn.config(bg=self.generator.line_color)
    
    def apply_preset(self, preset_type):
        presets = {
            'black_white': ('#000000', '#FFFFFF'),
            'white_black': ('#FFFFFF', '#000000'),
            'red_white': ('#8B0000', '#FFFFFF'),
            'blue_white': ('#1a1a2e', '#FFFFFF')
        }
        
        if preset_type in presets:
            main, border = presets[preset_type]
            self.generator.main_color = main
            self.generator.border_color = border
            
            self.main_color_btn.config(bg=self.generator.main_color)
            self.border_color_btn.config(bg=self.generator.border_color) 