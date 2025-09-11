from typing import Optional, Dict
from datetime import datetime

class Task:
    """
    任务类，表示单个项目任务
    
    Attributes:
        title (str): 任务标题
        description (str): 任务描述
        priority (int): 优先级 (1-5)
        status (str): 任务状态
        progress (int): 进度百分比
        start_date (str): 开始日期
        updated_at (str): 最后更新时间
        due_date (Optional[str]): 截止日期
        project_number (Optional[str]): 项目编号
    """

    def __init__(self, title: str, description: str = "", priority: int = 1,
                 due_date: Optional[str] = None, start_date: Optional[str] = None,
                 project_number: Optional[str] = None):
        """
        初始化任务实例
        
        Args:
            title: 任务标题
            description: 任务描述，默认为空字符串
            priority: 优先级 (1-5)，默认为1
            due_date: 截止日期，默认为None
            start_date: 开始日期，默认为当前日期
            project_number: 项目编号，默认为None
        """
        self.title = title
        self.description = description
        self.priority = priority  # 1-5，数字越大优先级越高
        self.status = "待开始"  # 待开始、进行中、已完成、已延期
        self.start_date = start_date if start_date else datetime.now().strftime("%Y-%m-%d")
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.due_date = due_date
        self.progress = 0  # 进度百分比
        self.project_number = project_number  # 项目编号

    def update_progress(self, progress: int) -> None:
        """
        更新任务进度
        
        Args:
            progress: 进度百分比 (0-100)
            
        Raises:
            ValueError: 如果进度不在0-100范围内
        """
        if not 0 <= progress <= 100:
            raise ValueError("进度必须在0-100之间")
            
        self.progress = progress
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 根据进度自动更新状态
        if progress == 100:
            self.status = "已完成"
        elif progress > 0:
            self.status = "进行中"
        else:
            self.status = "待开始"

    def to_dict(self) -> Dict:
        """
        转换为字典格式用于序列化
        
        Returns:
            Dict: 包含任务所有属性的字典
        """
        return {
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'progress': self.progress,
            'start_date': self.start_date,
            'updated_at': self.updated_at,
            'due_date': self.due_date,
            'project_number': self.project_number
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """
        从字典创建任务实例
        
        Args:
            data: 包含任务数据的字典
            
        Returns:
            Task: 新创建的任务实例
            
        Raises:
            KeyError: 如果缺少必需的字段
        """
        # 验证必需字段
        required_fields = ['title', 'description', 'priority', 'status', 
                         'progress', 'start_date', 'updated_at']
        for field in required_fields:
            if field not in data:
                raise KeyError(f"缺少必需字段: {field}")
        
        task = cls(data['title'], data['description'], data['priority'],
                   data.get('due_date'), data.get('start_date'), 
                   data.get('project_number'))
        task.status = data['status']
        task.progress = data['progress']
        task.updated_at = data['updated_at']
        return task

    def __str__(self) -> str:
        """返回任务的字符串表示"""
        return f"Task(title='{self.title}', status='{self.status}', progress={self.progress}%)"

    def __repr__(self) -> str:
        """返回任务的正式字符串表示"""
        return (f"Task(title='{self.title}', description='{self.description}', "
                f"priority={self.priority}, status='{self.status}', progress={self.progress}, "
                f"start_date='{self.start_date}', updated_at='{self.updated_at}', "
                f"due_date='{self.due_date}', project_number='{self.project_number}')")