# 图像识别
from rapidocr_onnxruntime import RapidOCR
import ctypes  # 用于系统弹窗
from win10toast import ToastNotifier
# 初始化通知器 (放在全局变量处)
toaster = ToastNotifier()
import keyboard
import threading
import pyautogui
import time
import win32gui
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
# 新增: 导入全局变量hwnd用于获取窗口位置
import win32gui
window_title = "Phone-OBN7WS7D99EYFI49" 
# 新增: 创建screenshots文件夹用于保存调试图片
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")
def recognize_numbers_in_region(region):
    """
    识别指定区域内的数字
    返回: 数字位置字典 {数字: (x, y, width, height)}
    """
    try:
        # 截取区域图片
        screenshot = pyautogui.screenshot(region=region)
        
        # 保存截图用于调试
        timestamp = int(time.time())
        screenshot.save(f"./screenshots/keyboard_region_{timestamp}.png")
        
        # 转换为OpenCV格式
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 图像预处理 - 增强对比度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 多种预处理方法尝试
        # 方法1: 二值化
        _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 方法2: 自适应阈值
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)
        
        numbers_positions = {}
        
        # 尝试两种预处理方法
        for i, thresh in enumerate([thresh1, thresh2]):
            try:
                # 使用pytesseract识别数字和位置
                data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT,
                                               config='--psm 8 -c tessedit_char_whitelist=0123456789')
                
                for idx in range(len(data['text'])):
                    text = data['text'][idx].strip()
                    confidence = int(data['conf'][idx])
                    
                    # 只处理置信度较高的单个数字
                    if text.isdigit() and len(text) == 1 and confidence > 60:
                        x = data['left'][idx] + region[0]
                        y = data['top'][idx] + region[1]
                        width = data['width'][idx]
                        height = data['height'][idx]
                        
                        # 计算中心点坐标
                        center_x = x + width // 2
                        center_y = y + height // 2
                        
                        # 如果同一个数字有多个识别结果，取置信度最高的
                        if text not in numbers_positions or confidence > numbers_positions[text][3]:
                            numbers_positions[text] = (center_x, center_y, width, height, confidence)
                            print(f"方法{i+1}识别到数字 {text} 位置: ({center_x}, {center_y}), 置信度: {confidence}")
                
            except Exception as e:
                print(f"OCR识别方法{i+1}失败: {e}")
        
        # 清理数据，只保留坐标信息
        clean_positions = {}
        for digit, (x, y, w, h, conf) in numbers_positions.items():
            clean_positions[digit] = (x, y, w, h)
        
        print(f"最终识别到的数字: {list(clean_positions.keys())}")
        return clean_positions
        
    except Exception as e:
        print(f"数字识别失败: {e}")
        return {}
    

def find_keyboard_region(hwnd):
    """
    在指定句柄窗口区域内查找键盘区域（黑白比对）
    参数:
    hwnd: 窗口句柄
    返回: 键盘区域坐标 (left, top, width, height)
    """
    # 确保screenshots目录存在
    screenshots_dir = "./screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    
    try:
        # 获取句柄窗口的位置和大小
        window_rect = win32gui.GetWindowRect(hwnd)
        print(f"句柄窗口坐标: {window_rect}")
        
        # 计算窗口区域 (left, top, width, height)
        window_left = window_rect[0]
        window_top = window_rect[1]
        window_width = window_rect[2] - window_rect[0]
        window_height = window_rect[3] - window_rect[1]
        
        window_region = (window_left, window_top, window_width, window_height)
        print(f"句柄窗口区域: {window_region}")
        
        # 截取句柄窗口区域并转换为黑白
        window_screenshot = pyautogui.screenshot(region=window_region)
        # 转换为灰度（黑白）
        window_screenshot_grayscale = window_screenshot.convert('L')
        
        # 保存黑白窗口截图用于调试
        window_debug_path = os.path.join(screenshots_dir, "window_grayscale_debug.png")
        window_screenshot_grayscale.save(window_debug_path)
        print(f"黑白窗口截屏已保存到: {window_debug_path}")
        
        # 加载键盘图片并转换为黑白
        keyboard_image = Image.open('./keyboard.png')
        keyboard_image_grayscale = keyboard_image.convert('L')
        
        # 保存黑白键盘图片用于调试
        keyboard_debug_path = os.path.join(screenshots_dir, "keyboard_grayscale_debug.png")
        keyboard_image_grayscale.save(keyboard_debug_path)
        print(f"黑白键盘图片已保存到: {keyboard_debug_path}")
        
        # 在黑白图像上进行比对
        keyboard_location = pyautogui.locate(
            keyboard_image_grayscale, 
            window_screenshot_grayscale, 
            confidence=0.7
        )
            
        if keyboard_location:
            print(f"找到键盘区域: {keyboard_location}")
            
            # 将相对坐标转换为绝对坐标，并确保是int类型
            absolute_left = int(window_left + keyboard_location.left)
            absolute_top = int(window_top + keyboard_location.top)
            keyboard_width = int(keyboard_location.width)
            keyboard_height = int(keyboard_location.height)
            
            print(f"转换后的键盘区域: ({absolute_left}, {absolute_top}, {keyboard_width}, {keyboard_height})")
            
            # 截取键盘区域并转换为黑白用于OCR识别
            keyboard_screenshot = pyautogui.screenshot(region=(
                absolute_left,
                absolute_top,
                keyboard_width,
                keyboard_height
            ))
            keyboard_screenshot_grayscale = keyboard_screenshot.convert('L')
            
            # 保存黑白键盘区域用于OCR
            temp_ocr_path = os.path.join(screenshots_dir, "temp_keyboard_ocr.png")
            keyboard_screenshot_grayscale.save(temp_ocr_path)
            print(f"OCR识别用黑白图片已保存到: {temp_ocr_path}")
            
            # 在键盘区域内进行OCR识别
            ocr_region = (absolute_left, absolute_top, keyboard_location.width, keyboard_location.height)
            recognized_text = ocr_image_recognition(region=ocr_region)
            
            if recognized_text:
                print(f"OCR识别到文字: {recognized_text}")
                # 根据识别到的文字进行点击操作
                # 这里需要根据你的具体需求实现点击逻辑
                # 例如：click_based_on_text(recognized_text)
            else:
                print("OCR识别失败，使用黑白图片匹配进行点击")
                # 使用黑白图片匹配进行点击
                center_x = absolute_left + keyboard_location.width // 2
                center_y = absolute_top + keyboard_location.height // 2
                pyautogui.click(center_x, center_y)
                print(f"已点击键盘区域中心: ({center_x}, {center_y})")
            
            # 返回键盘区域的绝对坐标
            return (
                absolute_left,
                absolute_top,
                keyboard_location.width,
                keyboard_location.height
            )
        else:
            print("在句柄窗口区域内未找到键盘区域")
            
            # 保存黑白窗口截图用于调试
            debug_image_path = os.path.join(screenshots_dir, "keyboard_not_found_debug.png")
            window_screenshot_grayscale.save(debug_image_path)
            print(f"未找到键盘区域，黑白窗口截屏已保存到: {debug_image_path}")
            
            return None
            
    except Exception as e:
        print(f"查找键盘区域失败: {e}")
        
        # 出错时也保存黑白截屏
        try:
            window_rect = win32gui.GetWindowRect(hwnd)
            window_left = int(window_rect[0])
            window_top = int(window_rect[1])
            window_width = int(window_rect[2] - window_rect[0])
            window_height = int(window_rect[3] - window_rect[1])
            
            window_region = (window_left, window_top, window_width, window_height)
            error_screenshot = pyautogui.screenshot(region=window_region)
            error_screenshot_grayscale = error_screenshot.convert('L')
            debug_image_path = os.path.join(screenshots_dir, "keyboard_error_debug.png")
            error_screenshot_grayscale.save(debug_image_path)
            print(f"查找键盘区域出错，黑白句柄窗口截屏已保存到: {debug_image_path}")
        except Exception as screenshot_error:
            print(f"保存调试截屏失败: {screenshot_error}")
            
        return None
