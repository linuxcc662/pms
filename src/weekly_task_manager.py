import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from task import WeeklyTask
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WeeklyTaskManager:
    """每周待办事项管理器"""

    def __init__(self, data_file: str = "weekly_data.json"):
        """初始化每周待办事项管理器"""
        self.data_file = Path(data_file)
        self.weekly_tasks: List[WeeklyTask] = []
        self.load_data()

    def load_data(self) -> None:
        """从文件加载每周待办事项数据"""
        if not self.data_file.exists():
            logger.info("每周待办事项数据文件不存在，创建空列表")
            self.weekly_tasks = []
            return
    
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.weekly_tasks = [WeeklyTask.from_dict(item) for item in data]  # 修复：使用WeeklyTask.from_dict
            logger.info(f"成功加载 {len(self.weekly_tasks)} 个每周待办事项")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"加载每周待办事项失败: {e}")
            self.weekly_tasks = []
        except Exception as e:
            logger.error(f"加载数据时发生未知错误: {e}")
            self.weekly_tasks = []

    def save_data(self) -> bool:
        """保存每周待办事项数据到文件"""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
    
            # 只保存用户输入的字段，而不是所有Task字段
            weekly_data = []
            for weekly_task in self.weekly_tasks:
                task_data = {
                    'title': weekly_task.title,
                    'description': weekly_task.description,
                    'priority': weekly_task.priority,
                    'due_date': weekly_task.due_date,
                    'start_date': weekly_task.start_date,
                    'is_completed': weekly_task.is_completed,  # 修复字段名
                    'project_name': weekly_task.project_name,   # 修复字段名
                }
                weekly_data.append(task_data)
    
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(weekly_data, f, ensure_ascii=False, indent=2)
    
            logger.info(f"成功保存 {len(self.weekly_tasks)} 个每周待办事项")
            return True
        except (IOError, PermissionError) as e:
            logger.error(f"保存每周待办事项失败: {e}")
            return False
        except Exception as e:
            logger.error(f"保存数据时发生未知错误: {e}")
            return False

    def add_weekly_task(self, title: str, description: str = "", priority: int = 1,
                        due_date: Optional[str] = None, start_date: Optional[str] = None,
                        project_name: Optional[str] = None) -> Optional[WeeklyTask]:
        """添加每周待办事项"""
        try:
            task = WeeklyTask(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                start_date=start_date,
                project_name=project_name,
                is_completed=False  # 添加默认完成状态
            )
            self.weekly_tasks.append(task)
            if self.save_data():
                return task
            return None
        except Exception as e:
            logger.error(f"添加每周待办事项失败: {e}")
            return None

    def get_all_weekly_tasks(self) -> List[WeeklyTask]:
        """获取所有每周待办事项"""
        return self.weekly_tasks.copy()

    # def get_tasks_by_week(self, week_number: int, year: Optional[int] = None) -> List[Task]:
    #     """获取指定周数的任务"""
    #     if year is None:
    #         year = datetime.now().year

    #     result = []
    #     for task in self.weekly_tasks:
    #         if task.start_date:
    #             try:
    #                 task_date = datetime.strptime(task.start_date, "%Y-%m-%d")
    #                 if task_date.isocalendar()[1] == week_number and task_date.year == year:
    #                     result.append(task)
    #             except ValueError:
    #                 continue
    #     return result

    def get_weekly_stats(self, week_number: int, year: Optional[int] = None) -> Dict[str, Any]:
        """获取每周统计信息"""
        tasks = self.get_tasks_by_week(week_number, year)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "已完成")
        progress = sum(t.progress for t in tasks) / total if total > 0 else 0

        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total * 100), 2) if total > 0 else 0,
            'average_progress': round(progress, 2)
        }