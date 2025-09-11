from datetime import datetime
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import tkinter as tk

# UI配置常量
UI_CONFIG = {
    'dialog_size': "400x400",
    'padding': "10",
    'entry_width': 40,
    'text_height': 4,
    'spinbox_width': 5,
    'date_entry_width': 20
}

class TaskDialog:
    """任务对话框类，用于创建和编辑任务信息"""

    def __init__(self, parent, title, task=None):
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

    def center_dialog(self, parent):
        """将对话框居中显示在父窗口中心"""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self, task):
        """创建对话框中的所有控件"""
        frame = ttk.Frame(self.dialog, padding=UI_CONFIG['padding'])
        frame.pack(fill=tk.BOTH, expand=True)

        # 项目编号
        self.create_label_entry(frame, "项目编号:", "project_number", 
                               task.project_number if task else "", 0)
        
        # 任务名称
        self.create_label_entry(frame, "任务名称:", "title", 
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
        
        # 日期格式提示
        ttk.Label(frame, text="格式: YYYY-MM-DD").grid(row=5, column=2, sticky=tk.W, pady=5)
        
        # 按钮框架
        self.create_button_frame(frame, 6)
        
        # 配置网格权重
        frame.columnconfigure(1, weight=1)

    def create_label_entry(self, parent, label_text, var_name, default_value, row):
        """创建标签和输入框组合"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.StringVar(value=default_value)
        setattr(self, f"{var_name}_var", var)
        entry = ttk.Entry(parent, textvariable=var, width=UI_CONFIG['entry_width'])
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

    def create_text_area(self, parent, label_text, default_text, row):
        """创建文本区域控件"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        text_widget = tk.Text(parent, width=UI_CONFIG['entry_width'], 
                             height=UI_CONFIG['text_height'])
        text_widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        if default_text:
            text_widget.insert("1.0", default_text)
        setattr(self, "desc_text", text_widget)

    def create_priority_spinbox(self, parent, default_value, row):
        """创建优先级微调框"""
        ttk.Label(parent, text="优先级:").grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.IntVar(value=default_value)
        setattr(self, "priority_var", var)
        spinbox = ttk.Spinbox(parent, from_=1, to=5, textvariable=var, 
                             width=UI_CONFIG['spinbox_width'])
        spinbox.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)

    def create_date_entry(self, parent, label_text, var_name, default_value, row):
        """创建日期选择器"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.StringVar(value=default_value)
        setattr(self, f"{var_name}_var", var)
        date_entry = DateEntry(parent, textvariable=var, 
                             width=UI_CONFIG['date_entry_width'],
                             date_pattern='yyyy-mm-dd', locale='zh_CN')
        date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)

    def create_button_frame(self, parent, row):
        """创建按钮框架"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)

    def validate_date_format(self, date_str, field_name):
        """验证日期格式是否正确"""
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return True
            except ValueError:
                messagebox.showwarning("警告", f"{field_name}格式错误，请使用 YYYY-MM-DD 格式")
                return False
        return True

    def on_ok(self):
        """确定按钮点击事件 - 验证输入并返回结果"""
        title = self.title_var.get().strip()
        
        if not title:
            messagebox.showwarning("警告", "标题不能为空")
            return

        # 验证日期格式
        if not self.validate_date_format(self.start_date_var.get().strip(), "开始日期"):
            return
        if not self.validate_date_format(self.due_date_var.get().strip(), "截止日期"):
            return

        description = self.desc_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        
        self.result = (
            title,
            description,
            priority,
            self.due_date_var.get().strip() or None,
            self.start_date_var.get().strip() or None,
            self.project_number_var.get().strip() or None
        )
        self.dialog.destroy()

    def on_cancel(self):
        """取消按钮点击事件"""
        self.dialog.destroy()