def input_coordinate_with_ocr(coordinate_value, coordinate_type="X"):
    """
    使用OCR识别方式输入坐标数字
    """
    try:
        coordinate_str = str(coordinate_value)
        print(f"正在输入{coordinate_type}坐标: {coordinate_str}")
        
        # 1. 首先查找键盘区域
        hwnd = find_window_by_title(window_title)
        keyboard_region = find_keyboard_region(hwnd)
        if not keyboard_region:
            print(f"错误: 未找到键盘区域，无法输入{coordinate_type}坐标")
            # 备用方案：使用原有的图片匹配方式
            return input_coordinate_old_method(coordinate_str, coordinate_type)
        
        # 2. 识别键盘区域内的数字位置
        numbers_positions = recognize_numbers_in_region(keyboard_region)
        if not numbers_positions:
            print(f"错误: 未能在键盘区域识别到数字，无法输入{coordinate_type}坐标")
            return input_coordinate_old_method(coordinate_str, coordinate_type)
        
        print(f"识别到的数字: {list(numbers_positions.keys())}")
        
        # 3. 逐个输入坐标数字
        for digit in coordinate_str:
            if digit in numbers_positions:
                x, y, width, height = numbers_positions[digit]
                # 点击数字
                pyautogui.click(x, y)
                print(f"点击数字 {digit} 位置: ({x}, {y})")
                time.sleep(0.3)
            else:
                print(f"警告: 键盘中未找到数字 {digit}，尝试备用方法")
                # 备用方案：使用图片匹配点击该数字
                if not click_digit_by_image(digit):
                    print(f"错误: 无法输入数字 {digit}")
                    return False
        
        # 4. 点击确认按钮
        sure_result = find_and_click_image('./keyboard/sure.png', confidence=0.8)
        if sure_result:
            print(f"{coordinate_type}坐标输入完成")
            time.sleep(0.5)
            return True
        else:
            print(f"错误: 未找到确认按钮，{coordinate_type}坐标输入失败")
            return False
            
    except Exception as e:
        print(f"输入{coordinate_type}坐标时发生异常: {e}")
        # 异常时使用备用方法
        return input_coordinate_old_method(coordinate_str, coordinate_type)
# 备用方法：原有的图片匹配方式
def input_coordinate_old_method(coordinate_str, coordinate_type):
    """原有的图片匹配方式作为备用"""
    print(f"使用备用方法输入{coordinate_type}坐标: {coordinate_str}")
    
    for digit in coordinate_str:
        digit_found = False
        for key_info in area:
            if key_info['name'] == digit:
                result = find_and_click_image(key_info['png'], confidence=0.95)
                if result:
                    digit_found = True
                    time.sleep(0.3)
                    break
                else:
                    print(f"警告: 未找到数字 {digit} 的图片")
        
        if not digit_found:
            print(f"错误: 无法输入数字 {digit}")
            return False
    
    # 点击确认按钮
    sure_result = find_and_click_image('./keyboard/sure.png', confidence=0.85)
    return bool(sure_result)
def click_digit_by_image(digit):
    """使用图片匹配方式点击单个数字（备用方法）"""
    for key_info in area:
        if key_info['name'] == digit:
            result = find_and_click_image(key_info['png'], confidence=0.95)
            if result:
                return True
    return False
