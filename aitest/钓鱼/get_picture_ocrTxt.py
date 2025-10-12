# 匹配指定窗口内的图片信息区域，进行ocr识别返回文字
import pyautogui
import numpy as np
import time
import traceback
import threading
import os
import re
from datetime import datetime
# 图像识别
from rapidocr_onnxruntime import RapidOCR

# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 初始化OCR引擎
ocr = RapidOCR()
stop_event = threading.Event()

# 创建调试截图目录
debug_screenshot_dir = "debug_screenshots"
if not os.path.exists(debug_screenshot_dir):
    os.makedirs(debug_screenshot_dir)

def get_ocr_text_from_template(template_path, confidence=0.8, save_debug_images=True, parse_type=None):
    """
    在指定窗口区域内匹配图片模板，并进行OCR识别返回所有文字信息
    
    Args:
        template_path: 模板图片路径
        confidence: 匹配阈值
        save_debug_images: 是否保存调试图片
        parse_type: 解析类型，'pasture'为牧场状态饲料数量 卫生等，'animal'为动物信息，None为不解析
    Returns:
        list or None: OCR识别到的所有文字信息（原始OCR结果）
                      如果未找到模板或识别失败，返回None
    """
    # 获取窗口句柄和位置
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        print(f"[get_ocr_text_from_template] 未找到窗口: {window_title}")
        return None
    
    x, y, width, height = get_window_position(hwnd)
    window_region = (x, y, width, height)
    
    try:
        # 在窗口区域内匹配模板图片
        template_location = pyautogui.locateOnScreen(template_path, confidence=confidence, region=window_region, grayscale=True)
        if not template_location:
            print(f"[get_ocr_text_from_template] 未找到模板图片: {template_path}")
            return None
        
        # 基于模板位置定义识别区域
        ocr_region = (
            int(template_location.left),
            int(template_location.top),
            int(template_location.width),
            int(template_location.height)
        )
        print(f"[get_ocr_text_from_template] 找到模板，OCR区域: {ocr_region}")
        
        # 截取识别区域进行OCR
        screenshot = pyautogui.screenshot(region=ocr_region)
        screenshot_np = np.array(screenshot)
        
        # 保存调试图片
        if save_debug_images:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            # 保存OCR识别区域截图
            debug_image_path = os.path.join(debug_screenshot_dir, f"ocr_region_{timestamp}.png")
            screenshot.save(debug_image_path)
            print(f"[get_ocr_text_from_template] 已保存OCR区域截图: {debug_image_path}")
            
            # 保存模板图片和匹配区域的对比（可选）
            try:
                import cv2
                # 读取模板图片
                template_img = cv2.imread(template_path)
                if template_img is not None:
                    # 保存模板图片
                    template_debug_path = os.path.join(debug_screenshot_dir, f"template_{timestamp}.png")
                    cv2.imwrite(template_debug_path, template_img)
                    print(f"[get_ocr_text_from_template] 已保存模板图片: {template_debug_path}")
                    
                    # 保存匹配区域的标记图
                    marked_screenshot = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                    # 在匹配区域画矩形框
                    cv2.rectangle(marked_screenshot, (0, 0), 
                                 (ocr_region[2], ocr_region[3]), 
                                 (0, 255, 0), 2)  # 绿色框
                    # 添加文字说明
                    cv2.putText(marked_screenshot, f"Matched: {template_path}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    marked_debug_path = os.path.join(debug_screenshot_dir, f"matched_region_{timestamp}.png")
                    cv2.imwrite(marked_debug_path, marked_screenshot)
                    print(f"[get_ocr_text_from_template] 已保存匹配区域标记图: {marked_debug_path}")
            except ImportError:
                print("[get_ocr_text_from_template] 未安装cv2，跳过模板对比图保存")
        
        # 使用OCR识别文字并返回原始结果
        ocr_result, _ = ocr(screenshot_np)
        
        # 打印OCR结果以便调试
        if ocr_result:
            print(f"[get_ocr_text_from_template] OCR识别结果: {ocr_result}")
            
            # 保存OCR结果标记图（如果有OCR结果）
            if save_debug_images:
                try:
                    import cv2
                    ocr_debug_image = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                    
                    ocr_debug_path = os.path.join(debug_screenshot_dir, f"ocr_result_{timestamp}.png")
                    cv2.imwrite(ocr_debug_path, ocr_debug_image)
                    print(f"[get_ocr_text_from_template] 已保存OCR结果图: {ocr_debug_path}")
                except ImportError:
                    print("[get_ocr_text_from_template] 未安装cv2，跳过OCR结果图保存")
        else:
            print(f"[get_ocr_text_from_template] 未识别到任何文字")
            
        # 根据parse_type进行不同方式的解析
        if parse_type == 'pasture':
            return parse_pasture_status(ocr_result)
        elif parse_type == 'animal':
            return parse_animal_info(ocr_result)
        else:
            # 不解析，返回原始OCR结果
            return ocr_result
        
    except Exception as e:
        print(f"[get_ocr_text_from_template] 处理过程中出错: {str(e)}")
        traceback.print_exc()
        return None
    
def parse_pasture_status(ocr_result):
    """
    解析牧场状态信息，提取饲料数量和清洁度
    
    Args:
        ocr_result: OCR识别结果
        
    Returns:
        dict: 包含饲料数量和清洁度的字典
    """
    # 提取所有文字内容
    texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
    text_str = ', '.join(texts)
    print(f"牧场状态原始文本: {text_str}")
    
    # 初始化结果
    result = {
        'feed_amount': None,  # 饲料数量
        'cleanliness': None,  # 清洁度
        'raw_text': text_str  # 原始文本
    }
    
    # 使用正则表达式提取饲料数量
    # 寻找"饲料"相关的字段及数值
    feed_pattern = r'(?:饲料\D*|牧场饲料\D*)(\d+)'
    feed_match = re.search(feed_pattern, text_str)
    if feed_match:
        result['feed_amount'] = int(feed_match.group(1))
        print(f"解析到饲料数量: {result['feed_amount']}")
    else:
        # 备用方案：寻找3位数字作为饲料数量
        feed_pattern_backup = r'\b\d{3}\b'
        feed_matches = re.findall(feed_pattern_backup, text_str)
        if feed_matches:
            result['feed_amount'] = int(feed_matches[0])
            print(f"解析到饲料数量: {result['feed_amount']}")
    
    # 使用正则表达式提取清洁度
    # 寻找"清洁度"相关的字段及数值
    clean_pattern = r'(?:清洁度\D*|牧场清洁度\D*)(\d+)'
    clean_match = re.search(clean_pattern, text_str)
    if clean_match:
        result['cleanliness'] = int(clean_match.group(1))
        print(f"解析到清洁度: {result['cleanliness']}")
    else:
        # 备用方案：寻找2位数字作为清洁度
        clean_pattern_backup = r'\b\d{2}\b'
        clean_matches = re.findall(clean_pattern_backup, text_str)
        if clean_matches:
            # 取最后一个2位数字作为清洁度（因为可能有多个2位数字）
            result['cleanliness'] = int(clean_matches[-1])
            print(f"解析到清洁度: {result['cleanliness']}")
    
    return result

def parse_animal_info(ocr_result):
    """
    解析动物信息，将信息按动物分组
    
    Args:
        ocr_result: OCR识别结果
        
    Returns:
        list: 动物信息列表，每个动物是一个字典
    """
    animals = []
    current_animal = {}
    
    # 提取所有文字和位置信息
    items = []
    for text_info in ocr_result:
        if text_info and len(text_info) > 1:
            box = text_info[0]  # 文字包围盒
            text = text_info[1]  # 文字内容
            confidence = text_info[2] if len(text_info) > 2 else 0.0
            
            # 计算文字区域的Y坐标（用于分组）
            y_coords = [point[1] for point in box]
            avg_y = sum(y_coords) / len(y_coords)
            
            items.append({
                'text': text,
                'y': avg_y,
                'confidence': confidence
            })
    
    # 按Y坐标分组（同一行的文字Y坐标相近）
    if not items:
        return animals
    
    # 按Y坐标排序并分组
    items.sort(key=lambda x: x['y'])
    
    # 分组阈值（同一行的文字Y坐标相差不超过这个值）
    y_threshold = 20
    
    rows = []
    current_row = [items[0]]
    current_y = items[0]['y']
    
    for item in items[1:]:
        if abs(item['y'] - current_y) <= y_threshold:
            current_row.append(item)
        else:
            rows.append(current_row)
            current_row = [item]
            current_y = item['y']
    
    if current_row:
        rows.append(current_row)
    
    # 按X坐标排序每行的文字
    for row in rows:
        row.sort(key=lambda x: x.get('x', 0) if 'x' in x else 0)
    
    # 解析每行动物信息（假设每行是一个动物的信息）
    for i, row in enumerate(rows):
        row_texts = [item['text'] for item in row]
        print(f"第{i+1}行动物信息: {row_texts}")
        
        animal = {}
        
        # 解析动物信息
        for text in row_texts:
            # 动物名称（通常是非数字的文本）
            if not text.isdigit() and len(text) > 1 and text not in ['成年', '生育期中', '进入生育期', '繁殖', '剩余']:
                if 'name' not in animal:
                    animal['name'] = text
                elif 'status' not in animal:
                    animal['status'] = text
            
            # 饱食度（通常是100或接近100的数字）
            elif text.isdigit() and len(text) == 3 and text.startswith('1'):
                animal['fullness'] = int(text)
            
            # 清洁度或年龄相关的数字（通常是2位数字）
            elif text.isdigit() and len(text) == 2:
                if 'cleanliness' not in animal:
                    animal['cleanliness'] = int(text)
                elif 'age' not in animal:
                    animal['age'] = int(text)
            
            # 其他状态信息
            elif text in ['成年', '生育期中', '进入生育期', '繁殖']:
                animal['reproductive_status'] = text
            
            # 剩余天数
            elif '剩余' in text or '天' in text:
                animal['remaining_days'] = text
        
        if animal:
            animals.append(animal)
    
    print(f"解析到 {len(animals)} 个动物信息:")
    for i, animal in enumerate(animals):
        print(f"  动物{i+1}: {animal}")
    
    return animals
