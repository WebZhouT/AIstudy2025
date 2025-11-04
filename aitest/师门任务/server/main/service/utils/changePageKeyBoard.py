# 切换页面键盘识别
from rapidocr_onnxruntime import RapidOCR
from .window_utils import get_window_position
import numpy as np
import cv2
import pyautogui
import time

def infer_missing_number_positions_for_2col(known_positions, keyboard_region, missing_numbers, ocr_result=None):
    """
    基于已知数字的位置推断缺失数字的位置 - 针对2列5行键盘布局
    
    Args:
        known_positions (dict): 已知数字的位置信息
        keyboard_region (tuple): 键盘区域坐标 (x, y, width, height)
        missing_numbers (list): 缺失的数字列表
        ocr_result: OCR识别结果，用于查找特殊数字
        
    Returns:
        dict: 推断的数字位置
    """
    inferred = {}
    keyboard_x, keyboard_y, keyboard_width, keyboard_height = keyboard_region
    
    # 如果已知的数字足够多，可以推断出键盘的布局
    if len(known_positions) >= 3:  # 至少有3个已知数字才能可靠推断
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
        
        print(f"[infer_missing_number_positions_for_2col] 检测到 {len(rows)} 行, {len(cols)} 列")
        
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
        
        print(f"[infer_missing_number_positions_for_2col] 计算出的行间距: {row_spacing}, 列间距: {col_spacing}")
        
        # 从OCR结果中查找特殊数字的位置（如10）
        special_numbers = {}
        if ocr_result:
            for item in ocr_result:
                if len(item) >= 3:
                    recognized_text = item[1]
                    confidence = float(item[2])
                    coordinates = item[0]
                    
                    # 记录特殊数字（两位数）
                    if len(recognized_text) > 1 and recognized_text.isdigit():
                        coords_array = np.array(coordinates)
                        center_x = int(np.mean(coords_array[:, 0])) + keyboard_x
                        center_y = int(np.mean(coords_array[:, 1])) + keyboard_y
                        
                        special_numbers[recognized_text] = {
                            'position': (center_x, center_y),
                            'confidence': confidence
                        }
                        print(f"[infer_missing_number_positions_for_2col] 找到特殊数字 {recognized_text} 位于 ({center_x}, {center_y})")
        
        # 尝试推断缺失的数字
        for missing_num in missing_numbers:
            # 基于2列5行键盘布局推断
            if missing_num == '1':
                # 数字1在第一行第一列
                if '2' in positions:
                    # 使用第二列的位置推断第一列
                    x_2, y_2 = positions['2']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_2 - col_spacing
                    else:
                        inferred_x = x_2 - 60  # 默认间距
                    
                    # 使用第二列的y坐标作为第一行的y坐标
                    inferred_y = y_2
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
            
            elif missing_num == '3':
                # 数字3在第二行第一列
                if '4' in positions:
                    # 使用第二行第二列的位置推断第一列
                    x_4, y_4 = positions['4']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_4 - col_spacing
                    else:
                        inferred_x = x_4 - 60  # 默认间距
                    
                    # 使用第二行的y坐标
                    inferred_y = y_4
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
            
            elif missing_num == '5':
                # 数字5在第三行第一列
                if '6' in positions:
                    # 使用第三行第二列的位置推断第一列
                    x_6, y_6 = positions['6']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_6 - col_spacing
                    else:
                        inferred_x = x_6 - 60  # 默认间距
                    
                    # 使用第三行的y坐标
                    inferred_y = y_6
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
            
            elif missing_num == '7':
                # 数字7在第四行第一列
                if '8' in positions:
                    # 使用第四行第二列的位置推断第一列
                    x_8, y_8 = positions['8']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_8 - col_spacing
                    else:
                        inferred_x = x_8 - 60  # 默认间距
                    
                    # 使用第四行的y坐标
                    inferred_y = y_8
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
            
            elif missing_num == '9':
                # 数字9在第五行第一列
                if '10' in special_numbers:
                    # 使用第五行第二列的位置推断第一列
                    x_10, y_10 = special_numbers['10']['position']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_10 - col_spacing
                    else:
                        inferred_x = x_10 - 60  # 默认间距
                    
                    # 使用第五行的y坐标
                    inferred_y = y_10
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
            
            elif missing_num == '10':
                # 数字10在第五行第二列
                if '9' in positions:
                    # 使用第五行第一列的位置推断第二列
                    x_9, y_9 = positions['9']
                    
                    # 计算列间距
                    if col_spacing > 0:
                        inferred_x = x_9 + col_spacing
                    else:
                        inferred_x = x_9 + 60  # 默认间距
                    
                    # 使用第五行的y坐标
                    inferred_y = y_9
                    
                    inferred[missing_num] = {
                        'position': (int(inferred_x), int(inferred_y)),
                        'confidence': 0.8
                    }
    
    return inferred

