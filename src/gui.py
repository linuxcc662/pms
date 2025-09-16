import json
import os
import logging
from datetime import datetime, timedelta
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from typing import List, Dict, Optional
import tkinter as tk
from dialogs import TaskDialog
from project_manager import ProjectManager
from dialogs import WeeklyTaskDialog
from weekly_task_manager import WeeklyTaskManager

# 配置日志
logger = logging.getLogger(__name__)

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
    """每周待办事项图形界面（优化版）"""

    def __init__(self, parent, weekly_task_manager):
        self.parent = parent
        self.weekly_task_manager = weekly_task_manager
        self.setup_ui()

    def setup_ui(self):
        """设置每周待办事项界面"""
        # 周选择器
        week_frame = ttk.Frame(self.parent)
        week_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(week_frame, text="选择周:").pack(side=tk.LEFT, padx=(0, 5))

        # 生成周选项
        week_options = self.generate_week_options()
        current_week = datetime.now().isocalendar()[1]
        current_monday, current_sunday = self.get_week_dates(current_week)

        self.week_var = tk.StringVar(
            value=f"第{current_week}周 ({current_monday}-{current_sunday})")

        week_combo = ttk.Combobox(week_frame, textvariable=self.week_var,
                                  values=week_options, width=20, state="readonly")
        week_combo.pack(side=tk.LEFT)
        week_combo.bind("<<ComboboxSelected>>", self.refresh_weekly_tasks)

        # 操作按钮
        self.setup_action_buttons(week_frame)

        # 每周任务列表
        self.setup_task_tree()

        # 统计信息
        self.setup_statistics()

        self.refresh_weekly_tasks()

    def generate_week_options(self):
        """生成周选项列表"""
        week_options = []
        for i in range(1, 53):
            monday, sunday = self.get_week_dates(i)
            week_options.append(f"第{i}周 ({monday}-{sunday})")
        return week_options

    def setup_action_buttons(self, parent_frame):
        """设置操作按钮"""
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))

        buttons = [
            ("新增任务", self.add_weekly_task, 'Success.TButton'),
            ("编辑任务", self.edit_weekly_task, 'Primary.TButton'),
            ("删除任务", self.delete_weekly_task, 'Danger.TButton'),
            ("刷新", self.refresh_weekly_tasks, 'Primary.TButton')
        ]

        for text, command, style in buttons:
            ttk.Button(button_frame, text=text, command=command,
                       style=style).pack(side=tk.LEFT, padx=5)

    def setup_task_tree(self):
        """设置任务树形列表"""
        weekly_frame = ttk.Frame(self.parent)
        weekly_frame.pack(fill=tk.BOTH, expand=True)

        weekly_columns = ("title", "project", "priority",
                          "completed", "due_date")
        self.weekly_tree = ttk.Treeview(weekly_frame, columns=weekly_columns,
                                        show="headings", height=15)

        # 设置列标题和宽度
        columns_config = [
            ("title", "任务名称", 150),
            ("project", "所属项目", 100),
            ("priority", "紧急程度", 80),
            ("completed", "是否完成", 80),
            ("due_date", "预期完成时间", 120)
        ]

        for col_id, heading, width in columns_config:
            self.weekly_tree.heading(col_id, text=heading)
            self.weekly_tree.column(col_id, width=width, anchor='center')

        # 添加滚动条
        weekly_scrollbar = ttk.Scrollbar(weekly_frame, orient=tk.VERTICAL,
                                         command=self.weekly_tree.yview)
        self.weekly_tree.configure(yscrollcommand=weekly_scrollbar.set)

        self.weekly_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        weekly_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_statistics(self):
        """设置统计信息区域"""
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill=tk.X, pady=(10, 0))

        self.total_label = ttk.Label(stats_frame, text="总任务: 0")
        self.total_label.pack(side=tk.LEFT, padx=(0, 10))

        self.completed_label = ttk.Label(stats_frame, text="已完成: 0")
        self.completed_label.pack(side=tk.LEFT, padx=(0, 10))

        self.pending_label = ttk.Label(stats_frame, text="未完成: 0")  # 新增这行
        self.pending_label.pack(side=tk.LEFT, padx=(0, 10))  # 新增这行

        self.progress_label = ttk.Label(stats_frame, text="平均进度: 0%")
        self.progress_label.pack(side=tk.LEFT)

    def get_selected_week_number(self):
        """获取当前选择的周数（带错误处理）"""
        try:
            selected_week_str = self.week_var.get()
            week_number = int(selected_week_str.split("第")[1].split("周")[0])
            if 1 <= week_number <= 52:
                return week_number
            else:
                return datetime.now().isocalendar()[1]
        except (IndexError, ValueError):
            return datetime.now().isocalendar()[1]

    def get_weekly_tasks(self, week_number):
        """获取指定周的所有任务"""
        tasks = self.weekly_task_manager.get_all_weekly_tasks()
        weekly_tasks = []

        for task in tasks:
            if task.start_date:
                try:
                    task_week = datetime.strptime(
                        task.start_date, "%Y-%m-%d").isocalendar()[1]
                    if task_week == week_number:
                        weekly_tasks.append(task)
                except ValueError:
                    continue
        return weekly_tasks

    def convert_priority(self, priority_str):
        """将优先级字符串转换为数值"""
        priority_map = {
            "一般": 1,
            "重要": 2,
            "核心": 3
        }
        return priority_map.get(priority_str, 1)  # 默认返回1（一般）

    def _get_week_dates_helper(self, week_number):
        """周日期计算辅助方法"""
        current_year = datetime.now().year
        jan_first = datetime(current_year, 1, 1)
        first_weekday = jan_first.weekday()

        if first_weekday <= 3:
            first_monday = jan_first - timedelta(days=first_weekday)
        else:
            first_monday = jan_first + timedelta(days=(7 - first_weekday))

        return first_monday

    def calculate_week_start_date(self, week_number):
        """计算指定周的周一日期（优化版）"""
        first_monday = self._get_week_dates_helper(week_number)
        return (first_monday + timedelta(weeks=week_number - 1)).strftime("%Y-%m-%d")

    def get_week_dates(self, week_number):
        """获取指定周的周一和周日日期（优化版）"""
        first_monday = self._get_week_dates_helper(week_number)
        target_monday = first_monday + timedelta(weeks=week_number - 1)
        target_sunday = target_monday + timedelta(days=6)

        return target_monday.strftime("%m/%d"), target_sunday.strftime("%m/%d")

    def add_weekly_task(self):
        """添加每周待办事项任务"""
        from project_manager import ProjectManager
        project_manager = ProjectManager()
        projects = project_manager.get_all_projects()
        project_names = [
            project.title for project in projects if project.title]

        dialog = WeeklyTaskDialog(
            self.parent, "添加每周任务", project_names=project_names)
        if dialog.result:
            title, description, project, priority_str, completed, due_date = dialog.result

            week_number = self.get_selected_week_number()
            start_date = self.calculate_week_start_date(week_number)

            # 转换优先级和状态
            priority_num = self.convert_priority(priority_str)

            self.weekly_task_manager.add_weekly_task(
                title=title,
                description=description,
                priority=priority_num,
                due_date=due_date,
                start_date=start_date,
                project_name=project if project != "无" else None
            )

            self.refresh_weekly_tasks()
            messagebox.showinfo("成功", "每周任务添加成功!")

    def refresh_weekly_tasks(self, event=None):
        """刷新每周待办事项（优化版）"""
        try:
            # 清空现有数据
            for item in self.weekly_tree.get_children():
                self.weekly_tree.delete(item)

            week_number = self.get_selected_week_number()
            weekly_tasks = self.weekly_task_manager.get_all_weekly_tasks()

            # 显示任务
            for task in weekly_tasks:
                try:
                    # 优化：使用更明确的状态显示
                    completed_status = "已完成" if task.is_completed else "未完成"
                    # 将优先级数值转换为星号显示
                    priority_stars = "★" * min(task.priority, 3) if task.priority else ""
                    self.weekly_tree.insert("", "end", values=(
                        task.title,
                        task.project_name or "无",
                        priority_stars,
                        completed_status,  # 使用明确的状态
                        task.due_date or "无"
                    ))
                except Exception as e:
                    logger.error(f"显示任务时出错: {e}")
                    continue

            # 更新统计信息
            self.update_statistics(weekly_tasks)

        except Exception as e:
            logger.error(f"刷新任务列表时出错: {e}")
            messagebox.showerror("错误", "刷新任务列表失败")

    def find_matching_task(self, tasks, values):
        """查找匹配的任务对象"""
        for task in tasks:
            try:
                # 修复：将星号字符串转换回相应的数值，以正确比较优先级
                priority_value = values[2]
                # 如果是星号格式，转换为对应的数字
                if isinstance(priority_value, str) and priority_value.startswith("★"):
                    priority_num = len(priority_value)
                else:
                    # 保持原有逻辑，处理可能的数字值
                    try:
                        priority_num = int(priority_value)
                    except ValueError:
                        priority_num = 0

                # 修改比较逻辑，使用转换后的优先级数值
                if (str(task.title) == str(values[0]) and
                    ((task.project_name or "无") == values[1] or 
                     (hasattr(task, 'project_number') and (task.project_number or "无") == values[1])) and
                    task.priority == priority_num and  # 使用转换后的数值进行比较
                    ("已完成" if task.is_completed else "未完成") == values[3] and
                        (task.due_date or "无") == values[4]):
                    return task
            except Exception as e:
                # 处理可能的类型转换错误，继续尝试下一个任务
                logger.error(f"匹配任务时出错: {e}")
                continue
        return None

    def update_task_info(self, task, title, description, project, priority, completed, due_date):
        """更新任务信息"""
        priority_num = self.convert_priority(priority)
        # 修复：正确处理状态转换
        is_completed = completed == "已完成"

        task.title = title
        task.description = description
        task.project_name = project if project != "无" else None
        task.priority = priority_num
        task.is_completed = is_completed  # 直接设置布尔值
        task.due_date = due_date
        task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_statistics(self, tasks):
        """更新统计信息"""
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.is_completed)
        pending_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks *
                           100) if total_tasks > 0 else 0

        self.total_label.config(text=f"总任务: {total_tasks}")
        self.completed_label.config(text=f"已完成: {completed_tasks}")
        self.pending_label.config(text=f"未完成: {pending_tasks}")  # 新增未完成统计
        self.progress_label.config(text=f"完成率: {completion_rate:.1f}%")

    def edit_weekly_task(self):
        """编辑每周任务"""
        try:
            selected = self.weekly_tree.selection()
            if not selected:
                messagebox.showwarning("警告", "请先选择一个任务")
                return

            # 获取选中的任务信息
            item = self.weekly_tree.item(selected[0])
            values = item['values']

            week_number = self.get_selected_week_number()
            weekly_tasks = self.get_weekly_tasks(week_number)

            # 查找对应的任务对象
            task_to_edit = self.find_matching_task(weekly_tasks, values)

            if not task_to_edit:
                messagebox.showwarning("警告", "无法找到匹配的任务")
                return

            dialog = WeeklyTaskDialog(self.parent, "编辑每周任务", task_to_edit)
            if dialog.result:
                title, description, project, priority, completed, due_date = dialog.result

                # 更新任务信息
                self.update_task_info(
                    task_to_edit, title, description, project, priority, completed, due_date)

                # 修复：将不存在的save_tasks()改为正确的save_data()
                self.weekly_task_manager.save_data()
                self.refresh_weekly_tasks()
                messagebox.showinfo("成功", "任务更新成功!")
        except Exception as e:
            logger.error(f"编辑任务时出错: {e}")
            messagebox.showerror("错误", f"编辑任务失败: {str(e)}")

    def delete_weekly_task(self):
        """删除每周任务"""
        try:
            selected = self.weekly_tree.selection()
            if not selected:
                messagebox.showwarning("警告", "请先选择一个任务")
                return

        # 获取选中的任务信息
            item = self.weekly_tree.item(selected[0])
            values = item['values']

            week_number = self.get_selected_week_number()
            weekly_tasks = self.get_weekly_tasks(week_number)

            # 查找对应的任务对象
            task_to_delete = self.find_matching_task(weekly_tasks, values)

            if not task_to_delete:
                messagebox.showwarning("警告", "无法找到匹配的任务")
                return

            if messagebox.askyesno("确认", "确定要删除这个任务吗？"):
                # 从管理器中删除任务
                all_tasks = self.weekly_task_manager.get_all_weekly_tasks()
                for i, task in enumerate(all_tasks):
                    if task == task_to_delete:
                        if self.weekly_task_manager.remove_task(i):
                            self.refresh_weekly_tasks()
                            messagebox.showinfo("成功", "任务删除成功!")
                        else:
                            messagebox.showerror("错误", "删除任务失败")
                        break
        except Exception as e:
            logger.error(f"删除任务时出错: {e}")
            messagebox.showerror("错误", f"删除任务失败: {str(e)}")


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
                                                 values=["所有"] + sorted(set(project.project_number for project in self.manager.get_all_projects() if project.project_number)))
        self.project_number_combo.set("所有")
        self.project_number_combo.pack(side=tk.LEFT, padx=5)
        self.project_number_combo.bind(
            "<<ComboboxSelected>>", self.filter_tasks)

        # 任务列表容器框架
        tree_container = ttk.Frame(self.parent)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 任务列表
        columns = ("project_number", "title", "progress",
                   "status", "priority", "start_date", "due_date")
        self.tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", height=15)

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

        scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮框架
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(button_frame, text="添加项目", command=self.add_task,
                   style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="编辑项目", command=self.edit_task,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除项目", command=self.delete_task,
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
            task.project_number for task in self.manager.get_all_projects() if task.project_number))
        self.project_number_combo['values'] = ["所有"] + project_numbers

        tasks = self.manager.get_all_projects()
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

        tasks = self.manager.get_all_projects()

        if status_filter != "所有":
            tasks = [t for t in tasks if t.status == status_filter]

        if priority_filter != "所有":
            tasks = [t for t in tasks if t.priority == int(priority_filter)]

        if project_number_filter != "所有":
            tasks = [t for t in tasks if t.project_number ==
                     project_number_filter]

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
        dialog = TaskDialog(self.parent, "添加项目")
        if dialog.result:
            title, description, priority, due_date, start_date, project_number = dialog.result
            self.manager.add_project(
                title, description, priority, due_date, start_date, project_number)
            self.refresh_task_list()
            messagebox.showinfo("成功", "项目添加成功!")

    def edit_task(self):
        """编辑项目"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个项目")
            return

        item = self.tree.item(selected[0])
        project_number = item['values'][0]

        # 确保项目编号是字符串类型
        if project_number != "无":  # 处理"无"的情况
            project_number = str(project_number)  # 确保转换为字符串
        else:
            messagebox.showwarning("警告", "无法编辑没有项目编号的任务")
            return

        task = self.manager.get_project_by_number(project_number)

        if task:
            dialog = TaskDialog(self.parent, "编辑项目", task)
            if dialog.result:
                title, description, priority, due_date, start_date, project_number = dialog.result
                task.title = title
                task.description = description
                task.priority = priority
                task.due_date = due_date
                task.start_date = start_date
                task.project_number = project_number
                task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.manager.save_data()
                self.refresh_task_list()
                messagebox.showinfo("成功", "项目更新成功!")

    def update_progress(self):
        """更新项目进度"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个项目")
            return

        item = self.tree.item(selected[0])
        project_number = item['values'][0]

        # 确保项目编号是字符串类型
        if project_number != "无":  # 处理"无"的情况
            project_number = str(project_number)  # 确保转换为字符串
        else:
            messagebox.showwarning("警告", "无法更新没有项目编号的任务进度")
            return

        task = self.manager.get_project_by_number(project_number)

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
                self.manager.save_data()
                self.refresh_task_list()
                messagebox.showinfo("成功", "进度更新成功!")

    def delete_task(self):
        """删除项目"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个项目")
            return

        item = self.tree.item(selected[0])
        project_number = item['values'][0]

        # 确保项目编号是字符串类型
        if project_number != "无":  # 处理"无"的情况
            project_number = str(project_number)  # 确保转换为字符串
        else:
            messagebox.showwarning("警告", "无法删除没有项目编号的任务")
            return

        if messagebox.askyesno("确认", "确定要删除这个项目吗？"):
            if self.manager.delete_project(project_number):
                self.refresh_task_list()
                messagebox.showinfo("成功", "项目删除成功!")
            else:
                messagebox.showerror("错误", "删除项目失败")


class ProjectManagerGUI:
    """项目进度管理图形界面（主控制器）"""

    def __init__(self, root):
        self.root = root
        self.root.title("项目进度管理系统")
        self.root.state('zoomed')
        self.root.configure(bg='#ecf0f1')
        # 初始化项目管理器
        self.manager = ProjectManager()
        # 初始化每周待办事项管理器
        self.weekly_task_manager = WeeklyTaskManager()
        # 当前视图
        self.current_view = "split"
        # 视图字典
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
        self.weekly_gui = WeeklyTasksGUI(
            weekly_frame, self.weekly_task_manager)
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


def setup_weekly_tasks_ui(self, parent):
    """设置每周待办事项界面"""
    # 创建WeeklyTaskManager实例
    weekly_task_manager = WeeklyTaskManager()

    # 创建WeeklyTasksGUI实例，传递正确的manager
    self.weekly_tasks_gui = WeeklyTasksGUI(parent, weekly_task_manager)

    # 移除原有的UI设置代码，因为WeeklyTasksGUI会自己设置UI