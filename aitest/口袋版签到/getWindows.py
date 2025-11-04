# 设置以及获取窗口信息

import win32gui
from win10toast import ToastNotifier
import ctypes  # 用于系统弹窗
import pyautogui
import win32gui
import win32con
import cv2
import time
# 初始化通知器 (放在全局变量处)
toaster = ToastNotifier()
# 导入自定义的图像工具模块
from common_utils import click_at_window_coord

window_title = "Phone-S25QBDPT22ATF" 
# window_title = "Phone-OBN7WS7D99EYFI49" 
# window_title = "Phone-192.168.0.106:5555" 
# 全局变量
def find_window_by_title(title):
    """根据窗口标题查找窗口句柄"""
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None
def get_screenshot_virtual_desktop(region=None):
    """
    使用虚拟桌面坐标截图，支持多显示器
    region: (left, top, width, height) 基于虚拟桌面的坐标
    """
    with mss.mss() as sct:
        # 监控器0代表整个虚拟桌面
        if region:
            monitor = {
                "left": region[0],
                "top": region[1], 
                "width": region[2],
                "height": region[3]
            }
        else:
            # 截取整个虚拟桌面
            monitor = sct.monitors[0]
        
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
def get_window_region_virtual(hwnd):
    """
    获取窗口在虚拟桌面中的区域
    返回: (left, top, width, height)
    """
    try:
        # 获取窗口在虚拟桌面中的位置
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        return (x, y, width, height)
    except Exception as e:
        print(f"获取窗口区域失败: {e}")
        return None

def click_at_virtual_coord(hwnd, virtual_x, virtual_y):
    """
    在虚拟桌面坐标处点击
    """
    try:
        # 将虚拟桌面坐标转换为窗口客户区坐标
        point = (virtual_x, virtual_y)
        client_point = win32gui.ScreenToClient(hwnd, point)
        
        # 发送点击消息
        lParam = (client_point[1] << 16) | (client_point[0] & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        
        print(f"[click_at_virtual_coord] 点击虚拟坐标: ({virtual_x}, {virtual_y})")
        return True
    except Exception as e:
        print(f"点击虚拟坐标失败: {e}")
        return False

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