""" =================================================== """
def click_numbers_on_keyboardPage(hwnd, template_path, number_to_click, threshold=0.8, ocr_engine=None):
    """
    在窗口中匹配数字键盘模板，识别数字位置并点击指定数字 - 针对2列5行键盘布局
    
    Args:
        hwnd (int): 窗口句柄
        template_path (str): 数字键盘模板图片路径
        number_to_click (str): 需要点击的数字，如 "1" 或 "10"
        threshold (float): 模板匹配阈值，默认0.8
        ocr_engine (RapidOCR, optional): OCR引擎实例，如果未提供则创建新的实例
        
    Returns:
        dict: 操作结果
              {
                  'success': bool, 是否成功完成点击操作
                  'clicked_number': str, 已点击的数字
                  'keyboard_region': tuple, 键盘区域坐标
              }
    """
    try:
        # 如果没有提供OCR引擎实例，则创建一个新的
        if ocr_engine is None:
            ocr_engine = RapidOCR()
        
        # 直接使用传入的数字字符串，不进行拆分
        number_str = str(number_to_click)
        print(f"[click_numbers_on_keyboardPage] 需要点击的数字: {number_str}")
        
        # 获取窗口位置
        window_x, window_y, window_width, window_height = get_window_position(hwnd)
        window_region = (window_x, window_y, window_width, window_height)
        
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[click_numbers_on_keyboardPage] 警告: 无法读取模板图片 {template_path}")
            return {
                'success': False,
                'clicked_number': number_str,
                'keyboard_region': None
            }
        
        # 截取整个窗口区域的屏幕截图
        window_screenshot = pyautogui.screenshot(region=window_region)
        screenshot_cv = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
        
        # 进行模板匹配
        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[click_numbers_on_keyboardPage] 键盘模板匹配度: {max_val:.2f} (阈值: {threshold})")
        
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
            
            print(f"[click_numbers_on_keyboardPage] 找到数字键盘区域: {keyboard_region}")
            
            # 对键盘区域进行OCR识别，获取各数字的位置信息
            keyboard_screenshot = pyautogui.screenshot(region=keyboard_region)
            ocr_result, _ = ocr_engine(np.array(keyboard_screenshot))
            
            # 调试输出OCR识别的所有内容
            print(f"[click_numbers_on_keyboardPage] OCR识别原始结果: {ocr_result}")
            if ocr_result:
                print("[click_numbers_on_keyboardPage] 详细OCR识别结果:")
                for i, item in enumerate(ocr_result):
                    if len(item) >= 3:
                        print(f"  [{i}] 文本: '{item[1]}', 置信度: {item[2]}, 坐标: {item[0]}")
                    else:
                        print(f"  [{i}] 不完整数据: {item}")
            else:
                print("[click_numbers_on_keyboardPage] OCR未识别到任何内容")
            
            # 解析OCR结果，构建数字位置映射表
            number_positions = {}
            
            if ocr_result:
                for item in ocr_result:
                    if len(item) >= 3:
                        recognized_text = item[1]
                        confidence = float(item[2])
                        coordinates = item[0]
                        
                        # 记录所有数字，包括单个数字和多个数字
                        if recognized_text.isdigit():
                            # 计算数字在屏幕上的中心位置
                            coords_array = np.array(coordinates)
                            center_x = int(np.mean(coords_array[:, 0])) + keyboard_x
                            center_y = int(np.mean(coords_array[:, 1])) + keyboard_y
                            
                            number_positions[recognized_text] = {
                                'position': (center_x, center_y),
                                'confidence': confidence
                            }
                            print(f"[click_numbers_on_keyboardPage] 识别到数字 {recognized_text} 位于 ({center_x}, {center_y})")
            
            # 策略1: 如果OCR没有识别到目标数字，尝试基于已知数字的位置推断缺失数字的位置
            if number_str not in number_positions:
                print(f"[click_numbers_on_keyboardPage] OCR未识别到目标数字: {number_str}")
                print("[click_numbers_on_keyboardPage] 尝试基于已知数字推断目标数字位置...")
                
                # 基于2列5行数字键盘布局推断位置
                inferred_positions = infer_missing_number_positions_for_2col(number_positions, keyboard_region, [number_str], ocr_result)
                
                # 将推断的位置添加到number_positions中
                for num, pos_info in inferred_positions.items():
                    if num not in number_positions:
                        number_positions[num] = pos_info
                        print(f"[click_numbers_on_keyboardPage] 推断数字 {num} 位于 {pos_info['position']}")
            
            # 策略2: 如果仍然没有找到目标数字，尝试扩展OCR识别区域
            if number_str not in number_positions:
                print(f"[click_numbers_on_keyboardPage] 仍未找到数字: {number_str}")
                print("[click_numbers_on_keyboardPage] 尝试扩展OCR识别区域...")
                
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
                            
                            # 如果识别到目标数字，则记录其位置
                            if recognized_text == number_str and recognized_text.isdigit():
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
                                    print(f"[click_numbers_on_keyboardPage] 在扩展区域识别到数字 {recognized_text} 位于 ({center_x}, {center_y})")
            
            # 点击指定的数字
            if number_str in number_positions:
                # 获取数字位置并点击
                pos = number_positions[number_str]['position']
                center_x, center_y = pos
                
                # 物理移动鼠标并点击
                current_x, current_y = pyautogui.position()
                distance = ((center_x - current_x)**2 + (center_y - current_y)**2)**0.5
                move_duration = min(0.1, max(0.05, distance / 1000))
                
                pyautogui.moveTo(center_x, center_y, duration=move_duration, tween=pyautogui.easeInOutQuad)
                time.sleep(0.05)
                pyautogui.click()
                time.sleep(0.1)  # 点击间隔
                
                print(f"[click_numbers_on_keyboardPage] 已点击数字 {number_str} 位于 ({center_x}, {center_y})")
                
                return {
                    'success': True,
                    'clicked_number': number_str,
                    'keyboard_region': keyboard_region
                }
            else:
                print(f"[click_numbers_on_keyboardPage] 未找到数字 {number_str} 的位置")
                return {
                    'success': False,
                    'clicked_number': number_str,
                    'keyboard_region': keyboard_region
                }
        else:
            print(f"[click_numbers_on_keyboardPage] 键盘模板匹配度不足阈值({threshold:.2f})")
            return {
                'success': False,
                'clicked_number': number_str,
                'keyboard_region': None
            }
            
    except Exception as e:
        print(f"[click_numbers_on_keyboardPage] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'clicked_number': number_str if 'number_str' in locals() else None,
            'keyboard_region': None
        }