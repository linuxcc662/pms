from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "待开始"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    DELAYED = "已延期"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class Task:
    """任务类，表示单个项目任务"""
    
    title: str
    description: str = ""
    priority: int = Priority.LOW.value
    status: str = TaskStatus.PENDING.value
    progress: int = 0
    start_date: Optional[str] = None
    updated_at: Optional[str] = None
    due_date: Optional[str] = None
    project_number: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.start_date:
            self.start_date = datetime.now().strftime("%Y-%m-%d")
        if not self.updated_at:
            self.updated_at = current_time
    
    def update_progress(self, progress: int) -> None:
        """更新任务进度"""
        if not 0 <= progress <= 100:
            raise ValueError("进度必须在0-100之间")
            
        self.progress = progress
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._update_status_based_on_progress()
    
    def _update_status_based_on_progress(self) -> None:
        """根据进度自动更新状态"""
        if self.progress == 100:
            self.status = TaskStatus.COMPLETED.value
        elif self.progress > 0:
            self.status = TaskStatus.IN_PROGRESS.value
        else:
            self.status = TaskStatus.PENDING.value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建任务实例"""
        return cls(**data)
    
    def is_overdue(self) -> bool:
        """检查任务是否逾期"""
        if not self.due_date:
            return False
        
        try:
            due_date = datetime.strptime(self.due_date, "%Y-%m-%d")
            return datetime.now() > due_date and self.status != TaskStatus.COMPLETED.value
        except ValueError:
            return False