# 全部操作完毕后出现提示信息
def show_alert(message, use_toast=True):
    """显示提醒（可选择Toast或传统弹窗）"""
    if use_toast:
        toaster.show_toast(
            "提醒",
            message,
            duration=5,
            threaded=True
        )
    else:
        ctypes.windll.user32.MessageBoxW(0, message, "提醒", 1)

def find_window_by_title(title):
    """根据窗口标题查找窗口句柄"""
    def callback(hwnd, hwnds):
        try:
            if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
                hwnds.append(hwnd)
            return True
        except Exception as e:
            print(f"窗口回调处理出错: {e}")
            return False
    
    hwnds = []
    try:
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None
    except Exception as e:
        print(f"查找窗口时出错: {e}")
        return None

def get_window_position(hwnd):
    """获取窗口位置和大小"""
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height

# 新增: 点击窗口顶部中间位置以获得焦点
def focus_window(x, y, width, height):
    """点击窗口顶部中间位置以获得焦点"""
    # 计算窗口顶部中间位置
    focus_x = x + width // 2
    focus_y = y + 10  # 窗口顶部偏下10像素，避免点击到边框
    
    # 点击该位置以获得焦点
    pyautogui.click(focus_x, focus_y)
    time.sleep(0.1)  # 短暂延迟确保焦点生效

# 点击藏宝图
def click_treasure_maps(locations, x, y, width, height):
    """根据坐标数组依次点击藏宝图"""
    # 这里可以根据需要扩展点击逻辑
    print(f"找到{len(locations)}个藏宝图位置")
    # 修改: 只点击第一个藏宝图
    if locations and not stop_event.is_set():
        loc = locations[0]  # 只取第一个藏宝图位置
        center_x = loc.left + loc.width // 2
        center_y = loc.top + loc.height // 2
        print(f"点击藏宝图位置: ({center_x}, {center_y})")
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)


# 新增: 通用图片匹配和点击函数
def find_and_click_image(image_path, confidence=0.8, region=None, click=True, fixed_coords=None,grayscale=True):
    """
    通用的图片匹配和点击函数
    
    参数:
    image_path: 图片路径
    confidence: 匹配相似度
    region: 匹配区域 (left, top, width, height)
    click: 是否点击匹配位置
    fixed_coords: 固定坐标 (x, y)，如果提供则直接点击该坐标
    grayscale: 是否将图片转换为灰度
    返回:
    匹配位置或None
    """
  # 如果提供了固定坐标，直接点击
    if fixed_coords:
        x, y = fixed_coords
        if click:
            pyautogui.click(x, y)
            time.sleep(0.5)
            print(f"使用固定坐标点击: {fixed_coords}")
        return {"x": x, "y": y}
    
    try:
        # 修改: 如果没有指定region，则在游戏窗口范围内查找
        if region:
            # 使用黑白模式进行匹配
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale)
            
            # 保存截图到本地（黑白模式）
            timestamp = int(time.time())
            screenshot = pyautogui.screenshot(region=region)
            
            # 如果启用黑白模式，将截图转换为黑白
            if grayscale:
                screenshot = screenshot.convert('L')  # 转换为灰度图
            
            # 修改: 将截图保存到screenshots文件夹下
            # screenshot.save(f"./screenshots/screenshot_find_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
        else:
            # 修改: 当region为None时，在游戏窗口范围内查找而不是整个屏幕
            # 获取当前游戏窗口位置和大小
            # hwnd = find_window_by_title("Phone-E6EDU20429087631")
            hwnd = find_window_by_title("Phone-OBN7WS7D99EYFI49")
            if hwnd:
                x, y, width, height = get_window_position(hwnd)
                window_region = (x, y, width, height)
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=window_region, grayscale=grayscale)
                
                # 保存截图到本地（黑白模式）
                timestamp = int(time.time())
                screenshot = pyautogui.screenshot(region=window_region)
                
                # 如果启用黑白模式，将截图转换为黑白
                if grayscale:
                    screenshot = screenshot.convert('L')  # 转换为灰度图
                
                # 修改: 将截图保存到screenshots文件夹下
                # screenshot.save(f"./screenshots/screenshot_find_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
            else:
                # 如果找不到窗口，则在整个屏幕范围内查找
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=grayscale)
        
        if location:
            if click:
                pyautogui.click(location.left + location.width//2, location.top + location.height//2)
                time.sleep(0.5)  # 添加点击后的延迟
                mode_text = "黑白模式" if grayscale else "彩色模式"
                print(f"成功点击图片: {image_path}, 相似度: {confidence}, 位置: {location}, 模式: {mode_text}")
            else:
                mode_text = "黑白模式" if grayscale else "彩色模式"
                print(f"找到图片但未点击: {image_path}, 相似度: {confidence}, 位置: {location}, 模式: {mode_text}")
            return location
        else:
            # 新增：获取实际相似度并输出
            actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale)
            if actual_confidence is not None:
                mode_text = "黑白模式" if grayscale else "彩色模式"
                print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
            else:
                mode_text = "黑白模式" if grayscale else "彩色模式"
                print(f"图片 {image_path} 在区域内完全未找到匹配, 模式: {mode_text}")
            return None
            
    except pyautogui.ImageNotFoundException:
        # 保存截图到本地（黑白模式）
        # hwnd = find_window_by_title("Phone-E6EDU20429087631")
        hwnd = find_window_by_title("Phone-OBN7WS7D99EYFI49")
        if region:
            timestamp = int(time.time())
            screenshot = pyautogui.screenshot(region=region)
            
            # 如果启用黑白模式，将截图转换为黑白
            if grayscale:
                screenshot = screenshot.convert('L')  # 转换为灰度图
            
            # 修改: 将截图保存到screenshots文件夹下
            # screenshot.save(f"screenshots/screenshot_find_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
        elif hwnd:
            # 如果没有指定region但找到了窗口，则截图窗口区域
            x, y, width, height = get_window_position(hwnd)
            window_region = (x, y, width, height)
            timestamp = int(time.time())
            screenshot = pyautogui.screenshot(region=window_region)
            
            # 如果启用黑白模式，将截图转换为黑白
            if grayscale:
                screenshot = screenshot.convert('L')  # 转换为灰度图
            
            # 修改: 将截图保存到screenshots文件夹下
            screenshot.save(f"screenshots/screenshot_find_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
        
        # 新增：获取实际相似度并输出
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale)
        if actual_confidence is not None:
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        else:
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"图片 {image_path} 在区域内完全未找到匹配, 模式: {mode_text}")
        return None
    except Exception as e:
        print(f"查找图片 {image_path} 时发生异常: {e}")
        # 新增：获取实际相似度并输出
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale)
        if actual_confidence is not None:
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"图片 {image_path} 实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        return None

