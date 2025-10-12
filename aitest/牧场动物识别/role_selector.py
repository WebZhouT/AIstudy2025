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
# 导入自定义的图像工具模块
from image_utils2 import find_and_click_image
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, window_title
from drag_scroll import drag_from_to

roleList = ['鱼的仓库2','社区装饰123','2J药材44','0仓整2','3J药品123',]
# roleList = ['芊','兄弟情义','佑手','潇湘天奇','天雪','妙手','嘻哈','狮驼岭',]
# '兽决仓库002','长寿图库','家具存放123','麒麟图库',
# '传说中','席',  这2个现在没养殖不需要访问
def capture_window_region():
    """捕获窗口区域"""
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        return None, None
    
    # 检查窗口是否最小化
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.1)
    
    # 获取窗口区域
    x, y, width, height = get_window_position(hwnd)
    region = (x, y, x + width, y + height)
    
    # 截取窗口区域
    screenshot = ImageGrab.grab(bbox=region)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    return screenshot, (x, y, width, height)

def find_role_position(role_name, window_region):
    """查找角色位置 - 优化版本，直接匹配角色名"""
    screenshot, (x, y, width, height) = window_region
    
    # 初始化OCR
    ocr_engine = RapidOCR()
    
    # 进行OCR识别
    result, elapse = ocr_engine(screenshot)
    
    # 添加调试信息：打印所有识别到的文本
    print("OCR识别到的所有文本:")
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
                    
                    print(f"找到角色 '{role_name}'，位置: ({center_x}, {center_y})，置信度: {confidence_float:.2f}")
                    print(f"匹配文本: '{text}'")
                    return {
                        'x': center_x,
                        'y': center_y,
                        'name': role_name,
                        'confidence': confidence_float,
                        'box': box
                    }
    
    return None

def swipe_window(direction='down', window_region=None):
    """滑动窗口 - 直接使用drag_scroll.py中的函数"""
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
    print(f"向{direction}滑动窗口: 从({center_x}, {start_y})到({center_x}, {end_y})")
    drag_from_to(center_x, start_y, center_x, end_y)
    time.sleep(1)  # 等待拖拽效果
    
    return True

def get_role_names_from_screenshot(screenshot, window_info):
    """直接从截图中提取角色名"""
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
    
    print(f"从截图中提取到的角色名: {set(role_names)}")
    return set(role_names)

def cycle_select_roles(index):
    """循环选择指定索引的角色 - 通过比较角色名集合判断边界"""
    if index >= len(roleList):
        print("角色索引超出范围")
        return False
    
    role_name = roleList[index]
    print(f"开始选择角色: {role_name} (第{index + 1}个)")
    
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        print("未找到游戏窗口")
        return False
    
    x, y, width, height = get_window_position(hwnd)
    
    # 尝试点击选择按钮出现选择框
    if find_and_click_image('./role_selector/select.png', confidence=0.6,  region=(x, y, width, height)):
        print("成功点击选择按钮，等待选择界面弹出")
        time.sleep(3)  # 增加等待时间，确保选择界面完全弹出
        
        # 现在在选择界面中查找角色
        max_scroll_attempts = 60  # 最大拖拽次数
        scroll_count = 0
        max_retry_attempts = 3  # 最大重试次数
        retry_count = 0
        same_role_count = 0  # 相同角色集合计数
        last_role_set = set()  # 上一次的角色名集合
        current_direction = 'down'  # 当前滑动方向
        consecutive_empty_sets = 0  # 连续空集合计数
        
        while scroll_count < max_scroll_attempts and retry_count < max_retry_attempts:
            # 获取当前窗口区域
            window_region = capture_window_region()
            if window_region[0] is None:  # 明确检查是否为None
                print("无法获取窗口区域")
                retry_count += 1
                time.sleep(1)
                continue
            
            screenshot, window_info = window_region
            
            # 查找角色位置
            role_position = find_role_position(role_name, window_region)
            
            if role_position:
                # 找到角色，点击选择
                pyautogui.click(role_position['x'], role_position['y'])
                print(f"成功选择角色: {role_name}")
                time.sleep(2)  # 等待角色选择完成
                return True
            else:
                print(f"未找到角色 '{role_name}'，尝试滚动查找")
                
                # 直接使用截图进行OCR识别
                current_role_set = get_role_names_from_screenshot(screenshot, window_info)
                
                # 检查角色名集合是否为空
                if not current_role_set:
                    consecutive_empty_sets += 1
                    print(f"未识别到任何角色名，连续空集合计数: {consecutive_empty_sets}")
                    
                    # 如果连续多次都是空集合，可能是滑动到底部或顶部
                    if consecutive_empty_sets >= 3:
                        print("连续多次未识别到角色名，改变滑动方向")
                        current_direction = 'up' if current_direction == 'down' else 'down'
                        consecutive_empty_sets = 0
                        same_role_count = 0
                else:
                    consecutive_empty_sets = 0
                
                # 检查角色名集合是否相同（判断是否滑动到底部）
                if current_role_set and current_role_set == last_role_set:
                    same_role_count += 1
                    print(f"角色名集合相同，计数: {same_role_count}/2")
                    
                    # 如果连续2次角色名集合相同，改变滑动方向
                    if same_role_count >= 2:
                        print(f"连续2次角色名集合相同，改变滑动方向")
                        current_direction = 'up' if current_direction == 'down' else 'down'
                        same_role_count = 0
                        # 执行一次反方向滑动
                        if swipe_window(current_direction, window_region):
                            scroll_count += 1
                            print(f"第{scroll_count}次滑动，方向: {current_direction}")
                        else:
                            print("滑动失败")
                            retry_count += 1
                        continue
                else:
                    same_role_count = 0
                
                last_role_set = current_role_set
                
                # 按照当前方向滑动
                if swipe_window(current_direction, window_region):
                    scroll_count += 1
                    print(f"第{scroll_count}次滑动，方向: {current_direction}")
                else:
                    print("滑动失败")
                    retry_count += 1
        
        # 如果连续3次匹配都失败，显示错误提示
        if retry_count >= max_retry_attempts:
            print("连续3次匹配失败，显示错误提示")
            show_alert(f"角色 {role_name} 选择失败，请检查游戏状态", use_toast=True)
            return False
        
        print(f"滑动{max_scroll_attempts}次后仍未找到角色: {role_name}")
        return False
    else:
        print("未能点击选择按钮")
        return False