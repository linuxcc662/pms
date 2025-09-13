import json
import os
from datetime import datetime, timedelta
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from typing import List, Dict, Optional
import tkinter as tk
from dialogs import TaskDialog
from project_manager import ProjectManager

# UI配置常量
UI_CONFIG = {
    'PADDING': 10,
    'BUTTON_PADDING': (10, 5),
    'TREEVIEW_HEIGHT': 15,
    'COLUMN_WIDTHS': {
        'title': 150,
        'project': 100,
        'priority': 80,
        'completed': 80,
        'due_date': 120
    }
}

FILTER_OPTIONS = {
    'STATUS': ["所有", "待开始", "进行中", "已完成", "已延期"],
    'PRIORITY': ["所有", "1", "2", "3", "4", "5"]
}

class WeeklyTasksGUI:
    """每周待办事项图形界面"""

    def __init__(self, parent_frame, manager):
        self.parent = parent_frame
        self.manager = manager
        self.setup_ui()

    def setup_ui(self):
        """设置每周待办事项界面"""
        # 周选择器
        week_frame = ttk.Frame(self.parent)
        week_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(week_frame, text="选择周:").pack(side=tk.LEFT, padx=(0, 5))

        current_week = datetime.now().isocalendar()[1]
        week_options = []
        for i in range(1, 53):
            monday, sunday = self.get_week_date_range(i)
            week_options.append(f"第{i}周 ({monday}-{sunday})")

        current_monday, current_sunday = self.get_week_date_range(current_week)
        self.week_var = tk.StringVar(value=f"第{current_week}周 ({current_monday}-{current_sunday})")
        
        week_combo = ttk.Combobox(week_frame, textvariable=self.week_var, values=week_options, width=20)
        week_combo.pack(side=tk.LEFT)
        week_combo.bind("<<ComboboxSelected>>", self.refresh_weekly_tasks)

        # 每周任务列表
        weekly_frame = ttk.Frame(self.parent)
        weekly_frame.pack(fill=tk.BOTH, expand=True)

        weekly_columns = ("title", "project", "priority", "completed", "due_date")
        self.weekly_tree = ttk.Treeview(weekly_frame, columns=weekly_columns, show="headings", height=15)
        
        self.weekly_tree.heading("title", text="任务名称")
        self.weekly_tree.heading("project", text="所属项目")
        self.weekly_tree.heading("priority", text="紧急程度")
        self.weekly_tree.heading("completed", text="是否完成")
        self.weekly_tree.heading("due_date", text="预期完成时间")
        
        self.weekly_tree.column("title", width=150, anchor='center')
        self.weekly_tree.column("project", width=100, anchor='center')
        self.weekly_tree.column("priority", width=80, anchor='center')
        self.weekly_tree.column("completed", width=80, anchor='center')
        self.weekly_tree.column("due_date", width=120, anchor='center')

        weekly_scrollbar = ttk.Scrollbar(weekly_frame, orient=tk.VERTICAL, command=self.weekly_tree.yview)
        self.weekly_tree.configure(yscrollcommand=weekly_scrollbar.set)

        self.weekly_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        weekly_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 统计信息
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill=tk.X, pady=(10, 0))

        self.total_label = ttk.Label(stats_frame, text="总任务: 0")
        self.total_label.pack(side=tk.LEFT, padx=(0, 10))

        self.completed_label = ttk.Label(stats_frame, text="已完成: 0")
        self.completed_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_label = ttk.Label(stats_frame, text="总进度: 0%")
        self.progress_label.pack(side=tk.LEFT)

        self.refresh_weekly_tasks()

    def get_week_date_range(self, week_number):
        """获取指定周数的周一至周日日期范围"""
        current_year = datetime.now().year
        jan_first = datetime(current_year, 1, 1)
        first_weekday = jan_first.weekday()
        if first_weekday <= 3:
            first_monday = jan_first - timedelta(days=first_weekday)
        else:
            first_monday = jan_first + timedelta(days=(7 - first_weekday))
        
        target_monday = first_monday + timedelta(weeks=week_number - 1)
        target_sunday = target_monday + timedelta(days=6)
        
        return target_monday.strftime("%m/%d"), target_sunday.strftime("%m/%d")

    def refresh_weekly_tasks(self, event=None):
        """刷新每周待办事项"""
        for item in self.weekly_tree.get_children():
            self.weekly_tree.delete(item)

        selected_week_str = self.week_var.get()
        selected_week = int(selected_week_str.split("第")[1].split("周")[0])
        
        tasks = self.manager.get_all_tasks()
        weekly_tasks = []
        total_progress = 0

        for task in tasks:
            if task.start_date:
                try:
                    task_week = datetime.strptime(task.start_date, "%Y-%m-%d").isocalendar()[1]
                    if task_week == selected_week:
                        weekly_tasks.append(task)
                        total_progress += task.progress
                except ValueError:
                    continue

        for task in weekly_tasks:
            completed_status = "是" if task.status == "已完成" else "否"
            self.weekly_tree.insert("", "end", values=(
                task.title, 
                task.project_number or "无", 
                task.priority, 
                completed_status,
                task.due_date or "无"
            ))
        
        total_tasks = len(weekly_tasks)
        completed_tasks = sum(1 for t in weekly_tasks if t.status == "已完成")
        avg_progress = total_progress / total_tasks if total_tasks > 0 else 0

        self.total_label.config(text=f"总任务: {total_tasks}")
        self.completed_label.config(text=f"已完成: {completed_tasks}")
        self.progress_label.config(text=f"平均进度: {avg_progress:.1f}%")

