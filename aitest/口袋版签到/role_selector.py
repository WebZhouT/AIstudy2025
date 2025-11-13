# 初始启动游戏后，角色选择进入游戏
# role_selector.py
import cv2
import numpy as np
import pyautogui
import time
from PIL import ImageGrab
import win32gui
import win32con
from rapidocr_onnxruntime import RapidOCR
import os
import traceback

# 导入自定义的图像工具模块
from image_utils import find_and_click_template, click_at_window_coord, save_debug_screenshot
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, window_title, roleList
from drag_scroll import drag_from_to

def capture_window_region():
    """捕获窗口区域"""
    try:
        hwnd = find_window_by_title(window_title)
        if not hwnd:
            print("[capture_window_region] 错误：无法找到游戏窗口句柄")
            return None, None
        
        # 验证窗口是否有效
        if not win32gui.IsWindow(hwnd):
            print("[capture_window_region] 错误：窗口句柄无效")
            return None, None
        
        # 检查窗口是否最小化
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)
        
        # 获取窗口区域
        x, y, width, height = get_window_position(hwnd)
        
        # 截取窗口区域
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # 保存调试截图
        save_debug_screenshot(screenshot_cv, "window_capture", (x, y, width, height))
        
        return screenshot_cv, (x, y, width, height)
    except Exception as e:
        print(f"[capture_window_region] 截取窗口区域时发生错误: {str(e)}")
        traceback.print_exc()
        return None, None

def find_role_position(role_name, window_region):
    """查找角色位置 - 优化版本，直接匹配角色名"""
    try:
        screenshot, (x, y, width, height) = window_region
        
        # 初始化OCR
        ocr_engine = RapidOCR()
        
        # 进行OCR识别
        result, elapse = ocr_engine(screenshot)
        
        # 添加调试信息：打印所有识别到的文本
        print("[find_role_position] OCR识别到的所有文本:")
        if result:
            for item in result:
                text = item[1] if len(item) > 1 else "无文本"
                confidence = item[2] if len(item) > 2 else 0
                print(f"  文本: '{text}', 置信度: {confidence}")
        else:
            print("   无结果")
        
        if result:
            for item in result:
                if len(item) > 1:
                    text = item[1]
                    confidence = item[2] if len(item) > 2 else 0
                    
                    # 确保confidence是数字类型
                    try:
                        confidence_float = float(confidence)
                    except (ValueError, TypeError):
                        confidence_float = 0.0
                    
                    # 直接匹配角色名
                    if role_name in text and confidence_float > 0.6:
                        # 计算角色框的中心位置
                        box = item[0]
                        center_x = int((box[0][0] + box[2][0]) / 2) + x
                        center_y = int((box[0][1] + box[2][1]) / 2) + y
                        
                        print(f"[find_role_position] 找到角色 '{role_name}'，位置: ({center_x}, {center_y})，置信度: {confidence_float:.2f}")
                        print(f"[find_role_position] 匹配文本: '{text}'")
                        return {
                            'x': center_x,
                            'y': center_y,
                            'name': role_name,
                            'confidence': confidence_float,
                            'box': box
                        }
        
        print(f"[find_role_position] 未找到角色: {role_name}")
        return None
    except Exception as e:
        print(f"[find_role_position] 查找角色位置时发生错误: {str(e)}")
        traceback.print_exc()
        return None

def swipe_window(direction='down', window_region=None):
    """滑动窗口"""
    try:
        if not window_region:
            screenshot, (x, y, width, height) = capture_window_region()
            if not screenshot:
                return False
        else:
            screenshot, (x, y, width, height) = window_region
        
        # 计算滑动起始和结束位置
        center_x = x + width // 2 + 60
        
        if direction == 'down':
            # 向下滑动：从下方拖到上方（显示下方内容）
            start_y = y + int(height * 0.8)
            end_y = y + int(height * 0.5)
        elif direction == 'up':
            # 向上滑动：从上方拖到下方（显示上方内容）
            start_y = y + int(height * 0.3)
            end_y = y + int(height * 0.7)
        else:
            return False
        
        # 直接使用drag_scroll.py中的拖拽函数
        print(f"[swipe_window] 向{direction}滑动窗口: 从({center_x}, {start_y})到({center_x}, {end_y})")
        drag_from_to(center_x, start_y, center_x, end_y)
        time.sleep(1)  # 等待拖拽效果
        
        return True
    except Exception as e:
        print(f"[swipe_window] 滑动窗口时发生错误: {str(e)}")
        return False

def get_role_names_from_screenshot(screenshot, window_info):
    """直接从截图中提取角色名"""
    try:
        if screenshot is None:
            return set()
        
        # 初始化OCR
        ocr_engine = RapidOCR()
        
        # 进行OCR识别
        result, elapse = ocr_engine(screenshot)
        
        # 提取角色名
        role_names = []
        if result:
            for item in result:
                if len(item) > 1:
                    text = item[1]
                    # 检查这个文本是否在角色列表中
                    for role in roleList:
                        if role in text:
                            role_names.append(role)
                            break
        
        print(f"[get_role_names_from_screenshot] 从截图中提取到的角色名: {set(role_names)}")
        return set(role_names)
    except Exception as e:
        print(f"[get_role_names_from_screenshot] 提取角色名时发生错误: {str(e)}")
        return set()

