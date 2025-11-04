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

def find_drag_area_and_scroll(drag_area_template, target_text, threshold=0.7):
    """
    匹配拖拽区域并实现上下滚动功能，查找目标文字
    
    Args:
        drag_area_template: 拖拽区域模板图片路径
        target_text: 要查找的目标文字
        threshold: 匹配阈值
        
    Returns:
        tuple or None: 找到的目标文字中心坐标 (x, y)，未找到则返回None
    """
    print(f"[find_drag_area_and_scroll] 开始匹配拖拽区域，查找文字: {target_text}")
    hwnd = find_window_by_title(window_title)
    if hwnd:
        x, y, width, height = get_window_position(hwnd)
        # 1. 通过drag_area_template获取区域
        area_btn_location = pyautogui.locateOnScreen(drag_area_template, confidence=threshold, region=(x, y, width, height))
        if not area_btn_location:
            print("[find_drag_area_and_scroll] 未找到拖拽区域模板")
            return None
        
        # 基于模板位置定义识别区域（基于整个屏幕的坐标）
        regionScrollAim = (
            int(area_btn_location.left),
            int(area_btn_location.top),
            int(area_btn_location.width),
            int(area_btn_location.height)
        )
        print(f"[find_drag_area_and_scroll] 基于模板定义的识别区域: {regionScrollAim}")
        
        # 2. 循环查找目标文字
        max_scroll_attempts = 60  # 最大拖拽次数
        scroll_count = 0
        max_retry_attempts = 3  # 最大重试次数
        retry_count = 0
        
        # 记录上一次OCR识别到的文字，用于判断是否到达底部
        last_recognized_texts = []
        
        while retry_count < max_retry_attempts and not stop_event.is_set():
            scroll_count = 0
            found_target = False
            
            while scroll_count < max_scroll_attempts and not stop_event.is_set():
                # 截取当前区域进行OCR识别
                try:
                    # 截取regionScrollAim区域进行OCR
                    screenshot = pyautogui.screenshot(region=regionScrollAim)
                    screenshot_np = np.array(screenshot)
                    
                    # 使用OCR识别文字
                    if ocr is None:
                        print("[find_drag_area_and_scroll] OCR引擎未初始化")
                        return None
                        
                    ocr_result, _ = ocr(screenshot_np)
                    
                    # 打印所有OCR识别到的文字内容，便于调试
                    print("[find_drag_area_and_scroll] OCR识别到的所有文字:")
                    for i, text_info in enumerate(ocr_result):
                        if text_info and len(text_info) > 1:
                            print(f"  {i+1}. 文字: '{text_info[1]}', 置信度: {text_info[2]:.4f}")
                    
                    current_recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
                    
                    print(f"[find_drag_area_and_scroll] 当前OCR识别结果: {current_recognized_texts}")
                    
                    # 检查是否有识别结果
                    if ocr_result:
                        # 检查目标文字是否在识别结果中
                        for text_info in ocr_result:
                            if len(text_info) > 1 and target_text in text_info[1]:
                                # 获取文字位置信息
                                box = text_info[0]  # 文字包围盒
                                # 计算文字区域中心点
                                x_coords = [point[0] for point in box]
                                y_coords = [point[1] for point in box]
                                center_x = sum(x_coords) / len(x_coords)
                                center_y = sum(y_coords) / len(y_coords)
                                
                                # 转换为屏幕坐标（基于整个屏幕）
                                screen_x = regionScrollAim[0] + int(center_x)
                                screen_y = regionScrollAim[1] + int(center_y)
                                
                                print(f"[find_drag_area_and_scroll] 找到目标文字 '{target_text}'，坐标: ({screen_x}, {screen_y})")
                                found_target = True
                                return (screen_x, screen_y)
                    
                    # 判断是否到达底部：连续2次OCR结果相同
                    if (len(last_recognized_texts) > 0 and 
                        len(current_recognized_texts) > 0 and
                        set(last_recognized_texts) == set(current_recognized_texts)):
                        print("[find_drag_area_and_scroll] 检测到滑动到底部，准备反向滑动")
                        break
                    
                    # 更新上一次识别结果
                    last_recognized_texts = current_recognized_texts.copy()
                    
                    # 如果没有找到目标文字，执行向下拖拽操作
                    print(f"[find_drag_area_and_scroll] 未找到目标文字 '{target_text}'，执行向下拖拽操作...")
                    
                    # 根据regionScrollAim区域计算拖拽起始和结束点（向下滚动）
                    x, y, w, h = regionScrollAim
                    # 设置拖拽起始点（区域中部偏下）
                    start_x = x + w // 2
                    start_y = y + int(h * 0.8)
                    # 设置拖拽结束点（区域中部偏上）
                    end_x = x + w // 2
                    end_y = y + int(h * 0.5)
                    
                    # 执行拖拽操作
                    drag_from_to(start_x, start_y, end_x, end_y)
                    time.sleep(0.5)  # 等待拖拽效果
                    scroll_count += 1
                    
                except Exception as e:
                    print(f"[find_drag_area_and_scroll] OCR识别出错: {str(e)}")
                    traceback.print_exc()
                    
                    # 即使OCR出错，也执行拖拽操作
                    x, y, w, h = regionScrollAim
                    start_x = x + w // 2
                    start_y = y + int(h * 0.7)
                    end_x = x + w // 2
                    end_y = y + int(h * 0.5)
                    
                    drag_from_to(start_x, start_y, end_x, end_y)
                    time.sleep(0.5)
                    scroll_count += 1
            
            # 如果已经找到目标，直接返回
            if found_target:
                break
                
            # 如果滑动到底部但未找到目标，执行反向滑动
            retry_count += 1
            if retry_count < max_retry_attempts:
                print(f"[find_drag_area_and_scroll] 第{retry_count}次重试，反向滑动{scroll_count}次")
                
                # 反向滑动（向上滚动）完整的向下滑动次数，确保回到顶部
                reverse_scroll_count = scroll_count
                for i in range(reverse_scroll_count):
                    if stop_event.is_set():
                        break
                        
                    x, y, w, h = regionScrollAim
                    # 反向拖拽：从上方拖到下方
                    start_x = x + w // 2
                    start_y = y + int(h * 0.3)
                    end_x = x + w // 2
                    end_y = y + int(h * 0.7)
                    
                    drag_from_to(start_x, start_y, end_x, end_y)
                    time.sleep(0.5)

                # 清空上一次识别结果，重新开始
                last_recognized_texts = []
            else:
                print(f"[find_drag_area_and_scroll] 已达到最大重试次数{max_retry_attempts}，未找到目标文字 '{target_text}'")
                return None
        
        return None