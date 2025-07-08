import tkinter as tk
from tkinter import ttk, messagebox
import os
from gui.text_layer_dialog import TextLayerDialog

class TextTab:
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
        
        # 初始化时添加一个默认文字层
        if not self.generator.text_layers:
            # 设置默认字体路径
            default_font_path = None
            if os.path.exists("assets/fonts/Songti.ttc"):
                default_font_path = "assets/fonts/Songti.ttc"
            
            self.generator.text_layers.append({
                'content': '示例文字',
                'size': 120,
                'color': '#FFFFFF',
                'font_path': default_font_path,
                'x_offset': 0,
                'y_offset': 0,
                'direction': 'horizontal_ltr',
                'flip': 'none',
                'rotation': 0
            })
        
        self.update_layer_list()
    
    def setup_ui(self, parent):
        # 文字层设置
        text_frame = ttk.LabelFrame(parent, text="文字层管理", padding="10")
        text_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # 文字层列表
        ttk.Label(text_frame, text="当前文字层:").grid(row=0, column=0, sticky="nw", pady=5)
        
        # 创建文字层列表框
        list_frame = ttk.Frame(text_frame)
        list_frame.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        self.layer_listbox = tk.Listbox(list_frame, height=8, width=60)
        scrollbar_list = ttk.Scrollbar(list_frame, orient="vertical", command=self.layer_listbox.yview)
        self.layer_listbox.configure(yscrollcommand=scrollbar_list.set)
        
        self.layer_listbox.pack(side="left", fill="both", expand=True)
        scrollbar_list.pack(side="right", fill="y")
        
        # 文字层操作按钮
        button_frame = ttk.Frame(text_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="新增文字层", command=self.add_text_layer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="编辑选中层", command=self.edit_text_layer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="删除选中层", command=self.delete_text_layer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="上移", command=self.move_layer_up).pack(side="left", padx=5)
        ttk.Button(button_frame, text="下移", command=self.move_layer_down).pack(side="left", padx=5)
        
        # 功能说明
        help_frame = ttk.LabelFrame(parent, text="文字层功能说明", padding="10")
        help_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        help_text = """
        ✨ 文字方向: 支持水平、垂直、从右到左三种排列方式
        🔄 翻转效果: 支持水平、垂直翻转以及组合翻转
        🎯 旋转角度: 支持8个方向的旋转 (0°-315°)
        🎨 多层文字: 无限叠加不同样式的文字层
        📍 位置调节: 精确控制每一层文字的位置
        🎭 字体设置: 支持自定义字体文件 (.ttf, .ttc, .otf)
        
        💡 使用技巧:
        • 先在"背景设置"中调整基础背景
        • 在这里添加和编辑文字层
        • 最后在"预览和保存"中查看效果
        • 可以通过上移/下移调整文字层的显示顺序
        """
        help_label = ttk.Label(help_frame, text=help_text, justify="left", font=("", 9))
        help_label.grid(row=0, column=0, sticky="w")
        
        # 快速文字样式预设
        preset_frame = ttk.LabelFrame(parent, text="快速文字样式", padding="10")
        preset_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        preset_buttons_frame = ttk.Frame(preset_frame)
        preset_buttons_frame.grid(row=0, column=0, sticky="w")
        
        ttk.Button(preset_buttons_frame, text="大标题样式", 
                  command=lambda: self.add_preset_layer("大标题", 180, "#FFFFFF")).pack(side="left", padx=5)
        ttk.Button(preset_buttons_frame, text="副标题样式", 
                  command=lambda: self.add_preset_layer("副标题", 120, "#CCCCCC")).pack(side="left", padx=5)
        ttk.Button(preset_buttons_frame, text="正文样式", 
                  command=lambda: self.add_preset_layer("正文内容", 80, "#FFFFFF")).pack(side="left", padx=5)
        ttk.Button(preset_buttons_frame, text="垂直文字", 
                  command=lambda: self.add_preset_layer("竖排文字", 100, "#FFFFFF", direction="vertical")).pack(side="left", padx=5)
    
    def update_layer_list(self):
        """更新文字层列表显示"""
        self.layer_listbox.delete(0, tk.END)
        for i, layer in enumerate(self.generator.text_layers):
            content = layer['content'][:15] + "..." if len(layer['content']) > 15 else layer['content']
            direction_short = {
                'horizontal_ltr': '横→',
                'vertical': '竖↓',
                'horizontal_rtl': '横←'
            }.get(layer.get('direction', 'horizontal_ltr'), '横→')
            
            rotation = layer.get('rotation', 0)
            flip = layer.get('flip', 'none')
            flip_short = {
                'none': '',
                'horizontal': '水平翻转',
                'vertical': '垂直翻转',
                'both': '双向翻转'
            }.get(flip, '')
            
            effects = []
            if rotation != 0:
                effects.append(f"{rotation}°")
            if flip_short:
                effects.append(flip_short)
            
            effect_str = f" [{','.join(effects)}]" if effects else ""
            display_text = f"层{i+1}: {content} ({direction_short}, {layer['size']}px, {layer['color']}){effect_str}"
            self.layer_listbox.insert(tk.END, display_text)
    
    def add_text_layer(self):
        """添加新文字层"""
        dialog = TextLayerDialog(self.frame, self.generator, is_new=True)
        # 对话框关闭后同步预览
        self.frame.after(100, self.sync_preview)
    
    def edit_text_layer(self):
        """编辑文字层"""
        selection = self.layer_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的文字层")
            return
        layer_index = selection[0]
        layer = self.generator.text_layers[layer_index]
        
        dialog = TextLayerDialog(self.frame, self.generator, layer, layer_index, is_new=False)
        # 对话框关闭后同步预览
        self.frame.after(100, self.sync_preview)
    
    def delete_text_layer(self):
        """删除选中的文字层"""
        selection = self.layer_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的文字层")
            return
        
        layer_index = selection[0]
        if messagebox.askyesno("确认", "确定要删除这个文字层吗？"):
            del self.generator.text_layers[layer_index]
            self.update_layer_list()
            # 同步预览
            self.sync_preview()
    
    def move_layer_up(self):
        """上移文字层"""
        selection = self.layer_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要移动的文字层")
            return
        
        layer_index = selection[0]
        if layer_index > 0:
            self.generator.text_layers[layer_index], self.generator.text_layers[layer_index-1] = \
                self.generator.text_layers[layer_index-1], self.generator.text_layers[layer_index]
            self.update_layer_list()
            self.layer_listbox.selection_set(layer_index-1)
            # 同步预览
            self.sync_preview()
    
    def move_layer_down(self):
        """下移文字层"""
        selection = self.layer_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要移动的文字层")
            return
        
        layer_index = selection[0]
        if layer_index < len(self.generator.text_layers) - 1:
            self.generator.text_layers[layer_index], self.generator.text_layers[layer_index+1] = \
                self.generator.text_layers[layer_index+1], self.generator.text_layers[layer_index]
            self.update_layer_list()
            self.layer_listbox.selection_set(layer_index+1)
            # 同步预览
            self.sync_preview()
    
    def add_preset_layer(self, content, size, color, direction="horizontal_ltr"):
        """添加预设样式的文字层"""
        # 设置默认字体路径
        default_font_path = None
        if os.path.exists("fonts/Songti.ttc"):
            default_font_path = "fonts/Songti.ttc"
            
        new_layer = {
            'content': content,
            'size': size,
            'color': color,
            'font_path': default_font_path,
            'x_offset': 0,
            'y_offset': 0,
            'direction': direction,
            'flip': 'none',
            'rotation': 0
        }
        self.generator.text_layers.append(new_layer)
        self.update_layer_list()
        # 同步预览
        self.sync_preview()
    
    def sync_preview(self):
        """同步更新预览标签页"""
        try:
            if hasattr(self, 'preview_tab') and self.preview_tab:
                # 如果预览标签页有当前图像，则重新生成预览
                if hasattr(self.preview_tab, 'current_image') and self.preview_tab.current_image:
                    self.preview_tab.generate_preview()
        except Exception as e:
            print(f"同步预览失败: {e}") 