def cycle_select_roles(index):
    """循环选择指定索引的角色"""
    try:
        if index >= len(roleList):
            print("[cycle_select_roles] 角色索引超出范围")
            return False
        
        role_name = roleList[index]
        print(f"[cycle_select_roles] 开始选择角色: {role_name} (第{index + 1}个)")
        
        hwnd = find_window_by_title(window_title)
        if not hwnd:
            print("[cycle_select_roles] 未找到游戏窗口")
            return False
        
        x, y, width, height = get_window_position(hwnd)
        
        # 尝试点击选择按钮出现选择框
        print("[cycle_select_roles] 尝试点击切换角色按钮")
        click_result = find_and_click_template((x, y, width, height), 'changerole.png', 0.7, grayscale=False)
        
        if click_result:
            print("[cycle_select_roles] 成功点击选择按钮，等待选择界面弹出")
            time.sleep(3)  # 增加等待时间，确保选择界面完全弹出
            
            # 现在在选择界面中查找角色
            max_scroll_attempts = 20  # 减少最大拖拽次数
            scroll_count = 0
            max_retry_attempts = 2   # 减少最大重试次数
            retry_count = 0
            same_role_count = 0  # 相同角色集合计数
            last_role_set = set()  # 上一次的角色名集合
            current_direction = 'down'  # 当前滑动方向
            consecutive_empty_sets = 0  # 连续空集合计数
            
            while scroll_count < max_scroll_attempts and retry_count < max_retry_attempts:
                # 获取当前窗口区域
                window_region = capture_window_region()
                if window_region[0] is None:
                    print("[cycle_select_roles] 无法获取窗口区域")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                screenshot, window_info = window_region
                
                # 查找角色位置
                role_position = find_role_position(role_name, window_region)
                
                if role_position:
                    # 找到角色，点击选择
                    success = click_at_window_coord(hwnd, role_position['x'], role_position['y'])
                    if success:
                        print(f"[cycle_select_roles] 成功选择角色: {role_name}")
                        time.sleep(2)  # 等待角色选择完成
                        return True
                    else:
                        print(f"[cycle_select_roles] 点击角色失败: {role_name}")
                
                print(f"[cycle_select_roles] 未找到角色 '{role_name}'，尝试滚动查找")
                
                # 直接使用截图进行OCR识别
                current_role_set = get_role_names_from_screenshot(screenshot, window_info)
                
                # 检查角色名集合是否为空
                if not current_role_set:
                    consecutive_empty_sets += 1
                    print(f"[cycle_select_roles] 未识别到任何角色名，连续空集合计数: {consecutive_empty_sets}")
                    
                    # 如果连续多次都是空集合，可能是滑动到底部或顶部
                    if consecutive_empty_sets >= 2:
                        print("[cycle_select_roles] 连续多次未识别到角色名，改变滑动方向")
                        current_direction = 'up' if current_direction == 'down' else 'down'
                        consecutive_empty_sets = 0
                        same_role_count = 0
                else:
                    consecutive_empty_sets = 0
                
                # 检查角色名集合是否相同（判断是否滑动到底部）
                if current_role_set and current_role_set == last_role_set:
                    same_role_count += 1
                    print(f"[cycle_select_roles] 角色名集合相同，计数: {same_role_count}/2")
                    
                    # 如果连续2次角色名集合相同，改变滑动方向
                    if same_role_count >= 2:
                        print(f"[cycle_select_roles] 连续2次角色名集合相同，改变滑动方向")
                        current_direction = 'up' if current_direction == 'down' else 'down'
                        same_role_count = 0
                        # 执行一次反方向滑动
                        if swipe_window(current_direction, window_region):
                            scroll_count += 1
                            print(f"[cycle_select_roles] 第{scroll_count}次滑动，方向: {current_direction}")
                        else:
                            print("[cycle_select_roles] 滑动失败")
                            retry_count += 1
                        continue
                else:
                    same_role_count = 0
                
                last_role_set = current_role_set
                
                # 按照当前方向滑动
                if swipe_window(current_direction, window_region):
                    scroll_count += 1
                    print(f"[cycle_select_roles] 第{scroll_count}次滑动，方向: {current_direction}")
                else:
                    print("[cycle_select_roles] 滑动失败")
                    retry_count += 1
            
            # 如果连续匹配失败，显示错误提示
            if retry_count >= max_retry_attempts:
                print("[cycle_select_roles] 连续匹配失败，显示错误提示")
                show_alert(f"角色 {role_name} 选择失败，请检查游戏状态", use_toast=True)
                return False
            
            print(f"[cycle_select_roles] 滑动{max_scroll_attempts}次后仍未找到角色: {role_name}")
            return False
        else:
            print("[cycle_select_roles] 未能点击选择按钮")
            return False
    except Exception as e:
        print(f"[cycle_select_roles] 选择角色时发生错误: {str(e)}")
        traceback.print_exc()
        return False