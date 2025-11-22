# drag_scroll.py  匹配拖拽区域并实现上下滚动功能，查找目标文字后返回坐标匹配
import pyautogui
import numpy as np
import time
import traceback
import threading
import win32gui
import win32con
# 图像识别
from rapidocr_onnxruntime import RapidOCR
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 初始化OCR引擎
ocr = RapidOCR()
stop_event = threading.Event()

def drag_from_to(start_x, start_y, end_x, end_y):
    """
    从起始坐标拖拽到终止坐标，使用Windows API而不是移动鼠标
    
    Args:
        start_x: 起始点x坐标
        start_y: 起始点y坐标
        end_x: 终止点x坐标
        end_y: 终止点y坐标
    """
    print(f"[drag_from_to] 执行拖拽操作: 从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
    
    # 使用Windows API进行拖拽操作，不移动鼠标
    hwnd = find_window_by_title(window_title)
    if hwnd:
        # 转换起始点坐标为客户区坐标
        start_point = (start_x, start_y)
        client_start_point = win32gui.ScreenToClient(hwnd, start_point)
        
        # 转换终点坐标为客户区坐标
        end_point = (end_x, end_y)
        client_end_point = win32gui.ScreenToClient(hwnd, end_point)
        
        # 发送鼠标按下消息
        start_lParam = (client_start_point[1] << 16) | (client_start_point[0] & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, start_lParam)
        
        # 增加移动步数以使拖拽更平滑
        steps = 30
        for i in range(steps + 1):
            intermediate_x = client_start_point[0] + (client_end_point[0] - client_start_point[0]) * i // steps
            intermediate_y = client_start_point[1] + (client_end_point[1] - client_start_point[1]) * i // steps
            intermediate_lParam = (intermediate_y << 16) | (intermediate_x & 0xFFFF)
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, intermediate_lParam)
            time.sleep(0.01)
        
        # 发送鼠标抬起消息
        end_lParam = (client_end_point[1] << 16) | (client_end_point[0] & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, end_lParam)
        
        time.sleep(0.1)
    else:
        print("[drag_from_to] 未找到窗口句柄，无法执行拖拽操作")

