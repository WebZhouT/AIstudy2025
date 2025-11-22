import cv2
import numpy as np
import pyautogui
import time
import os
import datetime
import datetime
from PIL import ImageGrab
from rapidocr_onnxruntime import RapidOCR
from image_utils import find_image_position
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 导入自定义的图像工具模块
from image_utils import find_and_click_image, click_at_window_coord, mark_and_save_screenshot
# 获得牧场管理员目标匹配方法
from recognize_simple_target import aim,recognize_simple_target
def return_home_and_release():
    """4. 点击管理员回家放出"""
    print('点击管理员回家放出')
    # 点击左上角地图
    find_and_click_image('./breeding_image/lefttop.png', confidence=0.65)
    time.sleep(1)
    # 点击x输入
    find_and_click_image('./breeding_image/xinput.png', confidence=0.65)
    time.sleep(0.5)
    hwnd = find_window_by_title(window_title)
    xsuccess = click_sequence_numbers(hwnd, "./breeding_image/number_keyboard.png", "29")
    if xsuccess:
        # 点击确定按钮
        find_and_click_image('./breeding_image/sure.png', confidence=0.65)
    time.sleep(1)
    ysuccess = click_sequence_numbers(hwnd, "./breeding_image/number_keyboard.png", "32")
    if ysuccess:
        # 点击确定按钮
        find_and_click_image('./breeding_image/sure.png', confidence=0.65)
    time.sleep(2)
    find_and_click_image('./breeding_image/closemap.png', confidence=0.65)
    # 点击管理员回家咯
    # 找到牧场管理员并进行点击操作
    admin_position = recognize_simple_target(aim)    
    if admin_position:
        print(f"找到管理员，位置: {admin_position}，相似度: {admin_position.get('confidence', 0):.2f}")
        hwnd = find_window_by_title(window_title)
        click_at_window_coord(hwnd,admin_position['x'], admin_position['y'])
        time.sleep(1)
        # 回家回家
        find_and_click_image('./breeding_image/gohome.png', confidence=0.65)
        time.sleep(1)
        # 放出全部动物
        # 点击宠物
        find_and_click_image('./breeding_image/pet.png', confidence=0.65)
        time.sleep(1)
        # 点击牧场空间
        find_and_click_image('./breeding_image/area.png', confidence=0.65)
        time.sleep(0.5)
        # 点击全部放出
        find_and_click_image('./breeding_image/giveout.png', confidence=0.65)
        time.sleep(1)
        find_and_click_image('./breeding_image/close.png', confidence=0.65)
def click_sequence_numbers(hwnd, template_path, number_sequence, threshold=0.8, ocr_engine=None):
    """
    简化版函数，用于点击数字序列（如密码）
    
    Args:
        hwnd (int): 窗口句柄
        template_path (str): 数字键盘模板图片路径
        number_sequence (str): 需要点击的数字序列，如 "19"
        threshold (float): 模板匹配阈值，默认0.8
        ocr_engine (RapidOCR, optional): OCR引擎实例
        
    Returns:
        bool: 是否成功完成所有点击操作
    """
    result = click_numbers_on_keyboard(hwnd, template_path, number_sequence, threshold, ocr_engine)
    return result['success']