class ProjectTasksGUI:
    """项目任务管理图形界面"""

    def __init__(self, parent_frame, manager):
        self.parent = parent_frame
        self.manager = manager
        self.setup_ui()

    def setup_ui(self):
        """设置任务管理界面"""
        # 筛选框架
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(filter_frame, text="状态筛选:").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                         values=["所有", "待开始", "进行中", "已完成", "已延期"])
        self.status_combo.set("所有")
        self.status_combo.pack(side=tk.LEFT, padx=5)
        self.status_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        ttk.Label(filter_frame, text="优先级筛选:").pack(side=tk.LEFT, padx=5)
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(filter_frame, textvariable=self.priority_var,
                                           values=["所有", "1", "2", "3", "4", "5"])
        self.priority_combo.set("所有")
        self.priority_combo.pack(side=tk.LEFT, padx=5)
        self.priority_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        ttk.Label(filter_frame, text="项目编号筛选:").pack(side=tk.LEFT, padx=5)
        self.project_number_var = tk.StringVar()
        self.project_number_combo = ttk.Combobox(filter_frame, textvariable=self.project_number_var,
                                                 values=["所有"] + sorted(set(task.project_number for task in self.manager.get_all_tasks() if task.project_number)))
        self.project_number_combo.set("所有")
        self.project_number_combo.pack(side=tk.LEFT, padx=5)
        self.project_number_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        # 任务列表容器框架
        tree_container = ttk.Frame(self.parent)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 任务列表
        columns = ("project_number", "title", "progress", "status", "priority", "start_date", "due_date")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)

        self.tree.heading("project_number", text="项目编号")
        self.tree.heading("title", text="项目名称")
        self.tree.heading("progress", text="进度")
        self.tree.heading("status", text="状态")
        self.tree.heading("priority", text="优先级")
        self.tree.heading("start_date", text="开始日期")
        self.tree.heading("due_date", text="截止日期")

        self.tree.column("project_number", width=100, anchor='center')
        self.tree.column("title", width=200, anchor='center')
        self.tree.column("progress", width=80, anchor='center')
        self.tree.column("status", width=80, anchor='center')
        self.tree.column("priority", width=80, anchor='center')
        self.tree.column("start_date", width=100, anchor='center')
        self.tree.column("due_date", width=100, anchor='center')

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮框架
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(button_frame, text="添加任务", command=self.add_task,
                   style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="编辑任务", command=self.edit_task,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除任务", command=self.delete_task,
                   style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="更新进度", command=self.update_progress,
                   style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.refresh_task_list,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)

        self.refresh_task_list()

    def refresh_task_list(self):
        """刷新任务列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        project_numbers = sorted(set(
            task.project_number for task in self.manager.get_all_tasks() if task.project_number))
        self.project_number_combo['values'] = ["所有"] + project_numbers

        tasks = self.manager.get_all_tasks()
        for task in tasks:
            self.tree.insert("", "end", values=(
                task.project_number or "无",
                task.title,
                f"{task.progress}%",
                task.status,
                task.priority,
                task.start_date,
                task.due_date or "无"
            ))

    def filter_tasks(self, event=None):
        """筛选任务"""
        status_filter = self.status_var.get()
        priority_filter = self.priority_var.get()
        project_number_filter = self.project_number_var.get()

        tasks = self.manager.get_all_tasks()

        if status_filter != "所有":
            tasks = [t for t in tasks if t.status == status_filter]

        if priority_filter != "所有":
            tasks = [t for t in tasks if t.priority == int(priority_filter)]

        if project_number_filter != "所有":
            tasks = [t for t in tasks if t.project_number == project_number_filter]

        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in tasks:
            self.tree.insert("", "end", values=(
                task.project_number or "无",
                task.title,
                f"{task.progress}%",
                task.status,
                task.priority,
                task.start_date,
                task.due_date or "无"
            ))

    def add_task(self):
        """添加新任务"""
        dialog = TaskDialog(self.parent, "添加任务")
        if dialog.result:
            title, description, priority, due_date, start_date, project_number = dialog.result
            self.manager.add_task(title, description, priority, due_date, start_date, project_number)
            self.refresh_task_list()
            messagebox.showinfo("成功", "任务添加成功!")

    def edit_task(self):
        """编辑任务"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return

        item = self.tree.item(selected[0])
        task_index = self.tree.index(selected[0])
        task = self.manager.get_task(task_index)

        if task:
            dialog = TaskDialog(self.parent, "编辑任务", task)
            if dialog.result:
                title, description, priority, due_date, start_date, project_number = dialog.result
                task.title = title
                task.description = description
                task.priority = priority
                task.due_date = due_date
                task.start_date = start_date
                task.project_number = project_number
                task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.manager.save_tasks()
                self.refresh_task_list()
                messagebox.showinfo("成功", "任务更新成功!")

    def delete_task(self):
        """删除任务"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return

        task_index = self.tree.index(selected[0])

        if messagebox.askyesno("确认", "确定要删除这个任务吗？"):
            if self.manager.remove_task(task_index):
                self.refresh_task_list()
                messagebox.showinfo("成功", "任务删除成功!")
            else:
                messagebox.showerror("错误", "删除任务失败")

    def update_progress(self):
        """更新任务进度"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return

        task_index = self.tree.index(selected[0])
        task = self.manager.get_task(task_index)

        if task:
            new_progress = simpledialog.askinteger("更新进度", 
                                                 f"请输入新的进度 (0-100):",
                                                 initialvalue=task.progress,
                                                 minvalue=0, maxvalue=100)
            if new_progress is not None:
                task.progress = new_progress
                if new_progress == 100:
                    task.status = "已完成"
                elif new_progress > 0:
                    task.status = "进行中"
                else:
                    task.status = "待开始"
                task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.manager.save_tasks()
                self.refresh_task_list()
                messagebox.showinfo("成功", "进度更新成功!")

