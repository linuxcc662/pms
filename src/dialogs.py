from datetime import datetime
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import tkinter as tk
from typing import Optional, Tuple

# UI配置常量
UI_CONFIG = {
    'dialog_size': "600x450",
    'padding': "10",
    'entry_width': 12,  # 优化：从5调整为12
    'text_height': 8,
    'spinbox_width': 5,
    'date_entry_width': 12  # 优化：从20调整为12
}

class TaskDialog:
    """任务对话框类，用于创建和编辑任务信息"""

    def __init__(self, parent: tk.Tk, title: str, task: Optional[object] = None) -> None:
        """
        初始化任务对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            task: 可选的任务对象，用于编辑模式
        """
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(UI_CONFIG['dialog_size'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.center_dialog(parent)
        self.create_widgets(task)
        self.dialog.wait_window()

    def center_dialog(self, parent: tk.Tk) -> None:
        """将对话框居中显示在父窗口中心"""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self, task: Optional[object]) -> None:
        """创建对话框中的所有控件"""
        frame = ttk.Frame(self.dialog, padding=UI_CONFIG['padding'])
        frame.pack(fill=tk.BOTH, expand=True)

        # 项目编号
        self.create_label_entry(frame, "项目编号:", "project_number", 
                               task.project_number if task else "", 0)
        
        # 项目名称
        self.create_label_entry(frame, "项目名称:", "title", 
                               task.title if task else "", 1)
        
        # 描述
        self.create_text_area(frame, "描述:", task.description if task else "", 2)
        
        # 优先级
        self.create_priority_spinbox(frame, task.priority if task else 1, 3)
        
        # 开始日期
        self.create_date_entry(frame, "开始日期:", "start_date", 
                              task.start_date if task else "", 4)
        
        # 截止日期
        self.create_date_entry(frame, "截止日期:", "due_date", 
                              task.due_date if task else "", 5)
        
        # 日期格式提示 - 优化：合并为一行
        ttk.Label(frame, text="日期格式: YYYY-MM-DD").grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # 按钮框架
        self.create_button_frame(frame, 7)
        
        # 配置网格权重 - 修复变形问题
        frame.columnconfigure(0, weight=0)  # 标签列不扩展
        frame.columnconfigure(1, weight=1)   # 输入框列扩展
        frame.columnconfigure(2, weight=0)   # 提示列不扩展
        frame.columnconfigure(3, weight=0)   # 按钮列不扩展

    def create_label_entry(self, parent: ttk.Frame, label_text: str, var_name: str, 
                          default_value: str, row: int) -> ttk.Entry:
        """创建标签和输入框组合"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.StringVar(value=default_value)
        setattr(self, f"{var_name}_var", var)
        entry = ttk.Entry(parent, textvariable=var, width=UI_CONFIG['entry_width'])
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # 优化：添加焦点优化
        entry.bind('<FocusIn>', lambda e: entry.selection_range(0, tk.END))
        return entry

    def create_text_area(self, parent: ttk.Frame, label_text: str, default_text: str, row: int) -> None:
        """创建文本区域控件"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        text_widget = tk.Text(parent, height=UI_CONFIG['text_height'])
        text_widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        if default_text:
            text_widget.insert("1.0", default_text)
        setattr(self, "desc_text", text_widget)

    def create_priority_spinbox(self, parent: ttk.Frame, default_value: int, row: int) -> None:
        """创建优先级微调框"""
        ttk.Label(parent, text="优先级:").grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.IntVar(value=default_value)
        setattr(self, "priority_var", var)
        spinbox = ttk.Spinbox(parent, from_=1, to=5, textvariable=var, 
                             width=UI_CONFIG['spinbox_width'])
        spinbox.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)

    def create_date_entry(self, parent: ttk.Frame, label_text: str, var_name: str, 
                         default_value: str, row: int) -> None:
        """创建日期选择器"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.StringVar(value=default_value)
        setattr(self, f"{var_name}_var", var)
        date_entry = DateEntry(parent, textvariable=var, 
                             width=UI_CONFIG['date_entry_width'],
                             date_pattern='yyyy-mm-dd', locale='zh_CN')
        date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 添加焦点绑定以减少闪烁
        date_entry.bind('<FocusIn>', lambda e: date_entry.selection_range(0, tk.END))

    def create_button_frame(self, parent: ttk.Frame, row: int) -> None:
        """创建按钮框架"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)

    def validate_date_format(self, date_str: str, field_name: str) -> bool:
        """验证日期格式是否正确"""
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return True
            except ValueError:
                messagebox.showwarning("警告", f"{field_name}格式错误，请使用 YYYY-MM-DD 格式")
                return False
        return True

    def validate_inputs(self) -> bool:
        """验证所有输入"""
        title = self.title_var.get().strip()
        
        if not title:
            messagebox.showwarning("警告", "任务标题不能为空")
            return False

        # 验证日期格式
        if not self.validate_date_format(self.start_date_var.get().strip(), "开始日期"):
            return False
        if not self.validate_date_format(self.due_date_var.get().strip(), "截止日期"):
            return False
            
        return True

    def on_ok(self) -> None:
        """确定按钮点击事件 - 验证输入并返回结果"""
        if not self.validate_inputs():
            return

        description = self.desc_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        
        self.result = (
            self.title_var.get().strip(),
            description,
            priority,
            self.due_date_var.get().strip() or None,
            self.start_date_var.get().strip() or None,
            self.project_number_var.get().strip() or None
        )
        self.dialog.destroy()

    def on_cancel(self) -> None:
        """取消按钮点击事件"""
        self.dialog.destroy()