def click_numbers_on_keyboard(hwnd, template_path, numbers_to_click, threshold=0.8, ocr_engine=None):
    """
    在窗口中匹配数字键盘模板，识别数字位置并点击指定数字
    
    Args:
        hwnd (int): 窗口句柄
        template_path (str): 数字键盘模板图片路径
        numbers_to_click (str or list): 需要点击的数字序列，如 "19" 或 ['1', '9']
        threshold (float): 模板匹配阈值，默认0.8
        ocr_engine (RapidOCR, optional): OCR引擎实例，如果未提供则创建新的实例
        
    Returns:
        dict: 操作结果
              {
                  'success': bool, 是否成功完成所有点击操作
                  'clicked_numbers': list, 已点击的数字列表
                  'failed_numbers': list, 未找到的数字列表
                  'keyboard_region': tuple, 键盘区域坐标
              }
    """
    try:
        # 如果没有提供OCR引擎实例，则创建一个新的
        if ocr_engine is None:
            ocr_engine = RapidOCR()
        
        # 将输入转换为列表格式
        if isinstance(numbers_to_click, str):
            number_list = list(numbers_to_click)
        else:
            number_list = list(numbers_to_click)
        
        # 获取窗口位置
        window_x, window_y, window_width, window_height = get_window_position(hwnd)
        window_region = (window_x, window_y, window_width, window_height)
        
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[click_numbers_on_keyboard] 警告: 无法读取模板图片 {template_path}")
            return {
                'success': False,
                'clicked_numbers': [],
                'failed_numbers': number_list,
                'keyboard_region': None
            }
        
        # 截取整个窗口区域的屏幕截图
        window_screenshot = pyautogui.screenshot(region=window_region)
        screenshot_cv = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
        
        # 进行模板匹配
        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[click_numbers_on_keyboard] 键盘模板匹配度: {max_val:.2f} (阈值: {threshold})")
        
        if max_val >= threshold:
            # 获取模板尺寸
            h, w = template.shape[:2]
            
            # 计算匹配区域在屏幕上的绝对坐标
            match_x, match_y = max_loc
            keyboard_x = window_x + match_x
            keyboard_y = window_y + match_y
            keyboard_width = w
            keyboard_height = h
            
            # 定义键盘区域
            keyboard_region = (
                keyboard_x,
                keyboard_y,
                keyboard_width,
                keyboard_height
            )
            
            print(f"[click_numbers_on_keyboard] 找到数字键盘区域: {keyboard_region}")
            
            # 对键盘区域进行OCR识别，获取各数字的位置信息
            ocr_result, _ = ocr_engine(np.array(pyautogui.screenshot(region=keyboard_region)))
            
            # 调试输出OCR识别的所有内容
            print(f"[click_numbers_on_keyboard] OCR识别原始结果: {ocr_result}")
            if ocr_result:
                print("[click_numbers_on_keyboard] 详细OCR识别结果:")
                for i, item in enumerate(ocr_result):
                    if len(item) >= 3:
                        print(f"  [{i}] 文本: '{item[1]}', 置信度: {item[2]}, 坐标: {item[0]}")
                    else:
                        print(f"  [{i}] 不完整数据: {item}")
            else:
                print("[click_numbers_on_keyboard] OCR未识别到任何内容")
            
            # 解析OCR结果，构建数字位置映射表
            number_positions = {}
            if ocr_result:
                for item in ocr_result:
                    if len(item) >= 3:
                        recognized_text = item[1]
                        confidence = float(item[2])
                        coordinates = item[0]
                        
                        # 如果识别结果是单个数字，则记录其位置
                        if len(recognized_text) == 1 and recognized_text.isdigit():
                            # 计算数字在屏幕上的中心位置
                            coords_array = np.array(coordinates)
                            center_x = int(np.mean(coords_array[:, 0])) + keyboard_x
                            center_y = int(np.mean(coords_array[:, 1])) + keyboard_y
                            
                            number_positions[recognized_text] = {
                                'position': (center_x, center_y),
                                'confidence': confidence
                            }
                            print(f"[click_numbers_on_keyboard] 识别到数字 {recognized_text} 位于 ({center_x}, {center_y})")
            
            # 策略1: 如果OCR没有识别到所有数字，尝试基于已知数字的位置推断缺失数字的位置
            missing_numbers = [num for num in number_list if num not in number_positions]
            if missing_numbers:
                print(f"[click_numbers_on_keyboard] OCR未识别到的数字: {missing_numbers}")
                print("[click_numbers_on_keyboard] 尝试基于已知数字推断缺失数字位置...")
                
                # 基于实际数字键盘布局推断位置
                inferred_positions = infer_missing_number_positions(number_positions, keyboard_region, missing_numbers)
                
                # 将推断的位置添加到number_positions中
                for num, pos_info in inferred_positions.items():
                    if num not in number_positions:
                        number_positions[num] = pos_info
                        print(f"[click_numbers_on_keyboard] 推断数字 {num} 位于 {pos_info['position']}")
            
            # 策略2: 如果仍然有缺失数字，尝试扩展OCR识别区域
            still_missing = [num for num in number_list if num not in number_positions]
            if still_missing:
                print(f"[click_numbers_on_keyboard] 仍有未找到的数字: {still_missing}")
                print("[click_numbers_on_keyboard] 尝试扩展OCR识别区域...")
                
                # 扩展键盘区域（上下左右各扩展20像素）
                expanded_keyboard_region = (
                    max(0, keyboard_x - 20),
                    max(0, keyboard_y - 20),
                    keyboard_width + 40,
                    keyboard_height + 40
                )
                
                # 在扩展区域重新进行OCR识别
                expanded_ocr_result, _ = ocr_engine(np.array(pyautogui.screenshot(region=expanded_keyboard_region)))
                
                if expanded_ocr_result:
                    for item in expanded_ocr_result:
                        if len(item) >= 3:
                            recognized_text = item[1]
                            confidence = float(item[2])
                            coordinates = item[0]
                            
                            # 如果识别结果是单个数字，则记录其位置
                            if len(recognized_text) == 1 and recognized_text.isdigit() and recognized_text in still_missing:
                                # 计算数字在屏幕上的中心位置
                                coords_array = np.array(coordinates)
                                center_x = int(np.mean(coords_array[:, 0])) + expanded_keyboard_region[0]
                                center_y = int(np.mean(coords_array[:, 1])) + expanded_keyboard_region[1]
                                
                                # 验证坐标是否在合理的键盘区域内
                                if (keyboard_x - 30 <= center_x <= keyboard_x + keyboard_width + 30 and
                                    keyboard_y - 30 <= center_y <= keyboard_y + keyboard_height + 30):
                                    
                                    number_positions[recognized_text] = {
                                        'position': (center_x, center_y),
                                        'confidence': confidence
                                    }
                                    print(f"[click_numbers_on_keyboard] 在扩展区域识别到数字 {recognized_text} 位于 ({center_x}, {center_y})")
            
            # 点击指定的数字
            clicked_numbers = []
            failed_numbers = []
            
            for number in number_list:
                if number in number_positions:
                    # 获取数字位置并点击
                    pos = number_positions[number]['position']
                    center_x, center_y = pos
                    
                    # 物理移动鼠标并点击
                    current_x, current_y = pyautogui.position()
                    distance = ((center_x - current_x)**2 + (center_y - current_y)**2)**0.5
                    move_duration = min(0.1, max(0.05, distance / 1000))
                    
                    pyautogui.moveTo(center_x, center_y, duration=move_duration, tween=pyautogui.easeInOutQuad)
                    time.sleep(0.5)
                    pyautogui.click()
                    time.sleep(0.1)  # 点击间隔
                    
                    clicked_numbers.append(number)
                    print(f"[click_numbers_on_keyboard] 已点击数字 {number} 位于 ({center_x}, {center_y})")
                else:
                    failed_numbers.append(number)
                    print(f"[click_numbers_on_keyboard] 未找到数字 {number} 的位置")
            
            return {
                'success': len(failed_numbers) == 0,
                'clicked_numbers': clicked_numbers,
                'failed_numbers': failed_numbers,
                'keyboard_region': keyboard_region
            }
        else:
            print(f"[click_numbers_on_keyboard] 键盘模板匹配度不足阈值({threshold:.2f})")
            return {
                'success': False,
                'clicked_numbers': [],
                'failed_numbers': number_list,
                'keyboard_region': None
            }
            
    except Exception as e:
        print(f"[click_numbers_on_keyboard] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'clicked_numbers': [],
            'failed_numbers': number_list if 'number_list' in locals() else [],
            'keyboard_region': None
        }



    
