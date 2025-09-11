import json
import os
from typing import List, Optional
from datetime import datetime
from task import Task
from builtins import int


class ProjectManager:
    """
    项目管理器，负责任务的增删改查和持久化

    Attributes:
        data_file (str): 数据文件路径
        tasks (List[Task]): 任务列表
    """

    def __init__(self, data_file: str = "project_data.json"):
        """
        初始化项目管理器

        Args:
            data_file: 数据文件路径，默认为project_data.json
        """
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.load_tasks()

    def add_task(self, title: str, description: str = "", priority: int = 1,
                 due_date: Optional[str] = None, start_date: Optional[str] = None,
                 project_number: Optional[str] = None) -> Task:
        """添加新任务"""
        task = Task(title, description, priority,
                    due_date, start_date, project_number)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def remove_task(self, task_index: int) -> bool:
        """删除指定索引的任务"""
        if 0 <= task_index < len(self.tasks):
            del self.tasks[task_index]
            self.save_tasks()
            return True
        return False

    def update_task_progress(self, task_index: int, progress: int) -> bool:
        """更新指定任务的进度"""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index].update_progress(progress)
            self.save_tasks()
            return True
        return False

    def get_task(self, task_index: int) -> Optional[Task]:
        """获取指定索引的任务"""
        if 0 <= task_index < len(self.tasks):
            return self.tasks[task_index]
        return None

    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return self.tasks.copy()  # 返回副本避免外部修改

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """按状态筛选任务"""
        return [task for task in self.tasks if task.status == status]

    def get_tasks_by_priority(self, priority: int) -> List[Task]:
        """按优先级筛选任务"""
        return [task for task in self.tasks if task.priority == priority]

    def get_tasks_by_project_number(self, project_number: str) -> List[Task]:
        """按项目编号筛选任务"""
        return [task for task in self.tasks if task.project_number == project_number]

    def save_tasks(self) -> None:
        """保存任务到文件"""
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (IOError, PermissionError) as e:
            print(f"保存任务失败: {e}")

    def load_tasks(self) -> None:
        """从文件加载任务"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(item) for item in data]
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                print(f"加载任务失败: {e}")
                self.tasks = []
        else:
            self.tasks = []

    def __len__(self) -> int:
        """返回任务数量"""
        return len(self.tasks)

    def __getitem__(self, index: int) -> Task:
        """支持索引访问"""
        return self.tasks[index]

    def __iter__(self):
        """支持迭代"""
        return iter(self.tasks)
