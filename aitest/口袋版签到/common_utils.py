""" 共享的公共的点击函数方法（模拟点击非真实点击） """

import win32gui
import win32api
import win32con
import time

# 窗口相关函数
def find_window_by_title(window_title):
    """根据窗口标题查找窗口句柄"""
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and window_title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

def get_window_position(hwnd):
    """获取窗口位置和大小"""
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height

def click_at_window_coord(hwnd, x, y, click_duration=0.05, with_mouse_move=True):
    """在窗口坐标处点击，不移动鼠标"""
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.01)
        
        client_x, client_y = win32gui.ScreenToClient(hwnd, (x, y))
        lParam = win32api.MAKELONG(client_x, client_y)
        
        if with_mouse_move:
            win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
            time.sleep(0.01)
        
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(click_duration)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        
        return True
    except Exception as e:
        print(f"点击失败: {e}")
        return False