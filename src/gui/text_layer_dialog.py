import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import os

class TextLayerDialog:
    def __init__(self, parent, generator, layer=None, layer_index=-1, is_new=False):
        self.parent = parent
        self.generator = generator
        # 设置默认字体路径
        default_font_path = None
        if os.path.exists("assets/fonts/Songti.ttc"):
            default_font_path = "assets/fonts/Songti.ttc"
        
        self.layer = layer or {
            'content': '新文字',
            'size': 120,
            'color': '#FFFFFF',
            'font_path': default_font_path,
            'x_offset': 0,
            'y_offset': 0,
            'direction': 'horizontal_ltr',
            'flip': 'none',
            'rotation': 0
        }
        self.layer_index = layer_index
        self.is_new = is_new
        
        self.dialog = None
        self.create_dialog()
    
    def create_dialog(self):
        """创建文字层编辑对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("编辑文字层" if not self.is_new else "新增文字层")
        self.dialog.geometry("600x750")
        self.dialog.resizable(True, True)
        
        # 设置为模态对话框
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 创建滚动框架
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.setup_dialog_content(scrollable_frame)
        
        # 配置滚动
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # 居中显示对话框
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_dialog_content(self, parent):
        """设置对话框内容"""
        # 基础文字设置
        basic_frame = ttk.LabelFrame(parent, text="基础文字设置", padding="10")
        basic_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # 文字内容
        ttk.Label(basic_frame, text="文字内容:").grid(row=0, column=0, sticky="w", pady=5)
        self.content_var = tk.StringVar(value=self.layer['content'])
        content_entry = ttk.Entry(basic_frame, textvariable=self.content_var, width=30)
        content_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # 文字大小
        ttk.Label(basic_frame, text="文字大小:").grid(row=1, column=0, sticky="w", pady=5)
        self.size_var = tk.StringVar(value=str(self.layer['size']))
        ttk.Entry(basic_frame, textvariable=self.size_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # 文字颜色
        ttk.Label(basic_frame, text="文字颜色:").grid(row=2, column=0, sticky="w", pady=5)
        self.color_var = tk.StringVar(value=self.layer['color'])
        
        def choose_text_color():
            color = colorchooser.askcolor(initialcolor=self.color_var.get())
            if color[1]:
                self.color_var.set(color[1])
                self.color_btn.config(bg=color[1])
        
        self.color_btn = tk.Button(basic_frame, text="选择颜色", bg=self.layer['color'], command=choose_text_color)
        self.color_btn.grid(row=2, column=1, padx=5, pady=5)
        
        # 字体文件
        ttk.Label(basic_frame, text="字体文件:").grid(row=3, column=0, sticky="w", pady=5)
        self.font_var = tk.StringVar(value=self.layer['font_path'] or "")
        
        def choose_font_for_layer():
            try:
                filetypes = (
                    ('Font files', '*.ttf *.ttc *.otf'),
                    ('TrueType fonts', '*.ttf'),
                    ('TrueType Collection', '*.ttc'),
                    ('OpenType fonts', '*.otf'),
                    ('All files', '*.*')
                )
                filename = filedialog.askopenfilename(
                    title='选择字体文件',
                    filetypes=filetypes
                )
            except:
                filename = filedialog.askopenfilename(
                    title='选择字体文件 (支持 .ttf .ttc .otf)'
                )
            
            if filename:
                valid_extensions = ['.ttf', '.ttc', '.otf']
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in valid_extensions:
                    self.font_var.set(filename)
                    self.font_label.config(text=f"已选择: {os.path.basename(filename)}")
                else:
                    messagebox.showwarning("警告", "请选择有效的字体文件")
        
        ttk.Button(basic_frame, text="选择字体", command=choose_font_for_layer).grid(row=3, column=1, padx=5, pady=5)
        self.font_label = ttk.Label(basic_frame, text=f"已选择: {os.path.basename(self.layer['font_path'])}" if self.layer['font_path'] else "使用系统默认字体")
        self.font_label.grid(row=3, column=2, padx=5, pady=5)
        
        # 位置偏移
        position_frame = ttk.LabelFrame(parent, text="位置设置", padding="10")
        position_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(position_frame, text="水平偏移:").grid(row=0, column=0, sticky="w", pady=5)
        self.x_var = tk.StringVar(value=str(self.layer['x_offset']))
        ttk.Entry(position_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(position_frame, text="垂直偏移:").grid(row=0, column=2, sticky="w", pady=5)
        self.y_var = tk.StringVar(value=str(self.layer['y_offset']))
        ttk.Entry(position_frame, textvariable=self.y_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        # 文字方向设置
        direction_frame = ttk.LabelFrame(parent, text="文字方向和效果", padding="10")
        direction_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # 文字方向
        ttk.Label(direction_frame, text="文字方向:").grid(row=0, column=0, sticky="w", pady=5)
        self.direction_var = tk.StringVar()
        direction_combo = ttk.Combobox(direction_frame, textvariable=self.direction_var, 
                                      values=self.generator.text_directions, state="readonly", width=15)
        direction_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # 设置默认值
        direction_map = {
            'horizontal_ltr': '水平 (左→右)',
            'vertical': '垂直 (上→下)',
            'horizontal_rtl': '水平 (右→左)'
        }
        current_direction = self.layer.get('direction', 'horizontal_ltr')
        self.direction_var.set(direction_map.get(current_direction, '水平 (左→右)'))
        
        # 翻转效果
        ttk.Label(direction_frame, text="翻转效果:").grid(row=1, column=0, sticky="w", pady=5)
        self.flip_var = tk.StringVar()
        flip_combo = ttk.Combobox(direction_frame, textvariable=self.flip_var,
                                 values=self.generator.flip_options, state="readonly", width=15)
        flip_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # 设置默认值
        flip_map = {
            'none': '无',
            'horizontal': '水平翻转',
            'vertical': '垂直翻转',
            'both': '水平+垂直翻转'
        }
        current_flip = self.layer.get('flip', 'none')
        self.flip_var.set(flip_map.get(current_flip, '无'))
        
        # 旋转角度
        ttk.Label(direction_frame, text="旋转角度:").grid(row=2, column=0, sticky="w", pady=5)
        self.rotation_var = tk.StringVar()
        rotation_combo = ttk.Combobox(direction_frame, textvariable=self.rotation_var,
                                     values=self.generator.rotation_options, state="readonly", width=15)
        rotation_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # 设置默认值
        current_rotation = self.layer.get('rotation', 0)
        self.rotation_var.set(f"{current_rotation}°")
        
        # 说明文字（简化版本）
        help_text = """💡 提示: 可以组合使用方向、翻转、旋转效果来创造独特的视觉效果"""
        help_label = ttk.Label(direction_frame, text=help_text, justify="left", font=("", 8))
        help_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # 按钮
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_layer).pack(side="left", padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side="left", padx=10)
    
    def save_layer(self):
        """保存文字层"""
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
            
            if self.is_new:
                self.generator.text_layers.append(new_layer)
            else:
                self.generator.text_layers[self.layer_index] = new_layer
            
            # 通知父窗口更新
            if hasattr(self.parent, 'update_layer_list'):
                self.parent.update_layer_list()
            
            # 如果有预览标签页，也更新预览
            try:
                # 查找主窗口的预览标签页
                main_window = self.parent
                while hasattr(main_window, 'parent') and main_window.parent:
                    main_window = main_window.parent
                
                if hasattr(main_window, 'preview_tab'):
                    main_window.preview_tab.generate_preview()
            except:
                pass  # 如果找不到预览标签页，忽略错误
            
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("错误", f"请输入有效的数字: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}") 