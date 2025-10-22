# 设置以及获取窗口信息

import win32gui
from win10toast import ToastNotifier
import ctypes  # 用于系统弹窗
import pyautogui
import time
# 初始化通知器 (放在全局变量处)
toaster = ToastNotifier()
# 导入自定义的图像工具模块
from common_utils import click_at_window_coord
# 全局变量
# window_title = "Phone-E6EDU20429087631"  # 全局窗口标题
window_title = "Phone-OBN7WS7D99EYFI49"  # 全局窗口标题
def find_window_by_title(title):
    """根据窗口标题查找窗口句柄"""
    def callback(hwnd, hwnds):
        try:
            if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
                hwnds.append(hwnd)
            return True
        except Exception as e:
            print(f"窗口回调处理出错: {e}")
            return False
    
    hwnds = []
    try:
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None
    except Exception as e:
        print(f"查找窗口时出错: {e}")
        return None

def get_window_position(hwnd):
    """获取窗口位置和大小"""
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height

# 全部操作完毕后出现提示信息
def show_alert(message, use_toast=True):
    """显示提醒（可选择Toast或传统弹窗）"""
    if use_toast:
        toaster.show_toast(
            "提醒",
            message,
            duration=5,
            threaded=True
        )
    else:
        ctypes.windll.user32.MessageBoxW(0, message, "提醒", 1)


# 新增: 点击窗口顶部中间位置以获得焦点
def focus_window(x, y, width, height):
    """点击窗口顶部中间位置以获得焦点"""
    # 计算窗口顶部中间位置
    focus_x = x + width // 2
    focus_y = y + 10  # 窗口顶部偏下10像素，避免点击到边框
    
    # 点击该位置以获得焦点
    hwnd = find_window_by_title(window_title)
    click_at_window_coord(hwnd,focus_x, focus_y)
    time.sleep(0.1)  # 短暂延迟确保焦点生效  