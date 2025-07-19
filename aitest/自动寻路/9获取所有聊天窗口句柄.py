import win32gui
import win32con
import os
from datetime import datetime
import time
def save_all_windows_to_file(filename="all_windows.txt", parent=None, level=0):
    """
    递归列出所有窗口及其子窗口并保存到文件
    :param filename: 输出文件名
    :param parent: 父窗口句柄
    :param level: 层级（用于缩进）
    """
    # 延迟5秒后执行
    time.sleep(5)
    # 打开文件准备写入
    with open(filename, "w", encoding="utf-8") as f:
        # 写入文件头
        f.write(f"窗口信息采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 100 + "\n")
        
        # 递归收集窗口信息
        def collect_windows(parent, level, file):
            def callback(hwnd, hwnds):
                hwnds.append(hwnd)
                return True

            children = []
            win32gui.EnumChildWindows(parent, callback, children)

            for hwnd in children:
                # 获取窗口信息
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                
                # 格式化窗口信息
                indent = "  " * level
                info = [
                    f"{indent}窗口句柄: {hwnd}",
                    f"{indent}标题: '{title}'",
                    f"{indent}类名: '{class_name}'",
                    f"{indent}坐标: {rect}",
                    f"{indent}{'-'*50}"
                ]
                
                # 写入文件
                file.write("\n".join(info) + "\n")
                
                # 递归获取子窗口
                collect_windows(hwnd, level + 1, file)
        
        # 开始收集顶级窗口
        f.write("系统所有窗口列表:\n")
        f.write("=" * 100 + "\n")
        collect_windows(parent, level, f)
    
    print(f"所有窗口信息已保存到: {os.path.abspath(filename)}")

# 使用示例
if __name__ == "__main__":
    # 保存所有窗口信息到文件
    save_all_windows_to_file("windows_info.txt")
    
    # 同时打印到控制台（可选）
    # 如果您也想在控制台看到输出，可以取消下面两行的注释
    # print("="*80)
    # print("系统所有窗口列表:")
    # print("="*80)
    # list_all_windows()  # 需要先定义list_all_windows函数