# 新增: 查找所有匹配图片的位置
def find_all_images(image_path, confidence=0.95, region=None,grayscale=True):
    """
    查找所有匹配的图片位置
    
    参数:
    image_path: 图片路径
    confidence: 匹配相似度
    region: 匹配区域 (left, top, width, height)
    grayscale: 是否启用黑白模式
    返回:
    匹配位置列表
    """
    try:
        if region:
            locations = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale))
            # 保存截图到本地
            timestamp = int(time.time())
            screenshot = pyautogui.screenshot(region=region)
            
            # 如果启用黑白模式，将截图转换为黑白
            if grayscale:
                screenshot = screenshot.convert('L')  # 转换为灰度图
            
            # 修改: 将截图保存到screenshots文件夹下
            screenshot.save(f"screenshots/screenshot_find_all_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
        else:
            return []  # 只在指定区域内查找
        return locations
    except pyautogui.ImageNotFoundException:
        # 保存截图到本地
        if region:
            timestamp = int(time.time())
            screenshot = pyautogui.screenshot(region=region)
            
            # 如果启用黑白模式，将截图转换为黑白
            if grayscale:
                screenshot = screenshot.convert('L')  # 转换为灰度图
            
            # 修改: 将截图保存到screenshots文件夹下
            screenshot.save(f"screenshots/screenshot_find_all_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
        
        # 修改: 输出实际相似度信息
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale)
        if actual_confidence is not None:
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        else:
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"图片 {image_path} 在区域内未找到任何匹配, 模式: {mode_text}")
        return []  # 返回空列表而不是抛出异常