def infer_missing_number_positions(known_positions, keyboard_region, missing_numbers):
    """
    基于已知数字的位置推断缺失数字的位置
    
    Args:
        known_positions (dict): 已知数字的位置信息
        keyboard_region (tuple): 键盘区域坐标 (x, y, width, height)
        missing_numbers (list): 缺失的数字列表
        
    Returns:
        dict: 推断的数字位置
    """
    inferred = {}
    
    # 如果已知的数字足够多，可以推断出键盘的布局
    if len(known_positions) >= 4:  # 至少有4个已知数字才能可靠推断
        # 提取所有已知数字的坐标
        positions = {}
        for num, info in known_positions.items():
            positions[num] = info['position']
        
        # 分析行和列的规律
        rows = {}
        cols = {}
        
        for num, (x, y) in positions.items():
            # 将数字按y坐标分组（行）
            row_key = round(y / 20)  # 使用20像素作为行的分组阈值
            if row_key not in rows:
                rows[row_key] = []
            rows[row_key].append((num, x, y))
            
            # 将数字按x坐标分组（列）
            col_key = round(x / 20)  # 使用20像素作为列的分组阈值
            if col_key not in cols:
                cols[col_key] = []
            cols[col_key].append((num, x, y))
        
        # 对每行按x坐标排序
        for row_key in rows:
            rows[row_key].sort(key=lambda item: item[1])
        
        # 对每列按y坐标排序
        for col_key in cols:
            cols[col_key].sort(key=lambda item: item[2])
        
        print(f"[infer_missing_number_positions] 检测到 {len(rows)} 行, {len(cols)} 列")
        
        # 根据实际键盘布局推断缺失数字
        # 键盘布局:
        # 1    2    3
        # 4    5    6    0
        # 7    8    9    确定
        
        # 计算行和列的平均间距
        row_spacing = 0
        col_spacing = 0
        
        # 计算行间距
        if len(rows) > 1:
            row_keys = sorted(rows.keys())
            row_spacings = []
            for i in range(1, len(row_keys)):
                row1_y = rows[row_keys[i-1]][0][2]  # 上一行第一个元素的y坐标
                row2_y = rows[row_keys[i]][0][2]    # 当前行第一个元素的y坐标
                row_spacings.append(row2_y - row1_y)
            if row_spacings:
                row_spacing = sum(row_spacings) / len(row_spacings)
        
        # 计算列间距
        if len(cols) > 1:
            col_keys = sorted(cols.keys())
            col_spacings = []
            for i in range(1, len(col_keys)):
                col1_x = cols[col_keys[i-1]][0][1]  # 上一列第一个元素的x坐标
                col2_x = cols[col_keys[i]][0][1]    # 当前列第一个元素的x坐标
                col_spacings.append(col2_x - col1_x)
            if col_spacings:
                col_spacing = sum(col_spacings) / len(col_spacings)
        
        print(f"[infer_missing_number_positions] 计算出的行间距: {row_spacing}, 列间距: {col_spacing}")
        
        # 尝试推断缺失的数字
        for missing_num in missing_numbers:
            # 基于实际键盘布局推断
            if missing_num == '1':
                # 数字1在第一行第一列
                if '2' in positions and '3' in positions:
                    # 使用第二列和第三列的位置推断第一列
                    x_2, y_2 = positions['2']
                    x_3, y_3 = positions['3']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_2 - col_spacing
                    else:
                        inferred_x = x_2 - (x_3 - x_2)
                    
                    # 使用第二行的y坐标作为第一行的y坐标
                    inferred_y = y_2
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
            
            elif missing_num == '4':
                # 数字4在第二行第一列
                if '5' in positions and '6' in positions and '7' in positions:
                    # 使用第二行第二列和第三列的位置推断第一列
                    x_5, y_5 = positions['5']
                    x_6, y_6 = positions['6']
                    x_7, y_7 = positions['7']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_5 - col_spacing
                    else:
                        inferred_x = x_5 - (x_6 - x_5)
                    
                    # 使用第二行的y坐标
                    inferred_y = y_5
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
            
            elif missing_num == '0':
                # 数字0在第二行第四列
                if '6' in positions and '确定' in known_positions:
                    # 使用第二行第三列和第三行第四列的位置推断
                    x_6, y_6 = positions['6']
                    x_confirm, y_confirm = known_positions['确定']['position']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_6 + col_spacing
                    else:
                        inferred_x = x_6 + (x_6 - positions.get('5', (x_6 - 50, 0))[0])
                    
                    # 使用第二行的y坐标
                    inferred_y = y_6
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
    
    return inferred
