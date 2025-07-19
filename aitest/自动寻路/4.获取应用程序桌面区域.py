import win32gui
import re
import os
import pyautogui
import cv2
import numpy as np
from datetime import datetime

def find_window_by_pattern(pattern):
    """通过正则表达式模糊匹配窗口标题"""
    def callback(hwnd, hwnds):
        if re.search(pattern, win32gui.GetWindowText(hwnd)):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else 0

def get_window_points(window_title_pattern):
    """获取窗口内4个关键点坐标"""
    handle = find_window_by_pattern(window_title_pattern)
    if not handle:
        return None
    
    # 获取窗口矩形
    left, top, right, bottom = win32gui.GetWindowRect(handle)
    
    # 返回4轴坐标（左上、右上、左下、右下）
    return {
        "左上角": (left, top),
        "右上角": (right, top),
        "左下角": (left, bottom),
        "右下角": (right, bottom)
    }

def capture_region(save_dir="screenshots", template_path=None):
    """根据梦幻西游窗口位置进行截图"""
    # 1. 获取梦幻西游窗口位置
    window_points = get_window_points(r"梦幻西游 ONLINE.*")
    
    if not window_points:
        print("未找到梦幻西游窗口")
        return None
    
    # 2. 提取4轴坐标
    top_left = window_points["左上角"]      # (left, top)
    top_right = window_points["右上角"]     # (right, top)
    bottom_left = window_points["左下角"]   # (left, bottom)
    bottom_right = window_points["右下角"]  # (right, bottom)
    
    # 3. 计算截图区域 (left, top, width, height)
    region = (
        top_left[0],     # x
        top_left[1],     # y
        top_right[0] - top_left[0],  # width
        bottom_left[1] - top_left[1] # height
    )
    
    print(f"截图区域: left={region[0]}, top={region[1]}, width={region[2]}, height={region[3]}")
    
    # 4. 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 5. 截图并保存
    screenshot = pyautogui.screenshot(region=region)
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
    
    # 6. 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join(save_dir, f"screenshot_{timestamp}.png")
    screenshot.save(filename)
    print(f"截图已保存: {filename}")
    
    # 7. 如果提供了模板图片，进行匹配
    if template_path and os.path.exists(template_path):
        # 模板匹配代码（根据您的需求实现）
        print(f"使用模板图片进行匹配: {template_path}")
        # 这里可以添加您的模板匹配逻辑
        # template = cv2.imread(template_path, 0)
        # result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        # ... 匹配逻辑 ...
    
    return screenshot_gray

# 使用示例
if __name__ == "__main__":
    # 替换为您的实际模板路径
    template_path = "F:\\AIstudy2025\\aitest\\test\\1.png"
    
    # 进行截图
    result = capture_region(
        save_dir="screenshots",
        template_path=template_path
    )
    
    if result is not None:
        print("截图和模板匹配完成！")