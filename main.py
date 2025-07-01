import tkinter as tk
from tkinter import ttk
from background_tab import BackgroundTab
from text_tab import TextTab
from preview_tab import PreviewTab
from image_generator import ImageGenerator

class ShinboBackgroundGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("新房风背景生成器 - Shinbo Style Background Generator")
        self.root.geometry("900x700")
        
        # 初始化图像生成器
        self.generator = ImageGenerator()
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.background_tab = BackgroundTab(self.notebook, self.generator)
        self.text_tab = TextTab(self.notebook, self.generator)
        self.preview_tab = PreviewTab(self.notebook, self.generator)
        
        # 设置标签页之间的引用，方便同步
        self.preview_tab.text_tab = self.text_tab
        self.text_tab.preview_tab = self.preview_tab
        
        # 添加标签页到notebook
        self.notebook.add(self.background_tab.frame, text="背景设置")
        self.notebook.add(self.text_tab.frame, text="文字设置")
        self.notebook.add(self.preview_tab.frame, text="预览和保存")
        
        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """标签页切换时的回调函数"""
        selected_tab = self.notebook.select()
        tab_index = self.notebook.index(selected_tab)
        
        # 当切换到预览标签页时，自动更新预览
        if tab_index == 2:  # 预览标签页索引
            self.preview_tab.auto_preview()

if __name__ == "__main__":
    root = tk.Tk()
    app = ShinboBackgroundGenerator(root)
    root.mainloop()