def find_drag_area_and_scroll(drag_area_template, target_text, threshold=0.6):
    """
    匹配拖拽区域并实现上下滚动功能，查找目标文字
    """
    print(f"[find_drag_area_and_scroll] 开始匹配拖拽区域，查找文字: {target_text}")
    
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        print("[find_drag_area_and_scroll] 未找到窗口句柄")
        return None
        
    try:
        win_x, win_y, win_width, win_height = get_window_position(hwnd)
        print(f"[find_drag_area_and_scroll] 窗口位置: x={win_x}, y={win_y}, width={win_width}, height={win_height}")
        
        # 1. 在窗口区域内查找拖拽区域模板
        area_btn_location = pyautogui.locateOnScreen(
            drag_area_template, 
            confidence=threshold, 
            region=(win_x, win_y, win_width, win_height)
        )
        
        if not area_btn_location:
            print(f"[find_drag_area_and_scroll] 未找到拖拽区域模板: {drag_area_template}")
            return None
        
        # 基于模板位置定义识别区域（窗口相对坐标）
        region_left = int(area_btn_location.left) - win_x
        region_top = int(area_btn_location.top) - win_y
        region_width = int(area_btn_location.width)
        region_height = int(area_btn_location.height)
        
        print(f"[find_drag_area_and_scroll] 识别区域 (窗口相对坐标): left={region_left}, top={region_top}, width={region_width}, height={region_height}")
        
        # 2. 循环查找目标文字
        max_scroll_attempts = 60
        scroll_count = 0
        max_retry_attempts = 3
        retry_count = 0
        last_recognized_texts = []
        
        while retry_count < max_retry_attempts and not stop_event.is_set():
            scroll_count = 0
            found_target = False
            
            while scroll_count < max_scroll_attempts and not stop_event.is_set():
                try:
                    # 截取窗口内特定区域进行OCR
                    screenshot = pyautogui.screenshot(
                        region=(
                            win_x + region_left,
                            win_y + region_top, 
                            region_width, 
                            region_height
                        )
                    )
                    screenshot_np = np.array(screenshot)
                    
                    if ocr is None:
                        print("[find_drag_area_and_scroll] OCR引擎未初始化")
                        return None
                        
                    ocr_result, _ = ocr(screenshot_np)
                    
                    # 打印OCR识别结果用于调试
                    print("[find_drag_area_and_scroll] OCR识别到的所有文字:")
                    recognized_texts = []
                    for i, text_info in enumerate(ocr_result):
                        if text_info and len(text_info) > 1:
                            text = text_info[1]
                            confidence = text_info[2]
                            print(f"  {i+1}. 文字: '{text}', 置信度: {confidence:.4f}")
                            recognized_texts.append(text)
                    
                    print(f"[find_drag_area_and_scroll] 当前OCR识别结果: {recognized_texts}")
                    
                    # 检查目标文字
                    for text_info in ocr_result:
                        if len(text_info) > 1 and target_text in text_info[1]:
                            # 计算文字中心点（相对于截图区域）
                            box = text_info[0]
                            x_coords = [point[0] for point in box]
                            y_coords = [point[1] for point in box]
                            center_x = sum(x_coords) / len(x_coords)
                            center_y = sum(y_coords) / len(y_coords)
                            
                            # 转换为屏幕坐标
                            screen_x = win_x + region_left + int(center_x)
                            screen_y = win_y + region_top + int(center_y)
                            
                            print(f"[find_drag_area_and_scroll] 找到目标文字 '{target_text}'，坐标: ({screen_x}, {screen_y})")
                            return (screen_x, screen_y)
                    
                    # 判断是否到达底部
                    if (len(last_recognized_texts) > 0 and 
                        len(recognized_texts) > 0 and
                        set(last_recognized_texts) == set(recognized_texts)):
                        print("[find_drag_area_and_scroll] 检测到滑动到底部，准备反向滑动")
                        break
                    
                    last_recognized_texts = recognized_texts.copy()
                    
                    # 执行向下拖拽
                    print(f"[find_drag_area_and_scroll] 未找到目标文字 '{target_text}'，执行向下拖拽操作...")
                    
                    # 计算拖拽点（基于窗口坐标）
                    start_x = win_x + region_left + region_width // 2
                    start_y = win_y + region_top + int(region_height * 0.8)
                    end_x = win_x + region_left + region_width // 2
                    end_y = win_y + region_top + int(region_height * 0.5)
                    
                    drag_from_to(start_x, start_y, end_x, end_y)
                    time.sleep(0.5)
                    scroll_count += 1
                    
                except Exception as e:
                    print(f"[find_drag_area_and_scroll] OCR识别或拖拽出错: {str(e)}")
                    traceback.print_exc()
                    break
            
            if found_target:
                break
                
            # 反向滑动逻辑
            retry_count += 1
            if retry_count < max_retry_attempts:
                print(f"[find_drag_area_and_scroll] 第{retry_count}次重试，反向滑动{scroll_count}次")
                
                for i in range(scroll_count):
                    if stop_event.is_set():
                        break
                    
                    start_x = win_x + region_left + region_width // 2
                    start_y = win_y + region_top + int(region_height * 0.3)
                    end_x = win_x + region_left + region_width // 2
                    end_y = win_y + region_top + int(region_height * 0.7)
                    
                    drag_from_to(start_x, start_y, end_x, end_y)
                    time.sleep(0.5)
                
                last_recognized_texts = []
            else:
                print(f"[find_drag_area_and_scroll] 已达到最大重试次数{max_retry_attempts}，未找到目标文字 '{target_text}'")
                return None
        
        return None
        
    except Exception as e:
        print(f"[find_drag_area_and_scroll] 函数执行出错: {str(e)}")
        traceback.print_exc()
        return None