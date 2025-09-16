from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from typing import List, Dict, Optional, Tuple
import tkinter as tk

# 配置常量
COLOR_SCHEME = {
    'PRIMARY': '#2c3e50',      # 主色调 - 深蓝色
    'SECONDARY': '#3498db',    # 次要色调 - 蓝色
    'SUCCESS': '#27ae60',      # 成功色 - 绿色
    'WARNING': '#f39c12',      # 警告色 - 橙色
    'DANGER': '#e74c3c',       # 危险色 - 红色
    'LIGHT_BG': '#ecf0f1',     # 浅色背景
    'DARK_TEXT': '#2c3e50',    # 深色文字
    'BORDER': '#bdc3c7',       # 边框颜色
    'HIGHLIGHT': '#f1c40f'     # 高亮颜色
}

FONT_CONFIG = {
    'BASE': ('微软雅黑', 10),
    'BOLD': ('微软雅黑', 10, 'bold'),
    'TITLE': ('微软雅黑', 14, 'bold'),
    'LARGE': ('微软雅黑', 12),
    'SMALL': ('微软雅黑', 9),
    'MONOSPACE': ('Consolas', 10)  # 新增：等宽字体
}

def setup_styles() -> ttk.Style:
    """
    设置应用程序的全局样式配置
    
    Returns:
        ttk.Style: 配置好的样式对象
    """
    style = ttk.Style()
    style.theme_use('clam')

    # 基础样式配置
    style.configure('.', 
                   background=COLOR_SCHEME['LIGHT_BG'],
                   foreground=COLOR_SCHEME['DARK_TEXT'],
                   font=FONT_CONFIG['BASE'])

    # 配置按钮样式
    style.configure('TButton', 
                   borderwidth=0, 
                   padding=8, 
                   font=FONT_CONFIG['BOLD'],
                   focuscolor=COLOR_SCHEME['SECONDARY'] + '40')
    
    style.map('TButton',
              background=[('active', COLOR_SCHEME['SECONDARY']),
                          ('pressed', COLOR_SCHEME['PRIMARY']),
                          ('focus', COLOR_SCHEME['SECONDARY'] + '20')],
              foreground=[('active', 'white'), 
                          ('pressed', 'white'),
                          ('focus', COLOR_SCHEME['DARK_TEXT'])])

    # 配置特殊按钮样式
    for style_name, color in [('Primary', 'PRIMARY'), ('Success', 'SUCCESS'),
                              ('Warning', 'WARNING'), ('Danger', 'DANGER')]:
        style.configure(f'{style_name}.TButton',
                        background=COLOR_SCHEME[color],
                        foreground='white',
                        font=FONT_CONFIG['BOLD'])

    # 配置导航按钮样式
    style.configure('Nav.TButton', 
                   font=FONT_CONFIG['BASE'], 
                   borderwidth=1, 
                   relief='solid',
                   padding=(15, 8),
                   background='white',
                   foreground=COLOR_SCHEME['DARK_TEXT'],
                   bordercolor=COLOR_SCHEME['BORDER'])

    style.configure('Nav.Selected.TButton',
                    font=FONT_CONFIG['BOLD'],
                    borderwidth=2,
                    relief='solid',
                    padding=(15, 8),
                    background=COLOR_SCHEME['PRIMARY'],
                    foreground='white',
                    bordercolor=COLOR_SCHEME['PRIMARY'])

    # 添加悬停效果映射
    style.map('Nav.TButton',
              background=[('active', COLOR_SCHEME['SECONDARY']),
                          ('pressed', COLOR_SCHEME['PRIMARY'])],
              foreground=[('active', 'white'), ('pressed', 'white')])

    style.map('Nav.Selected.TButton',
          background=[('active', COLOR_SCHEME['PRIMARY']),
                      ('pressed', COLOR_SCHEME['SECONDARY']),
                      ('focus', COLOR_SCHEME['PRIMARY'] + '20')],
          foreground=[('active', 'white'), 
                      ('pressed', 'white'),
                      ('focus', 'white')])

    # 配置标签样式
    style.configure('TLabel', 
                   font=FONT_CONFIG['BASE'], 
                   foreground=COLOR_SCHEME['DARK_TEXT'])
    style.configure('Title.TLabel', 
                   font=FONT_CONFIG['TITLE'], 
                   foreground=COLOR_SCHEME['PRIMARY'])
    style.configure('Large.TLabel', 
                   font=FONT_CONFIG['LARGE'], 
                   foreground=COLOR_SCHEME['DARK_TEXT'])
    style.configure('Small.TLabel', 
                   font=FONT_CONFIG['SMALL'], 
                   foreground=COLOR_SCHEME['DARK_TEXT'])
    style.configure('Mono.TLabel',
                   font=FONT_CONFIG['MONOSPACE'],
                   foreground=COLOR_SCHEME['DARK_TEXT'])

    # 配置其他组件样式
    style.configure('TCombobox', 
                   padding=6, 
                   font=FONT_CONFIG['BASE'],
                   fieldbackground='white')
    
    style.configure('Treeview', 
                   font=FONT_CONFIG['BASE'], 
                   rowheight=30,
                   fieldbackground=COLOR_SCHEME['LIGHT_BG'], 
                   background='white')
    
    style.configure('Treeview.Heading', 
                   font=('微软雅黑', 12, 'bold'),
                   background=COLOR_SCHEME['PRIMARY'], 
                   foreground='white')
    
    style.configure('TEntry', 
                   font=FONT_CONFIG['BASE'], 
                   padding=5,
                   fieldbackground='white')
    
    style.configure('TFrame', 
                   background=COLOR_SCHEME['LIGHT_BG'])
    
    style.configure('Vertical.TScrollbar', 
                   background=COLOR_SCHEME['SECONDARY'])
    
    style.configure('Horizontal.TScrollbar', 
                   background=COLOR_SCHEME['SECONDARY'])
    
    # 配置进度条样式
    style.configure('Horizontal.TProgressbar',
                   background=COLOR_SCHEME['SECONDARY'],
                   troughcolor=COLOR_SCHEME['LIGHT_BG'])

    return style