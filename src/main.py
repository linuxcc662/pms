import json
import os
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry  # 添加日历控件导入
from typing import List, Dict, Optional
import tkinter as tk
from gui import ProjectManagerGUI
from styles import setup_styles
import sv_ttk

def main():
    """
    项目进度管理系统主入口函数
    
    初始化Tkinter主窗口并启动应用程序
    """
    root = tk.Tk()
    # setup_styles()
    
    # # Change to the directory containing azure.tcl
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # os.chdir(script_dir)
    
    # root.tk.call("source", "themes/dark.tcl")
    # root.tk.call("set_theme", "light")
    # sv_ttk.set_theme("light")
    # sv_ttk.set_theme("dark")
    app = ProjectManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

