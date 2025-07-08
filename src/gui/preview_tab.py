import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class PreviewTab:
    def __init__(self, parent, generator):
        self.parent = parent
        self.generator = generator
        
        # 创建主框架
        self.frame = ttk.Frame(parent)
        
        self.current_preview = None
        self.current_image = None
        
        # 交互编辑相关变量
        self.interactive_mode = False
        self.text_layer_bounds = []  # 存储每个文字层的边界信息
        self.selected_layer_index = -1  # 当前选中的文字层索引
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_layer_start_x = 0
        self.drag_layer_start_y = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        # 创建左右分栏
        main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        control_frame = ttk.Frame(main_paned)
        main_paned.add(control_frame, weight=1)
        
        # 右侧预览面板
        preview_frame = ttk.Frame(main_paned)
        main_paned.add(preview_frame, weight=2)
        
        self.setup_control_panel(control_frame)
        self.setup_preview_panel(preview_frame)
    
    def setup_control_panel(self, parent):
        """设置控制面板"""
        # 预览控制
        preview_control_frame = ttk.LabelFrame(parent, text="预览控制", padding="10")
        preview_control_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(preview_control_frame, text="生成预览", 
                  command=self.generate_preview).pack(fill="x", pady=2)
        ttk.Button(preview_control_frame, text="刷新预览", 
                  command=self.refresh_preview).pack(fill="x", pady=2)
        
        # 交互编辑模式
        self.interactive_var = tk.BooleanVar()
        interactive_check = ttk.Checkbutton(preview_control_frame, text="交互编辑模式", 
                                          variable=self.interactive_var, 
                                          command=self.toggle_interactive_mode)
        interactive_check.pack(fill="x", pady=2)
        
        # 交互模式说明
        interactive_help = ttk.Label(preview_control_frame, 
                                   text="💡 交互模式: 拖拽移动文字，双击编辑", 
                                   font=("", 8))
        interactive_help.pack(fill="x", pady=2)
        
        # 预览尺寸设置
        size_frame = ttk.Frame(preview_control_frame)
        size_frame.pack(fill="x", pady=5)
        
        ttk.Label(size_frame, text="预览尺寸:").pack(side="left")
        self.preview_scale_var = tk.StringVar(value="25%")
        scale_combo = ttk.Combobox(size_frame, textvariable=self.preview_scale_var, 
                                  values=["10%", "25%", "50%", "75%", "100%"], 
                                  state="readonly", width=8)
        scale_combo.pack(side="right")
        scale_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_preview())
        
        # 图像信息
        info_frame = ttk.LabelFrame(parent, text="图像信息", padding="10")
        info_frame.pack(fill="x", padx=5, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="尚未生成预览", font=("", 9))
        self.info_label.pack(anchor="w")
        
        # 保存设置
        save_frame = ttk.LabelFrame(parent, text="保存设置", padding="10")
        save_frame.pack(fill="x", padx=5, pady=5)
        
        # 输出格式
        ttk.Label(save_frame, text="输出格式:").pack(anchor="w")
        self.format_var = tk.StringVar(value="PNG")
        format_frame = ttk.Frame(save_frame)
        format_frame.pack(fill="x", pady=2)
        
        ttk.Radiobutton(format_frame, text="PNG", variable=self.format_var, 
                       value="PNG").pack(side="left")
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.format_var, 
                       value="JPEG").pack(side="left")
        
        # JPEG质量设置
        quality_frame = ttk.Frame(save_frame)
        quality_frame.pack(fill="x", pady=2)
        
        ttk.Label(quality_frame, text="JPEG质量:").pack(side="left")
        self.quality_var = tk.StringVar(value="95")
        quality_spin = ttk.Spinbox(quality_frame, from_=1, to=100, 
                                  textvariable=self.quality_var, width=5)
        quality_spin.pack(side="right")
        
        # 保存按钮
        ttk.Button(save_frame, text="保存图像", 
                  command=self.save_image).pack(fill="x", pady=(10, 0))
        
        # 批量保存
        batch_frame = ttk.LabelFrame(parent, text="批量操作", padding="10")
        batch_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(batch_frame, text="保存预设尺寸", 
                  command=self.save_preset_sizes).pack(fill="x", pady=2)
        
        help_text = """
        💡 快速保存常用尺寸:
        • 1920x1080 (Full HD)
        • 1280x720 (HD)
        • 3840x2160 (4K)
        • 1080x1920 (手机竖屏)
        """
        help_label = ttk.Label(batch_frame, text=help_text, justify="left", font=("", 8))
        help_label.pack(anchor="w", pady=5)
        
        # 当前设置概览
        summary_frame = ttk.LabelFrame(parent, text="当前设置概览", padding="10")
        summary_frame.pack(fill="x", padx=5, pady=5)
        
        self.summary_label = ttk.Label(summary_frame, text="", justify="left", font=("", 8))
        self.summary_label.pack(anchor="w")
        
        self.update_settings_summary()
    
    def setup_preview_panel(self, parent):
        """设置预览面板"""
        # 预览标题
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(title_frame, text="图像预览", font=("", 12, "bold")).pack(side="left")
        
        # 预览区域
        preview_container = ttk.Frame(parent)
        preview_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建滚动的预览区域
        canvas = tk.Canvas(preview_container, bg="white")
        h_scrollbar = ttk.Scrollbar(preview_container, orient="horizontal", command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(preview_container, orient="vertical", command=canvas.yview)
        
        self.preview_canvas = canvas
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        
        # 预览提示
        self.preview_label = ttk.Label(canvas, text="点击'生成预览'查看效果", 
                                      font=("", 14), background="white")
        canvas.create_window(200, 100, window=self.preview_label)
        
        # 绑定鼠标事件用于交互编辑
        canvas.bind("<Button-1>", self.on_canvas_click)
        canvas.bind("<B1-Motion>", self.on_canvas_drag)
        canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
    
    def generate_preview(self):
        """生成预览"""
        try:
            # 生成图像
            self.current_image = self.generator.create_image()
            self.refresh_preview()
            self.update_image_info()
            
        except Exception as e:
            messagebox.showerror("错误", f"预览生成失败: {str(e)}")
    
    def refresh_preview(self):
        """刷新预览显示"""
        if self.current_image is None:
            return
        
        try:
            # 获取缩放比例
            scale_text = self.preview_scale_var.get()
            scale = float(scale_text.replace('%', '')) / 100.0
            
            # 计算预览尺寸
            preview_width = int(self.current_image.width * scale)
            preview_height = int(self.current_image.height * scale)
            
            # 创建缩放后的预览图像
            preview_img = self.current_image.resize((preview_width, preview_height), 
                                                   Image.Resampling.LANCZOS)
            
            # 转换为tkinter可用的格式
            self.current_preview = ImageTk.PhotoImage(preview_img)
            
            # 清除画布
            self.preview_canvas.delete("all")
            
            # 显示图像
            self.preview_canvas.create_image(0, 0, anchor="nw", image=self.current_preview)
            
            # 如果是交互模式，计算并绘制文字层边界
            if self.interactive_mode:
                self.calculate_text_layer_bounds(scale)
                self.draw_text_layer_bounds()
            
            # 更新滚动区域
            self.preview_canvas.configure(scrollregion=(0, 0, preview_width, preview_height))
            
        except Exception as e:
            messagebox.showerror("错误", f"预览刷新失败: {str(e)}")
    
    def update_image_info(self):
        """更新图像信息"""
        if self.current_image:
            width, height = self.current_image.size
            file_size_estimate = width * height * 3 // 1024  # 粗略估计KB
            
            info_text = f"""尺寸: {width} x {height} 像素
文字层数: {len(self.generator.text_layers)}
估计文件大小: ~{file_size_estimate} KB
背景色: {self.generator.main_color}
边框高度: {self.generator.border_height}px"""
            
            self.info_label.config(text=info_text)
    
    def update_settings_summary(self):
        """更新设置概览"""
        summary_text = f"""背景: {self.generator.width}x{self.generator.height}
主色: {self.generator.main_color}
边框: {self.generator.border_height}px
文字层: {len(self.generator.text_layers)}层
横线: {'是' if self.generator.add_lines else '否'}"""
        
        self.summary_label.config(text=summary_text)
    
    def save_image(self):
        """保存图像"""
        if self.current_image is None:
            messagebox.showwarning("警告", "请先生成预览")
            return
        
        try:
            # 选择保存格式
            format_type = self.format_var.get()
            if format_type == "PNG":
                filetypes = [('PNG files', '*.png'), ('All files', '*.*')]
                default_ext = '.png'
            else:
                filetypes = [('JPEG files', '*.jpg'), ('All files', '*.*')]
                default_ext = '.jpg'
            
            filename = filedialog.asksaveasfilename(
                title='保存背景图片',
                defaultextension=default_ext,
                filetypes=filetypes
            )
            
            if filename:
                if format_type == "JPEG":
                    # JPEG需要转换为RGB模式
                    if self.current_image.mode == 'RGBA':
                        rgb_image = Image.new('RGB', self.current_image.size, (255, 255, 255))
                        rgb_image.paste(self.current_image, mask=self.current_image.split()[-1])
                        quality = int(self.quality_var.get())
                        rgb_image.save(filename, 'JPEG', quality=quality)
                    else:
                        quality = int(self.quality_var.get())
                        self.current_image.save(filename, 'JPEG', quality=quality)
                else:
                    self.current_image.save(filename, 'PNG')
                
                messagebox.showinfo("成功", f"图片已保存到: {filename}")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_preset_sizes(self):
        """保存预设尺寸的图像"""
        if self.current_image is None:
            messagebox.showwarning("警告", "请先生成预览")
            return
        
        # 选择保存目录
        directory = filedialog.askdirectory(title="选择保存目录")
        if not directory:
            return
        
        preset_sizes = [
            (1920, 1080, "FullHD"),
            (1280, 720, "HD"),
            (3840, 2160, "4K"),
            (1080, 1920, "Mobile")
        ]
        
        try:
            original_size = (self.generator.width, self.generator.height)
            
            for width, height, name in preset_sizes:
                # 临时改变生成器尺寸
                self.generator.width = width
                self.generator.height = height
                
                # 生成对应尺寸的图像
                sized_image = self.generator.create_image()
                
                # 保存图像
                filename = f"{directory}/background_{name}_{width}x{height}.png"
                sized_image.save(filename, 'PNG')
            
            # 恢复原始尺寸
            self.generator.width, self.generator.height = original_size
            
            messagebox.showinfo("成功", f"已保存 {len(preset_sizes)} 个不同尺寸的图像到选定目录")
            
        except Exception as e:
            # 确保恢复原始尺寸
            self.generator.width, self.generator.height = original_size
            messagebox.showerror("错误", f"批量保存失败: {str(e)}")
    
    def auto_preview(self):
        """自动预览（在切换到此标签页时调用）"""
        self.update_settings_summary()
        # 如果已经有图像，刷新预览；否则提示用户生成
        if self.current_image:
            self.refresh_preview()
        else:
            # 自动生成一次预览
            try:
                self.generate_preview()
            except:
                pass  # 如果自动生成失败，不显示错误，让用户手动生成
    
    def toggle_interactive_mode(self):
        """切换交互编辑模式"""
        self.interactive_mode = self.interactive_var.get()
        self.selected_layer_index = -1  # 重置选中状态
        self.refresh_preview()
    
    def calculate_text_layer_bounds(self, scale):
        """计算文字层在预览中的边界"""
        self.text_layer_bounds = []
        
        for i, layer in enumerate(self.generator.text_layers):
            # 创建文字图像来获取尺寸
            text_img = self.generator.create_text_layer_image(layer)
            if text_img:
                text_width, text_height = text_img.size
                
                # 计算在原图中的位置
                original_x = (self.generator.width - text_width) // 2 + layer['x_offset']
                original_y = (self.generator.height - text_height) // 2 + layer['y_offset']
                
                # 缩放到预览尺寸
                preview_x = int(original_x * scale)
                preview_y = int(original_y * scale)
                preview_width = int(text_width * scale)
                preview_height = int(text_height * scale)
                
                bounds = {
                    'index': i,
                    'x': preview_x,
                    'y': preview_y,
                    'width': preview_width,
                    'height': preview_height,
                    'x2': preview_x + preview_width,
                    'y2': preview_y + preview_height
                }
                self.text_layer_bounds.append(bounds)
    
    def draw_text_layer_bounds(self):
        """绘制文字层边界框"""
        # 清除之前的边界框
        self.preview_canvas.delete("layer_bounds")
        
        for i, bounds in enumerate(self.text_layer_bounds):
            # 选中的层使用不同颜色
            if i == self.selected_layer_index:
                color = "#ff6b6b"  # 红色表示选中
                width = 2
            else:
                color = "#4ecdc4"  # 青色表示未选中
                width = 1
            
            # 绘制边界框
            self.preview_canvas.create_rectangle(
                bounds['x'], bounds['y'], bounds['x2'], bounds['y2'],
                outline=color, width=width, tags="layer_bounds"
            )
            
            # 绘制层标签
            label_text = f"层{i+1}"
            self.preview_canvas.create_text(
                bounds['x'] + 5, bounds['y'] - 15,
                text=label_text, fill=color, font=("", 10, "bold"),
                anchor="sw", tags="layer_bounds"
            )
    
    def find_layer_at_position(self, x, y):
        """查找指定位置的文字层"""
        for bounds in reversed(self.text_layer_bounds):  # 从上层开始查找
            if (bounds['x'] <= x <= bounds['x2'] and 
                bounds['y'] <= y <= bounds['y2']):
                return bounds['index']
        return -1
    
    def on_canvas_click(self, event):
        """处理画布点击事件"""
        if not self.interactive_mode:
            return
        
        # 获取点击位置
        canvas_x = self.preview_canvas.canvasx(event.x)
        canvas_y = self.preview_canvas.canvasy(event.y)
        
        # 查找点击的文字层
        clicked_layer = self.find_layer_at_position(canvas_x, canvas_y)
        
        if clicked_layer != -1:
            # 选中文字层
            self.selected_layer_index = clicked_layer
            self.dragging = True
            self.drag_start_x = canvas_x
            self.drag_start_y = canvas_y
            
            # 记录文字层的初始位置
            layer = self.generator.text_layers[clicked_layer]
            self.drag_layer_start_x = layer['x_offset']
            self.drag_layer_start_y = layer['y_offset']
            
            # 重绘边界框
            self.draw_text_layer_bounds()
        else:
            # 点击空白区域，取消选中
            self.selected_layer_index = -1
            self.draw_text_layer_bounds()
    
    def on_canvas_drag(self, event):
        """处理画布拖拽事件"""
        if not self.interactive_mode or not self.dragging or self.selected_layer_index == -1:
            return
        
        # 获取当前鼠标位置
        canvas_x = self.preview_canvas.canvasx(event.x)
        canvas_y = self.preview_canvas.canvasy(event.y)
        
        # 计算移动距离
        dx = canvas_x - self.drag_start_x
        dy = canvas_y - self.drag_start_y
        
        # 获取缩放比例
        scale_text = self.preview_scale_var.get()
        scale = float(scale_text.replace('%', '')) / 100.0
        
        # 转换到原图坐标系
        original_dx = int(dx / scale)
        original_dy = int(dy / scale)
        
        # 更新文字层位置
        layer = self.generator.text_layers[self.selected_layer_index]
        layer['x_offset'] = self.drag_layer_start_x + original_dx
        layer['y_offset'] = self.drag_layer_start_y + original_dy
        
        # 重新生成预览
        self.generate_preview()
        
        # 同步更新文字标签页（仅在拖拽结束时更新，避免频繁更新）
    
    def on_canvas_release(self, event):
        """处理鼠标释放事件"""
        if self.dragging:
            # 拖拽结束时同步更新文字标签页
            self.update_text_tab()
        self.dragging = False
    
    def on_canvas_double_click(self, event):
        """处理双击编辑事件"""
        if not self.interactive_mode:
            return
        
        # 获取点击位置
        canvas_x = self.preview_canvas.canvasx(event.x)
        canvas_y = self.preview_canvas.canvasy(event.y)
        
        # 查找双击的文字层
        clicked_layer = self.find_layer_at_position(canvas_x, canvas_y)
        
        if clicked_layer != -1:
            self.selected_layer_index = clicked_layer
            # 直接打开详细编辑对话框
            self.open_detailed_editor()
    
    def create_quick_edit_dialog(self):
        """创建快速编辑对话框"""
        if self.selected_layer_index == -1:
            return
        
        layer = self.generator.text_layers[self.selected_layer_index]
        
        # 创建简单的编辑对话框
        dialog = tk.Toplevel(self.frame)
        dialog.title(f"快速编辑 - 层{self.selected_layer_index + 1}")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # 设置为模态对话框
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # 文字内容
        ttk.Label(dialog, text="文字内容:").pack(pady=5)
        content_var = tk.StringVar(value=layer['content'])
        content_entry = ttk.Entry(dialog, textvariable=content_var, width=40, font=("", 12))
        content_entry.pack(pady=5)
        content_entry.focus()
        content_entry.select_range(0, tk.END)
        
        # 文字大小
        size_frame = ttk.Frame(dialog)
        size_frame.pack(pady=5)
        ttk.Label(size_frame, text="文字大小:").pack(side="left")
        size_var = tk.StringVar(value=str(layer['size']))
        size_spin = ttk.Spinbox(size_frame, from_=12, to=500, textvariable=size_var, width=10)
        size_spin.pack(side="left", padx=5)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def save_changes():
            try:
                layer['content'] = content_var.get()
                layer['size'] = int(size_var.get())
                
                # 重新生成预览
                self.generate_preview()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的文字大小")
        
        def open_full_editor():
            dialog.destroy()
            # 导入并打开完整的文字层编辑对话框
            from gui.text_layer_dialog import TextLayerDialog
            TextLayerDialog(self.frame, self.generator, layer, self.selected_layer_index, is_new=False)
        
        ttk.Button(button_frame, text="保存", command=save_changes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="详细编辑", command=open_full_editor).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side="left", padx=5)
        
        # 回车保存
        content_entry.bind('<Return>', lambda e: save_changes())
        
        # 居中显示对话框
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def open_detailed_editor(self):
        """打开详细编辑对话框"""
        if self.selected_layer_index == -1:
            return
        
        layer = self.generator.text_layers[self.selected_layer_index]
        
        # 导入并打开完整的文字层编辑对话框
        from text_layer_dialog import TextLayerDialog
        
        # 创建一个自定义的对话框，在保存后同步更新
        class InteractiveTextLayerDialog(TextLayerDialog):
            def __init__(self, parent, generator, layer, layer_index, preview_tab):
                self.preview_tab = preview_tab
                super().__init__(parent, generator, layer, layer_index, is_new=False)
            
            def save_layer(self):
                """保存文字层并同步更新预览和文字标签页"""
                try:
                    # 转换方向选择
                    direction_reverse_map = {
                        '水平 (左→右)': 'horizontal_ltr',
                        '垂直 (上→下)': 'vertical',
                        '水平 (右→左)': 'horizontal_rtl'
                    }
                    
                    # 转换翻转选择
                    flip_reverse_map = {
                        '无': 'none',
                        '水平翻转': 'horizontal',
                        '垂直翻转': 'vertical',
                        '水平+垂直翻转': 'both'
                    }
                    
                    # 转换旋转角度
                    rotation_value = int(self.rotation_var.get().replace('°', ''))
                    
                    new_layer = {
                        'content': self.content_var.get(),
                        'size': int(self.size_var.get()),
                        'color': self.color_var.get(),
                        'font_path': self.font_var.get() if self.font_var.get() else None,
                        'x_offset': int(self.x_var.get()) if self.x_var.get() else 0,
                        'y_offset': int(self.y_var.get()) if self.y_var.get() else 0,
                        'direction': direction_reverse_map.get(self.direction_var.get(), 'horizontal_ltr'),
                        'flip': flip_reverse_map.get(self.flip_var.get(), 'none'),
                        'rotation': rotation_value
                    }
                    
                    # 更新文字层
                    self.generator.text_layers[self.layer_index] = new_layer
                    
                    # 更新预览
                    self.preview_tab.generate_preview()
                    
                    # 同步更新文字标签页
                    self.preview_tab.update_text_tab()
                    
                    self.dialog.destroy()
                except ValueError as e:
                    messagebox.showerror("错误", f"请输入有效的数字: {str(e)}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        InteractiveTextLayerDialog(self.frame, self.generator, layer, self.selected_layer_index, self)
    
    def update_text_tab(self):
        """同步更新文字标签页"""
        try:
            if hasattr(self, 'text_tab') and self.text_tab:
                self.text_tab.update_layer_list()
        except Exception as e:
            print(f"同步文字标签页失败: {e}") 