class ProjectManagerGUI:
    """项目进度管理图形界面（主控制器）"""

    def __init__(self, root):
        self.root = root
        self.root.title("项目进度管理系统")
        self.root.state('zoomed')
        self.root.configure(bg='#ecf0f1')

        self.manager = ProjectManager()
        self.current_view = "split"
        self.views = {}
        
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 顶部导航栏
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        self.weekly_btn = ttk.Button(nav_frame, text="每周待办事项",
                                    command=self.show_weekly_view,
                                    style='Nav.TButton')
        self.weekly_btn.pack(side=tk.LEFT, padx=5)

        self.project_btn = ttk.Button(nav_frame, text="项目信息",
                                     command=self.show_project_view,
                                     style='Nav.TButton')
        self.project_btn.pack(side=tk.LEFT, padx=5)

        self.select_button(self.weekly_btn)

        # 主容器框架
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建所有视图
        self.create_all_views()
        self.show_weekly_view()

    def select_button(self, selected_button):
        """设置按钮选中状态"""
        self.weekly_btn.configure(style='Nav.TButton')
        self.project_btn.configure(style='Nav.TButton')
        selected_button.configure(style='Nav.Selected.TButton')

    def create_all_views(self):
        """创建所有视图框架"""
        # 每周待办事项视图
        weekly_frame = ttk.Frame(self.main_container, padding="10")
        self.weekly_gui = WeeklyTasksGUI(weekly_frame, self.manager)
        self.views["weekly"] = weekly_frame

        # 项目信息视图
        project_frame = ttk.Frame(self.main_container, padding="10")
        self.project_gui = ProjectTasksGUI(project_frame, self.manager)
        self.views["project"] = project_frame

        # 初始隐藏所有视图
        for view in self.views.values():
            view.pack_forget()

    def show_weekly_view(self):
        """显示每周待办事项视图"""
        self.switch_view("weekly")

    def show_project_view(self):
        """显示项目信息视图"""
        self.switch_view("project")

    def switch_view(self, view_name):
        """切换视图"""
        if hasattr(self, 'current_view_frame'):
            self.current_view_frame.pack_forget()

        self.current_view_frame = self.views[view_name]
        self.current_view_frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = view_name

        if view_name == "weekly":
            self.select_button(self.weekly_btn)
        elif view_name == "project":
            self.select_button(self.project_btn)