# image_utils.py 这个是用来图片匹配在界面中的位置，并且点击的。窗口事件点击
import pyautogui
import time
import os
import pyautogui
import win32gui
import win32api
import win32con
import cv2
import numpy as np
from PIL import ImageGrab
from datetime import datetime
# 获取窗口句柄位置和信息
from getWindows import find_window_by_title, get_window_position, window_title
hwnd = find_window_by_title(window_title)

def click_at_window_coord(hwnd, x, y, click_duration=0.05, with_mouse_move=True):
    """在窗口坐标处点击，不移动鼠标"""
    """
    增强版的窗口点击函数
    :param hwnd: 窗口句柄
    :param x: 屏幕x坐标
    :param y: 屏幕y坐标
    :param click_duration: 点击持续时间（秒）
    :param with_mouse_move: 是否包含鼠标移动事件
    """
    try:
        # 激活窗口（可选，某些应用需要）
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.01)
        
        # 坐标转换
        client_x, client_y = win32gui.ScreenToClient(hwnd, (x, y))
        lParam = win32api.MAKELONG(client_x, client_y)
        
        # 发送事件序列
        if with_mouse_move:
            win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
            time.sleep(0.01)
        
        # 使用SendMessage确保消息被处理
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(click_duration)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        
        return True
        
    except Exception as e:
        print(f"高级点击失败: {e}")
        return False

