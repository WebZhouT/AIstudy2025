"""
窗口操作和模板匹配工具类
提供窗口查找、位置获取、点击操作和模板匹配等公共方法
"""

import win32gui
import win32con
import pyautogui
import cv2
import numpy as np
import time


def find_window_by_title(title):
    """
    根据窗口标题查找窗口句柄
    
    Args:
        title (str): 窗口标题
        
    Returns:
        int: 窗口句柄，如果未找到返回None
    """
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None


def get_window_position(hwnd):
    """
    获取窗口位置和大小
    
    Args:
        hwnd (int): 窗口句柄
        
    Returns:
        tuple: (x, y, width, height) 窗口位置和大小
    """
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height


def click_top_center(hwnd):
    """
    点击窗口上方中间位置
    
    Args:
        hwnd (int): 窗口句柄
    """
    x, y, width, height = get_window_position(hwnd)
    click_x = x + width // 2
    click_y = y + 20
    pyautogui.moveTo(click_x, click_y, duration=0.1)
    pyautogui.click(click_x, click_y)
    print(f"[click_top_center] 点击窗口顶部中心: ({click_x}, {click_y})")
    time.sleep(0.1)


def match_and_click_template(screenshot, template_path, threshold, region=None):
    """
    匹配模板并执行点击操作
    
    Args:
        screenshot (numpy.ndarray): 屏幕截图
        template_path (str): 模板图片路径
        threshold (float): 匹配阈值
        region (tuple, optional): 区域参数 (x,y,width,height)
        
    Returns:
        tuple: (是否匹配成功, 点击坐标)
    """
    try:
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[match_and_click_template] 警告: 无法读取模板图片 {template_path}")
            return False, None
            
        # 彩色匹配
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[match_and_click_template] 当前匹配度: {max_val:.2f} (阈值: {threshold})")
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            x, y = max_loc
            
            if region:
                # 区域参数为(x,y,width,height)
                region_x, region_y, region_w, region_h = region
                
                # 计算模板中心点相对于全屏的坐标
                center_x = region_x + x + w // 2
                center_y = region_y + y + h // 2
                
                # 验证坐标是否在区域内
                if not (region_x <= center_x <= region_x + region_w and 
                        region_y <= center_y <= region_y + region_h):
                    print(f"[match_and_click_template] 警告: 计算坐标({center_x},{center_y})超出区域{region}")
            else:
                # 如果没有提供区域，则直接使用匹配位置
                center_x = x + w // 2
                center_y = y + h // 2
            
            print(f"[match_and_click_template] 匹配成功，点击坐标: ({center_x}, {center_y})")
            
            # 实际执行鼠标移动和点击操作 - 物理移动方式
            current_x, current_y = pyautogui.position()
            distance = ((center_x - current_x)**2 + (center_y - current_y)**2)**0.5
            
            # 根据距离动态调整移动时间
            move_duration = min(0.1, max(0.05, distance / 1000))
            
            # 物理移动鼠标
            pyautogui.moveTo(center_x, center_y, duration=move_duration, tween=pyautogui.easeInOutQuad)
            time.sleep(0.05)
            
            # 物理点击
            pyautogui.click()
            time.sleep(0.02)
            
            print(f"[match_and_click_template] 已物理点击坐标: ({center_x}, {center_y})")
            time.sleep(0.05)
            
            return True, (center_x, center_y)
        else:
            print(f"[match_and_click_template] 匹配度不足阈值({threshold:.2f})")
            return False, None
            
    except Exception as e:
        print(f"[match_and_click_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def find_and_click_template(region, template_path, threshold):
    """
    在指定区域查找并点击模板
    
    Args:
        region (tuple): 截图区域 (x, y, width, height)
        template_path (str): 模板图片路径
        threshold (float): 匹配阈值
        
    Returns:
        bool: 是否匹配成功
    """
    try:
        # 获取当前屏幕彩色截图
        print(f"[find_and_click_template] 截图区域: {region}")
        screenshot = pyautogui.screenshot(region=region)
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 进行模板匹配并点击
        matched, pos = match_and_click_template(screenshot_cv, template_path, threshold, region)
        
        return matched
    except Exception as e:
        print(f"[find_and_click_template] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False