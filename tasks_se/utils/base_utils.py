from pathlib import Path
import os
import winreg
from wcwidth import wcswidth
import socket

def auto_del_files(folder_path, max_nums):
    """
    folder_path 中文件数量超过 max_nums 时，自动删除时间较早的文件
    """
    folder = Path(folder_path)
    all_files = sorted(folder.glob("*.*"), key=lambda x: os.path.getmtime(x))
    if len(all_files) > max_nums:
        for old_file in all_files[: -max_nums]:
            old_file.unlink()

def get_desktop_path():
    """
    根据注册表获得桌面路径
    :return:
    """
    # 打开注册表键
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    )
    # 读取 Desktop 的值
    desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
    # 替换可能的环境变量（如 %USERPROFILE%）
    desktop_path = os.path.expandvars(desktop_path)
    return desktop_path

def format_dataframe(df, interval):
    """格式化DataFrame为对齐的文本"""
    df.index = df.index.astype(str)
    df.columns = df.columns.astype(str)
    df = df.astype(str)
    # 获取各列最大宽度
    col_widths = [
        max(df[col].apply(wcswidth).max(), wcswidth(col))
        for col in df.columns
    ]
    # 生成表头
    header = ' ' + ''.join(
        [col + (col_w - wcswidth(col) + interval) * ' '
         for col_w, col in zip(col_widths, df.columns)]
    ) + " \n"
    # 生成数据行
    rows = []
    for idx, row in df.iterrows():
        row_str = ' ' + ''.join(
            [row[col] + (col_w - wcswidth(row[col]) + interval) * ' '
             for col_w, col in zip(col_widths, df.columns)]
        )
        if idx != df.index[-1]:  # 如果不是最后一行，才加换行符
            row_str += " \n"
        rows.append(row_str)
    return header + ''.join(rows)

def is_port_available(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except socket.error:
            return False

def find_free_port(start_port=9222, max_attempts=100):
    """查找空闲端口"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except socket.error:
                continue
    raise Exception("找不到可用端口")


