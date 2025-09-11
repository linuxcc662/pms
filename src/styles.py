import json
import os
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry  # 添加日历控件导入
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk

# 配置常量
COLORS = {
    'PRIMARY': '#2c3e50',      # 主色调 - 深蓝色
    'SECONDARY': '#3498db',    # 次要色调 - 蓝色
    'SUCCESS': '#27ae60',      # 成功色 - 绿色
    'WARNING': '#f39c12',      # 警告色 - 橙色
    'DANGER': '#e74c3c',       # 危险色 - 红色
    'LIGHT_BG': '#ecf0f1',     # 浅色背景
    'DARK_TEXT': '#2c3e50'     # 深色文字
}

FONTS = {
    'BASE': ('微软雅黑', 10),
    'BOLD': ('微软雅黑', 10, 'bold'),
    'TITLE': ('微软雅黑', 14, 'bold'),
    'LARGE': ('微软雅黑', 12), 
    'SMALL': ('微软雅黑', 9)
}

def setup_styles():
    """
    设置应用程序的全局样式配置
    
    使用现代clam主题，提供一致的用户界面体验
    包含完整的颜色方案、字体设置和UI组件样式配置
    """
    style = ttk.Style()
    style.theme_use('clam')
    
    # 配置按钮样式
    style.configure('TButton', padding=8, font=FONTS['BOLD'])
    style.map('TButton',
              background=[('active', COLORS['SECONDARY']),
                          ('pressed', COLORS['PRIMARY'])],
              foreground=[('active', 'white'), ('pressed', 'white')])

    # 配置特殊按钮样式
    for style_name, color in [('Primary', 'PRIMARY'), ('Success', 'SUCCESS'), 
                             ('Warning', 'WARNING'), ('Danger', 'DANGER')]:
        style.configure(f'{style_name}.TButton', 
                       background=COLORS[color],
                       foreground='white', 
                       font=FONTS['BOLD'])

    # 配置导航按钮样式
    style.configure('Nav.TButton', font=FONTS['BASE'], borderwidth=0, 
                   relief='flat', padding=(10, 5), 
                   background=COLORS['LIGHT_BG'], 
                   foreground=COLORS['DARK_TEXT'])

    style.configure('Nav.Selected.TButton',
                   font=('微软雅黑', 10, 'bold underline'),
                   borderwidth=0, relief='flat', padding=(10, 5),
                   background=COLORS['LIGHT_BG'],
                   foreground=COLORS['PRIMARY'])

    # 配置标签样式
    style.configure('TLabel', font=FONTS['BASE'], foreground=COLORS['DARK_TEXT'])
    style.configure('Title.TLabel', font=FONTS['TITLE'], foreground=COLORS['PRIMARY'])
    style.configure('Large.TLabel', font=FONTS['LARGE'], foreground=COLORS['DARK_TEXT'])
    style.configure('Small.TLabel', font=FONTS['SMALL'], foreground=COLORS['DARK_TEXT'])

    # 配置其他组件样式
    style.configure('TCombobox', padding=6, font=FONTS['BASE'])
    style.configure('Treeview', font=FONTS['BASE'], rowheight=30,
                    fieldbackground=COLORS['LIGHT_BG'], background='white')
    style.configure('Treeview.Heading', font=('微软雅黑', 12, 'bold'),
                    background=COLORS['PRIMARY'], foreground='white')
    style.configure('TEntry', font=FONTS['BASE'], padding=5)
    style.configure('TFrame', background=COLORS['LIGHT_BG'])
    style.configure('Vertical.TScrollbar', background=COLORS['SECONDARY'])
    style.configure('Horizontal.TScrollbar', background=COLORS['SECONDARY'])