# 新增: 获取实际最大相似度的函数
def get_actual_max_similarity(image_path, region=None, grayscale=True):
    """
    获取图片在指定区域内的实际最大相似度
    
    参数:
    image_path: 图片路径
    region: 匹配区域 (left, top, width, height)
    grayscale: 是否启用黑白模式
    
    返回:
    实际最大相似度值或None
    """
    try:
        # 保存截图到本地
        if region:
            timestamp = int(time.time())
            screenshot = pyautogui.screenshot(region=region)
            
            # 如果启用黑白模式，将截图转换为黑白
            if grayscale:
                screenshot = screenshot.convert('L')  # 转换为灰度图
            
            # 修改: 将截图保存到screenshots文件夹下
            screenshot.save(f"screenshots/screenshot_similarity_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
        
        # 使用二分查找法确定实际最高相似度
        low = 0.01
        high = 0.99
        max_confidence = 0
        
        # 先检查最低相似度是否存在匹配
        try:
            pyautogui.locateOnScreen(image_path, confidence=low, region=region, grayscale=grayscale)
        except pyautogui.ImageNotFoundException:
            # 连最低相似度都没有匹配，说明完全找不到
            return None
            
        # 使用二分查找确定最大相似度
        while high - low > 0.01:
            mid = (low + high) / 2
            try:
                pyautogui.locateOnScreen(image_path, confidence=mid, region=region, grayscale=grayscale)
                low = mid
                max_confidence = mid
            except pyautogui.ImageNotFoundException:
                high = mid
                
        return max_confidence
    except Exception as e:
        print(f"获取图片 {image_path} 实际相似度时出错: {e}")
        return None

# 全局变量控制运行状态
running = False
stop_event = threading.Event()
# 新增: 存储提取的坐标
extracted_coordinate = None
# 新增: 藏宝图是否找到的标志
treasure_found = False
# 藏宝图
img_content = "treasure_map.png"
# 藏宝图结果
map_result = "map_result.png"
# 右侧道具/行囊区域
img_right = "img_right.png"
# 道具栏按钮
prop = "prop.png"
# 键盘虚拟按键
area = [
    {
      'name':"0",
      'png':"./keyboard/0.png"
    },
    {
      'name':"1",
      'png':"./keyboard/1.png"
    },    
    
    {
      'name':"2",
      'png':"./keyboard/2.png"
    },{
      'name':"3",
      'png':"./keyboard/3.png"
    },
    {
      'name':"4",
      'png':"./keyboard/4.png"
    },
    {
      'name':"5",
      'png':"./keyboard/5.png"
    },
    {
      'name':"6",
      'png':"./keyboard/6.png"
    },
    {
      'name':"7",
      'png':"./keyboard/7.png"
    },
    {
      'name':"8",
      'png':"./keyboard/8.png"
    },
    {
      'name':"9",
      'png':"./keyboard/9.png"
    }
]
# 新增: OCR识别函数
def ocr_image_recognition(region=None):
    """
    对指定区域进行OCR文字识别
    
    参数:
    region: 识别区域 (left, top, width, height)
    
    返回:
    识别到的文字内容
    """
    try:
        # 初始化OCR
        ocr = RapidOCR()
        
        # 截取指定区域或全屏
        if region:
            screenshot = pyautogui.screenshot(region=region)
            # 转换为黑白
            screenshot_grayscale = screenshot.convert('L')
            # 保存截图到本地
            timestamp = int(time.time())
            # 修改: 将截图保存到screenshots文件夹下
            # screenshot_grayscale.save(f"screenshots/screenshot_ocr_{timestamp}.png")
        else:
            return []
            
        # 保存临时截图用于OCR识别
        # 修改: 将临时截图保存到screenshots文件夹下
        temp_image = "screenshots/temp_ocr_image.png"
        screenshot.save(temp_image)
        
        # 进行OCR识别
        result, _ = ocr(temp_image)
        
        # 提取识别到的文字
        if result:
            recognized_text = '\n'.join([item[1] for item in result])
            print(f"OCR识别结果:\n{recognized_text}")
                
            # 新增: 提取坐标信息
            import re
            # 使用正则表达式匹配坐标格式 (x.y) 或 (x,y) 或 建邮城（243，127）
            coordinate_pattern = r'(?:[\w\W]*?[（(](\d+)[,，](\d+)[)）])'
            matches = re.findall(coordinate_pattern, recognized_text)
            
            if matches:
                # 取最后一组匹配结果作为坐标
                x, y = matches[-1]
                coordinate = [int(x), int(y)]
                print(f"提取到的坐标: {coordinate}")
                return coordinate
            else:
                # 尝试其他坐标格式
                coordinate_pattern = r'[($$]*\(?(\d+)[.,](\d+)\)?[$$]*'
                matches = re.findall(coordinate_pattern, recognized_text)
                if matches:
                    # 取最后一组匹配结果作为坐标
                    x, y = matches[-1]
                    coordinate = [int(x), int(y)]
                    print(f"提取到的坐标: {coordinate}")
                    return coordinate
                else:
                    print("未找到坐标信息")
                    return []
        else:
            print("未识别到任何文字")
            return []
    except Exception as e:
        print(f"OCR识别出错: {e}")
        return []

# 新增: 数字键盘输入函数
def input_coordinates_via_keyboard(coordinate):
    """
    使用OCR识别方式输入坐标数字
    
    参数:
    coordinate: 坐标数组 [x, y]
    """
    global extracted_coordinate
    
    if not coordinate or len(coordinate) != 2:
        print("坐标数据不正确")
        return False
    
    x, y = coordinate
    extracted_coordinate = [x, y]
    
    print(f"正在输入坐标: X={x}, Y={y}")
    
    # 使用OCR方式输入X坐标
    if not input_coordinate_with_ocr(str(x), "X"):
        print("X坐标输入失败")
        return False
    
    time.sleep(1)
    
    # 使用OCR方式输入Y坐标
    if not input_coordinate_with_ocr(str(y), "Y"):
        print("Y坐标输入失败")
        return False
    
    time.sleep(3)
    print("坐标输入完成")
    
    # 点击关闭地图按钮
    find_and_click_image('./close.png', confidence=0.8)
    # 坐标输入完成后，启动自动寻路监听
    listen_for_navigation_coordinates()
    return True

def listen_for_navigation_coordinates():
    """
    坐标输入完成后，每隔3秒进行指定区域的图像识别，
    监听界面中指定区域进行文本识别，识别出来的文字需要包含对应坐标
    """
    global extracted_coordinate  # 新增: 声明全局变量
    print("开始监听导航坐标...")
    ocr = RapidOCR()
    
    # 定义要识别的区域 (需要根据实际界面调整)
    # 这里假设在屏幕左上角区域
    # target_region = (50, 50, 300, 100)  # left, top, width, height
    
    # 修改: 使用areabtn.png图片定位区域
    # area_btn_location = None
    # try:
    #     area_btn_location = pyautogui.locateOnScreen('./areabtn.png', confidence=0.8)
    #     print(f"areabtn.png位置: {area_btn_location}")
    # except pyautogui.ImageNotFoundException:
    #     area_btn_location = None
    #     print("未找到areabtn.png")
    #     # 停止
    #     stop_script()
    
    # if area_btn_location:
    #     # 基于areabtn.png位置定义识别区域，稍微扩大一些范围以包含坐标文本
    #     target_region = (
    #         int(area_btn_location.left),
    #         int(area_btn_location.top),
    #         int(area_btn_location.width),
    #         int(area_btn_location.height)
    #     )
    #     print(f"基于areabtn.png定义的识别区域: {target_region}")
    # else:
    #     print("没找到监听区域")
    #     return False  # 修改为返回False，表示未找到监听区域
    target_region = (
        int(1000),
        int(70),
        int(120),
        int(30)
    )
    print(f"基于areabtn.png定义的识别区域: {target_region}")  
    # 保存上一次识别的结果
    previous_result = None
    same_count = 0  # 连续相同结果计数器
    
    for i in range(20):  # 最多监听20次，约1分钟
        if not running:
            break
            
        try:
            # 截取指定区域
            screenshot = pyautogui.screenshot(region=target_region)
            # 修改: 将临时截图保存到screenshots文件夹下
            temp_image = "screenshots/temp_navigation_ocr.png"
            screenshot.save(temp_image)
            
            # OCR识别
            result, _ = ocr(temp_image)
            
            if result:
                recognized_text = '\n'.join([item[1] for item in result])
                print(f"第{i+1}次监听结果: {recognized_text}")
                
                # 检查本次识别结果与上次是否相同
                if previous_result is not None and previous_result == recognized_text:
                    same_count += 1
                    print(f"识别结果连续 {same_count} 次相同")
                    # 如果连续3次识别结果相同，则认为已到达目标
                    if same_count >= 2:
                        print("识别结果连续2次未变化，判定已到达目标位置")
                        return True
                else:
                    # 重置计数器
                    same_count = 0
                
                # 更新上一次的结果
                previous_result = recognized_text
                
                # 检查是否包含坐标信息
                import re
                # 修改: 更新坐标匹配模式，支持更多格式包括独立的数字行
                expected_coordinate_pattern = r'(?:[\w\W]*?[（(](\d+)[,，](\d+)[)）])|(\d+)\s+(\d+)|(?:[$$$(]*(\d+)[.,](\d+)[$$)]*)'
                matches = re.findall(expected_coordinate_pattern, recognized_text)
                
                if matches:
                    print(f"检测到坐标信息: {matches}")
                    # 修改: 检查是否与提取的坐标匹配
                    if extracted_coordinate:
                        # 检查检测到的坐标是否与提取的坐标匹配
                        target_x, target_y = extracted_coordinate
                        found_target = False
                        for match in matches:
                            # 处理不同的匹配组
                            if match[0] and match[1]:  # (x,y) 格式
                                x, y = int(match[0]), int(match[1])
                            elif match[2] and match[3]:  # x y 格式 (独立数字行)
                                x, y = int(match[2]), int(match[3])
                            elif match[4] and match[5]:  # x.y 或 x,y 格式
                                x, y = int(match[4]), int(match[5])
                            else:
                                continue
                                
                            if x == target_x and y == target_y:
                                print(f"已到达目标坐标: {target_x},{target_y}")
                                found_target = True
                                break
                        
                        if found_target:
                            return True  # 修改为返回True，表示已到达目标
                    else:
                        # 这里可以添加到达目的地的处理逻辑
                        # 比如跳出循环或调用其他函数
                        return True  # 修改为返回True
                else:
                    # 新增: 尝试处理分行显示的坐标情况
                    lines = recognized_text.split('\n')
                    if len(lines) >= 2:
                        try:
                            # 尝试将最后两行解析为坐标
                            x_line = lines[-2].strip()
                            y_line = lines[-1].strip()
                            
                            # 只有当两行都是数字时才认为是坐标
                            if x_line.isdigit() and y_line.isdigit():
                                x, y = int(x_line), int(y_line)
                                print(f"检测到分行坐标信息: x={x}, y={y}")
                                
                                # 检查是否与提取的坐标匹配
                                if extracted_coordinate:
                                    target_x, target_y = extracted_coordinate
                                    if x == target_x and y == target_y:
                                        print(f"已到达目标坐标: {target_x},{target_y}")
                                        return True
                                else:
                                    return True
                        except ValueError:
                            pass  # 如果转换失败，继续执行原有逻辑
                    
                    print("未检测到坐标信息")
            else:
                print("未识别到任何文字")
                
        except Exception as e:
            print(f"监听过程中出现错误: {e}")
            
        # 等待3秒后继续
        time.sleep(3)
    
    print("导航监听结束")
    return False  # 监听结束但未找到目标坐标

# 监听指定图片直到消失
def wait_for_image_to_disappear(image_path, confidence=0.4, timeout=60):
    """
    监听指定图片直到消失
    
    参数:
    image_path: 图片路径
    confidence: 匹配相似度
    timeout: 超时时间(秒)
    
    返回:
    True: 图片消失
    False: 超时
    """
    print(f"开始监听图片 {image_path} 直到消失...")
    start_time = time.time()
    
    while not stop_event.is_set():
        if not running:
            return False
            
        # 检查超时
        if time.time() - start_time > timeout:
            print(f"监听图片 {image_path} 超时")
            return False
            
        try:
            # 尝试查找图片
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location is None:
                # 图片不存在，说明已消失
                print(f"图片 {image_path} 已消失")
                return True
            else:
                print(f"图片 {image_path} 仍存在: {location}")
                # 保存截图到本地
                timestamp = int(time.time())
                screenshot = pyautogui.screenshot()
                # 修改: 将截图保存到screenshots文件夹下
                # screenshot.save(f"screenshots/screenshot_monitor_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
        except pyautogui.ImageNotFoundException:
            # 图片不存在，说明已消失
            print(f"图片 {image_path} 已消失")
            return True
        except Exception as e:
            print(f"监听图片时出错: {e}")
            
        # 等待1秒后继续
        time.sleep(1)
    
    return False

# 监听战斗状态并重新开始挖图
def monitor_battle_and_restart():
    """
    监听战斗状态，当war.png消失后重新开始挖图流程
    如果没有战斗状态，直接返回True继续执行
    """
    print("开始监听战斗状态...")
    
    # 首先检查是否出现war.png（战斗状态）
    war_appeared = False
    start_time = time.time()
    battle_check_timeout = 2  # 只检查10秒看是否有战斗状态
    
    # 等待war.png出现（战斗开始）- 只等待10秒
    print("检查是否进入战斗状态...")
    # 点击关闭地图按钮
    find_and_click_image('./close.png', confidence=0.8)
    for i in range(battle_check_timeout):
        if not running or stop_event.is_set():
            return False
            
        try:
            war_location = pyautogui.locateOnScreen('./war.png', confidence=0.3)
            if war_location:
                print("检测到战斗状态开始")
                war_appeared = True
                break
        except pyautogui.ImageNotFoundException:
            pass
            
        # 每2秒检查一次
        time.sleep(2)
        print(f"战斗状态检查中... ({i+1}/{battle_check_timeout//2})")
        
    # 如果没有出现战斗状态，直接返回True继续执行
    if not war_appeared:
        print("未检测到战斗状态，继续执行后续流程")
        # 点击固定位置的tool.png按钮
        pyautogui.click(1743, 427)
        return True
    
    # 如果有战斗状态，等待war.png消失（战斗结束）
    print("检测到战斗状态，等待战斗结束...")
    start_time = time.time()
    battle_timeout = 120  # 战斗最多持续2分钟
    
    while not stop_event.is_set() and running:
        if time.time() - start_time > battle_timeout:
            print("等待战斗结束超时")
            return False
            
        try:
            war_location = pyautogui.locateOnScreen('./war.png', confidence=0.3)
            if war_location is None:
                print("战斗结束，重新开始挖图流程")
                time.sleep(3)  # 等待战斗结束后的界面稳定
                return True
        except pyautogui.ImageNotFoundException:
            print("战斗结束，重新开始挖图流程")
            time.sleep(3)  # 等待战斗结束后的界面稳定
            return True
            
        # 每5秒检查一次战斗状态
        time.sleep(5)
        elapsed_time = int(time.time() - start_time)
        print(f"战斗进行中... 已持续{elapsed_time}秒")
    
    return False


# 主函数包含所有程序逻辑
def main_loop():
    error_count = 0  # 添加错误计数器
    max_errors = 10  # 最大连续错误次数
    # 定义图片内容
    global running, treasure_found, window_title  # 声明所有需要的全局变量
    
    # 新增: 重置所有状态变量
    treasure_processed = False
    loop_count = 0
    max_loop_count = 50  # 最大循环次数
    
    while not stop_event.is_set():
        if running:
            # 根据右侧道具/行囊区域的图片，匹配到窗口内的区域获取到对应的匹配区域
            # 这里假设已经获取到窗口句柄hwnd和位置信息
            try:
                print(f"[主循环] 正在监听窗口: {window_title}, 循环次数: {loop_count + 1}")
                # 查找游戏窗口
                hwnd = find_window_by_title(window_title)
                if not hwnd:
                    print("未找到游戏窗口")
                    error_count += 1
                    if error_count >= max_errors:
                        print("连续未找到游戏窗口次数过多，脚本将停止")
                        show_alert("未找到游戏窗口，脚本已停止")
                        stop_script()
                    time.sleep(1)
                    continue
                else:
                    error_count = 0  # 重置错误计数
                    
                x, y, width, height = get_window_position(hwnd)
                print(f"窗口位置: x={x}, y={y}, width={width}, height={height}")
                
                # 只有第一次循环才点击窗口顶部中间位置以获得焦点
                if loop_count == 0:
                    focus_window(x, y, width, height)
                
                # 新增: 增加循环计数
                loop_count += 1
                if loop_count > max_loop_count:
                    print("达到最大循环次数，脚本将停止")
                    show_alert("脚本已达到最大循环次数，自动停止")
                    stop_script()
                    break
                pyautogui.click(1743, 427)
                # 查找藏宝图，只在未处理过的情况下查找
                if not treasure_found and not treasure_processed:
                    treasure_locations = find_all_images(img_content, confidence=0.8, region=(x, y, width, height))
                    if treasure_locations:
                        # 去重处理：过滤掉坐标相近的重复藏宝图
                        unique_treasure_locations = []
                        for loc in treasure_locations:
                            is_duplicate = False
                            for unique_loc in unique_treasure_locations:
                                # 如果两个藏宝图中心点距离小于50像素，则认为是同一个
                                center_x1 = loc.left + loc.width // 2
                                center_y1 = loc.top + loc.height // 2
                                center_x2 = unique_loc.left + unique_loc.width // 2
                                center_y2 = unique_loc.top + unique_loc.height // 2
                                distance = ((center_x1 - center_x2) ** 2 + (center_y1 - center_y2) ** 2) ** 0.5
                                if distance < 10:
                                    is_duplicate = True
                                    break
                            if not is_duplicate:
                                unique_treasure_locations.append(loc)
                        print(f"找到{len(unique_treasure_locations)}个藏宝图（已去重）")
                        
                        # 保存第一个藏宝图位置用于后续点击
                        first_treasure_loc = unique_treasure_locations[0]
                        pyautogui.click(first_treasure_loc.left + first_treasure_loc.width//2, 
                                      first_treasure_loc.top + first_treasure_loc.height//2)
                        # 点击藏宝图
                        # click_treasure_maps(unique_treasure_locations, x, y, width, height)
                        time.sleep(1)
                        treasure_found = True
                        
                        # 点击藏宝图后进行OCR识别
                        print("正在进行藏宝图结果OCR识别...")
                        # 先匹配藏宝图结果区域，再进行OCR识别
                        try:
                            result_location = pyautogui.locateOnScreen(map_result, confidence=0.4, region=(x, y, width, height))
                            print(f"藏宝图结果区域: {result_location}")
                        except pyautogui.ImageNotFoundException:
                            result_location = None
                            
                        if result_location:
                            # 基于找到的结果区域进行OCR识别
                            recognized_text = ocr_image_recognition(region=(
                                int(result_location.left), 
                                int(result_location.top), 
                                int(result_location.width), 
                                int(result_location.height)
                            ))  
                            print(f"识别结果: {recognized_text}")
                            
                            # 点击关闭按钮关闭当前道具行囊
                            closebtns = find_and_click_image('./close.png', confidence=0.8)
                            time.sleep(1)
                            if closebtns is None:
                                print("警告: 未找到道具关闭按钮")
                                stop_script()
                                stop_event.set()
                                break
                            print("成功点击关闭按钮，继续执行后续操作")
                            time.sleep(1)

                            # 点击界面左上角出现地图内容
                            print("正在点击areabtn.png...")
                            areabtn_center_x = 1030
                            areabtn_center_y = 74
                            pyautogui.click(areabtn_center_x, areabtn_center_y)
                            print("成功点击areabtn.png，继续执行后续操作")
                            time.sleep(1)

                            # 点击x输入框，输入识别结果中的x坐标
                            print("正在点击xbtn.png...")
                            x_btn_result = find_and_click_image('xbtn.png', confidence=0.8)
                            # 大唐境外
                            # x_btn_result = find_and_click_image('xbtn1.png', confidence=0.8)
                            if x_btn_result is None:
                                print("错误: 未找到xbtn.png按钮，脚本停止")
                                stop_script()
                                stop_event.set()
                                break

                            # 新增: 输入坐标
                            if recognized_text:
                                input_coordinates_via_keyboard(recognized_text)
                            
                            # 识别键盘内容
                            if listen_for_navigation_coordinates():
                                time.sleep(1)
                                # result = find_and_click_image('./tool.png', confidence=0.4)
                                # 点击固定位置的tool.png按钮
                              # result = find_and_click_image('./tool.png', confidence=0.8, region=(1803, 20, 33, 38))
                                # 点击固定位置的tool.png按钮
                                pyautogui.click(1743, 427)
                                # if result is None:
                                #     print("警告: 未找到tool.png按钮")
                                #     stop_script()
                                time.sleep(2)
                                treasure_locations = find_all_images(img_content, confidence=0.8, region=(x, y, width, height))
                                # 去重处理：过滤掉坐标相近的重复藏宝图
                                unique_treasure_locations = []
                                for loc in treasure_locations:
                                    is_duplicate = False
                                    for unique_loc in unique_treasure_locations:
                                        # 如果两个藏宝图中心点距离小于50像素，则认为是同一个
                                        center_x1 = loc.left + loc.width // 2
                                        center_y1 = loc.top + loc.height // 2
                                        center_x2 = unique_loc.left + unique_loc.width // 2
                                        center_y2 = unique_loc.top + unique_loc.height // 2
                                        distance = ((center_x1 - center_x2) ** 2 + (center_y1 - center_y2) ** 2) ** 0.5
                                        if distance < 10:
                                            is_duplicate = True
                                            break
                                    if not is_duplicate:
                                        unique_treasure_locations.append(loc)
                                print(f"找到{len(unique_treasure_locations)}个藏宝图（已去重）")
                                
                                # 保存第一个藏宝图位置用于后续点击
                                # first_treasure_loc = unique_treasure_locations[0]
                                
                                # 点击藏宝图
                                click_treasure_maps(unique_treasure_locations, x, y, width, height)
                                # # 点击第一个藏宝图位置
                                # pyautogui.click(first_treasure_loc.left + first_treasure_loc.width//2, 
                                #               first_treasure_loc.top + first_treasure_loc.height//2)
                                print(f"点击第一个藏宝图位置")
                                time.sleep(1)
                                
                                # 点击使用地图
                                find_and_click_image('usermap.png', confidence=0.8)
                                time.sleep(1)

                                # 监听战斗状态并重新开始挖图
                                if monitor_battle_and_restart():
                                    print("战斗结束，准备重新开始挖图流程")
                                    
                                    # 重置状态变量，准备下一次挖图
                                    treasure_found = False
                                    treasure_processed = False
                                    
                                    # 等待一段时间让界面稳定
                                    time.sleep(3)
                                    print("状态已重置，准备下一次挖图")
                                    continue  # 继续循环，重新开始挖图
                                else:
                                    print("战斗监听失败，停止脚本")
                                    stop_script()
                            else:
                                print("导航监听失败，停止脚本")
                                stop_script()
                        else:
                            print("未找到藏宝图结果区域")
                            stop_script()
                    else:
                        print("未找到藏宝图")
                        show_alert("未找到藏宝图，脚本停止")
                        stop_script()
                
                # 检查是否需要停止
                print(f"treasure_found状态: {treasure_found}, treasure_processed状态: {treasure_processed}")
                
                # 如果已经处理过藏宝图但treasure_found仍为True，说明有逻辑错误
                if treasure_processed and treasure_found:
                    print("状态异常，重置状态并继续")
                    treasure_found = False
                    treasure_processed = False
                    continue
                    
            except Exception as e:
                error_count += 1
                print(f"发生错误: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                if error_count >= max_errors:
                    print("连续错误次数过多，脚本将停止")
                    show_alert("程序出现连续错误，脚本已停止")
                    stop_script()
                    break
                time.sleep(1)
                continue
                
        time.sleep(0.1)  # 避免CPU占用过高

def stop_script():
    """停止脚本"""
    global running, treasure_found
    running = False
    treasure_found = False  # 重置藏宝图状态
    stop_event.set()
    print("\n===== 脚本已停止 =====")

def start_script():
    """启动脚本"""
    global running, treasure_found
    running = True
    treasure_found = False  # 启动时重置状态
    stop_event.clear()  # 清除停止事件
    print("\n===== 脚本已启动 =====")
def main():
    # 注册热键
    keyboard.add_hotkey('f1', start_script)
    keyboard.add_hotkey('f2', stop_script)
    
    print("提示: 按 F1 启动脚本，按 F2 停止脚本")
    
    try:
        # 启动主循环
        main_loop()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:  # 添加: 捕获主循环外的异常
        print(f"\n程序发生未处理的异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        stop_event.set()
        keyboard.unhook_all()

if __name__ == "__main__":
    main()