# 新增: 多尺度图片匹配函数
def multiscale_find_image(template_path, region=None, confidence=0.65, scales=[0.9, 1.0, 1.1], method=cv2.TM_CCOEFF_NORMED):
    """
    多尺度图片匹配函数，支持等比例放大缩小匹配
    
    参数:
        template_path: 模板图片路径
        region: 搜索区域 (left, top, width, height)
        confidence: 匹配置信度阈值
        scales: 缩放比例列表
        method: OpenCV模板匹配方法
    
    返回:
        匹配位置信息或None
    """
    try:
        # 读取模板图片
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"无法读取模板图片: {template_path}")
            return None
        
        # 获取屏幕截图
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                x, y, width, height = get_window_position(hwnd)
                region = (x, y, width, height)
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
        
        # 转换为OpenCV格式并转为灰度
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        screenshot_gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        best_match = None
        best_confidence = 0
        
        # 在多尺度下进行匹配
        for scale in scales:
            # 计算缩放后的模板尺寸
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            
            # 确保尺寸有效
            if width <= 0 or height <= 0:
                continue
                
            # 缩放模板
            resized_template = cv2.resize(template, (width, height), interpolation=cv2.INTER_AREA)
            
            # 如果缩放后的模板比截图大，跳过
            if resized_template.shape[0] > screenshot_gray.shape[0] or resized_template.shape[1] > screenshot_gray.shape[1]:
                continue
                
            # 模板匹配
            result = cv2.matchTemplate(screenshot_gray, resized_template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 更新最佳匹配
            if max_val > best_confidence and max_val >= confidence:
                best_confidence = max_val
                best_match = {
                    'left': max_loc[0] + region[0] if region else max_loc[0],
                    'top': max_loc[1] + region[1] if region else max_loc[1],
                    'width': width,
                    'height': height,
                    'confidence': max_val
                }
        
        if best_match:
            print(f"多尺度匹配成功: {template_path}, 最佳比例: {best_confidence:.3f}, 位置: ({best_match['left']}, {best_match['top']})")
            return best_match
        else:
            print(f"多尺度匹配失败: {template_path}, 最高相似度: {best_confidence:.3f}")
            return None
            
    except Exception as e:
        print(f"多尺度图片匹配出错: {e}")
        return None

# 修改: 增强的图片匹配和点击函数，支持多尺度匹配
def find_and_click_image(image_path, confidence=0.655, region=None, click=True, fixed_coords=None, grayscale=True, multiscale=False):
    """
    通用的图片匹配和点击函数，支持多尺度匹配
    
    参数:
    image_path: 图片路径
    confidence: 匹配相似度
    region: 匹配区域 (left, top, width, height)
    click: 是否点击匹配位置
    fixed_coords: 固定坐标 (x, y)，如果提供则直接点击该坐标
    grayscale: 是否将图片转换为灰度
    multiscale: 是否启用多尺度匹配
    
    返回:
    匹配位置或None
    """
    # 如果提供了固定坐标，直接点击
    if fixed_coords:
        x, y = fixed_coords
        if click:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                click_at_window_coord(hwnd, x, y)
                print(f"使用固定坐标点击: {fixed_coords}")
            time.sleep(0.5)
        return {"x": x, "y": y}
    
    try:
        location = None
        
        # 如果启用多尺度匹配
        if multiscale:
            location = multiscale_find_image(image_path, region, confidence)
        else:
            # 使用原来的pyautogui匹配方法
            if region:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale)
            else:
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    x, y, width, height = get_window_position(hwnd)
                    window_region = (x, y, width, height)
                    location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=window_region, grayscale=grayscale)
                else:
                    location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=grayscale)
        
        if location:
            if click:
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    # 处理多尺度匹配返回的字典格式
                    if isinstance(location, dict):
                        click_x = location['left'] + location['width'] // 2
                        click_y = location['top'] + location['height'] // 2
                    else:
                        click_x = location.left + location.width // 2
                        click_y = location.top + location.height // 2
                    
                    click_at_window_coord(hwnd, click_x, click_y)
                    time.sleep(0.5)
                    mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
                    print(f"成功点击图片: {image_path}, 相似度: {confidence}, 位置: ({click_x}, {click_y}), 模式: {mode_text}")
            else:
                mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
                print(f"找到图片但未点击: {image_path}, 相似度: {confidence}, 位置: {location}, 模式: {mode_text}")
            return location
        else:
            # 获取实际相似度
            actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale, multiscale=multiscale)
            if actual_confidence is not None:
                mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
                print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
            else:
                mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
                print(f"图片 {image_path} 在区域内完全未找到匹配, 模式: {mode_text}")
            return None
            
    except pyautogui.ImageNotFoundException:
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale, multiscale=multiscale)
        if actual_confidence is not None:
            mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
            print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        else:
            mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
            print(f"图片 {image_path} 在区域内完全未找到匹配, 模式: {mode_text}")
        return None
    except Exception as e:
        print(f"查找图片 {image_path} 时发生异常: {e}")
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale, multiscale=multiscale)
        if actual_confidence is not None:
            mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
            print(f"图片 {image_path} 实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        return None

# 修改: 增强的获取实际最大相似度函数，支持多尺度匹配
def get_actual_max_similarity(image_path, region=None, grayscale=True, multiscale=False):
    """
    获取图片在指定区域内的实际最大相似度，支持多尺度匹配
    
    参数:
    image_path: 图片路径
    region: 匹配区域 (left, top, width, height)
    grayscale: 是否启用黑白模式
    multiscale: 是否启用多尺度匹配
    
    返回:
    实际最大相似度值或None
    """
    try:
        # 如果启用多尺度匹配，使用多尺度方法获取相似度
        if multiscale:
            match_result = multiscale_find_image(image_path, region, confidence=0.1)  # 使用很低的阈值
            return match_result['confidence'] if match_result else None
        
        # 原来的方法
        low = 0.01
        high = 0.99
        max_confidence = 0
        
        try:
            if region:
                pyautogui.locateOnScreen(image_path, confidence=low, region=region, grayscale=grayscale)
            else:
                pyautogui.locateOnScreen(image_path, confidence=low, grayscale=grayscale)
        except pyautogui.ImageNotFoundException:
            return None
            
        while high - low > 0.01:
            mid = (low + high) / 2
            try:
                if region:
                    pyautogui.locateOnScreen(image_path, confidence=mid, region=region, grayscale=grayscale)
                else:
                    pyautogui.locateOnScreen(image_path, confidence=mid, grayscale=grayscale)
                low = mid
                max_confidence = mid
            except pyautogui.ImageNotFoundException:
                high = mid
                
        return max_confidence
    except Exception as e:
        print(f"获取图片 {image_path} 实际相似度时出错: {e}")
        return None

# 修改: 增强的查找图片位置函数，支持多尺度匹配
def find_image_position(image_path, confidence=0.65, region=None, grayscale=True, multiscale=False):
    """
    查找图片在屏幕上的位置，但不点击，支持多尺度匹配
    
    参数:
        image_path: 图片路径
        confidence: 匹配置信度阈值
        region: 搜索区域 (left, top, width, height)
        grayscale: 是否将图片转换为灰度
        multiscale: 是否启用多尺度匹配
    
    返回:
        dict: 图片位置信息
        None: 未找到图片
    """
    try:
        location = None
        
        if multiscale:
            location = multiscale_find_image(image_path, region, confidence)
        else:
            if region:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale)
            else:
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    x, y, width, height = get_window_position(hwnd)
                    window_region = (x, y, width, height)
                    location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=window_region, grayscale=grayscale)
                else:
                    location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=grayscale)
        
        if location:
            if isinstance(location, dict):
                center_x = location['left'] + location['width'] // 2
                center_y = location['top'] + location['height'] // 2
                position_info = {
                    'x': center_x,
                    'y': center_y,
                    'left': location['left'],
                    'top': location['top'],
                    'width': location['width'],
                    'height': location['height'],
                    'confidence': location['confidence']
                }
            else:
                center_x = location.left + location.width // 2
                center_y = location.top + location.height // 2
                actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale, multiscale=multiscale)
                position_info = {
                    'x': center_x,
                    'y': center_y,
                    'left': location.left,
                    'top': location.top,
                    'width': location.width,
                    'height': location.height,
                    'confidence': actual_confidence if actual_confidence else confidence
                }
            
            mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
            print(f"找到图片: {image_path}, 位置: ({center_x}, {center_y}), 相似度: {position_info['confidence']:.2f}, 模式: {mode_text}")
            return position_info
        else:
            actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale, multiscale=multiscale)
            if actual_confidence is not None:
                mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
                print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
            else:
                mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
                print(f"图片 {image_path} 在区域内完全未找到匹配, 模式: {mode_text}")
            return None
            
    except pyautogui.ImageNotFoundException:
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale, multiscale=multiscale)
        if actual_confidence is not None:
            mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
            print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        else:
            mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
            print(f"图片 {image_path} 在区域内完全未找到匹配, 模式: {mode_text}")
        return None
    except Exception as e:
        print(f"查找图片 {image_path} 位置时发生异常: {e}")
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale, multiscale=multiscale)
        if actual_confidence is not None:
            mode_text = "多尺度模式" if multiscale else ("黑白模式" if grayscale else "彩色模式")
            print(f"图片 {image_path} 实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        return None

def mark_and_save_screenshot(screen_image, animals, screenshots='debugMenu'):
    # 创建截图目录
    if not os.path.exists(screenshots):
        os.makedirs(screenshots)
    """在截图上标记动物并保存"""
    if screen_image is None or not animals:
        return None
        
    marked_image = screen_image.copy()
    
    # 绘制所有检测到的动物框
    for animal in animals:
        top_left = (animal['pt_x'], animal['pt_y'])
        bottom_right = (animal['pt_x'] + animal['template_w'], animal['pt_y'] + animal['template_h'])
        
        # 绘制矩形框
        cv2.rectangle(marked_image, top_left, bottom_right, animal['color'], 2)
        
        # 添加标签（动物名称和相似度）
        label = f"{animal['name']}: {animal['confidence']:.2f}"
        cv2.putText(marked_image, label, 
                    (top_left[0], top_left[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, animal['color'], 2)
    
    # 生成文件名并保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join(screenshots, f"detection_{timestamp}.png")
    cv2.imwrite(filename, marked_image)
    
    return filename