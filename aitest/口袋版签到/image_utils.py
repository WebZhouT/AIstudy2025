# image_utils.py 这个是用来图片匹配在界面中的位置，并且点击的。窗口事件点击
import pyautogui
import time
import os
import pyautogui
import win32gui
import win32api
import win32con
import win32con
import numpy as np
import cv2
from PIL import ImageGrab
# 获取窗口句柄位置和信息
from getWindows import find_window_by_title, get_window_position, window_title

def click_at_window_coord(hwnd, x, y, click_duration=0.05, with_mouse_move=True):
    """在窗口坐标处点击，不移动鼠标"""
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
        # 备用方案：使用原始方法
        try:
            point = (x, y)
            client_point = win32gui.ScreenToClient(hwnd, point)
            
            # 发送点击消息到窗口
            lParam = (client_point[1] << 16) | (client_point[0] & 0xFFFF)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            return True
        except Exception as e2:
            print(f"备用点击也失败: {e2}")
            return False

def multiscale_find_template(screenshot, template_path, confidence, grayscale=True):
    """
    多尺度模板匹配函数
    :param screenshot: 屏幕截图
    :param template_path: 模板图片路径
    :param confidence: 置信度阈值
    :param grayscale: 是否使用灰度匹配
    :return: 匹配位置信息或None
    """
    try:
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"无法读取模板图片: {template_path}")
            return None
            
        # 转换为灰度图（如果需要）
        if grayscale:
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            img = screenshot_gray
            tmp = template_gray
        else:
            img = screenshot
            tmp = template
        
        # 定义缩放比例范围
        scales = [0.9,1.0,1.1]
        best_match = None
        best_confidence = 0
        
        for scale in scales:
            # 调整模板大小
            width = int(tmp.shape[1] * scale)
            height = int(tmp.shape[0] * scale)
            
            # 确保调整后的尺寸有效
            if width <= 0 or height <= 0 or width > img.shape[1] or height > img.shape[0]:
                continue
                
            resized_template = cv2.resize(tmp, (width, height))
            
            # 执行模板匹配
            result = cv2.matchTemplate(img, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 更新最佳匹配
            if max_val > best_confidence and max_val >= confidence:
                best_confidence = max_val
                best_match = {
                    'confidence': max_val,
                    'location': max_loc,
                    'size': (width, height),
                    'scale': scale
                }
        
        return best_match
        
    except Exception as e:
        print(f"多尺度模板匹配出错: {e}")
        return None

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
        # 使用二分查找法确定实际最高相似度
        low = 0.01
        high = 0.99
        max_confidence = 0
        
        # 先检查最低相似度是否存在匹配
        try:
            if region:
                pyautogui.locateOnScreen(image_path, confidence=low, region=region, grayscale=grayscale)
            else:
                pyautogui.locateOnScreen(image_path, confidence=low, grayscale=grayscale)
        except pyautogui.ImageNotFoundException:
            # 连最低相似度都没有匹配，说明完全找不到
            return None
            
        # 使用二分查找确定最大相似度
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

def find_and_click_template(region, template_paths, confidence=0.7, max_attempts=3,grayscale=False):
    """
    在指定区域查找并点击模板，支持单个图片路径或图片路径列表
    
    参数:
        region: 查找区域 (left, top, width, height)
        template_paths: 单个图片路径或图片路径列表
        confidence: 匹配阈值
        max_attempts: 最大尝试次数
        timeout: 超时时间（秒）- 新增参数，用于兼容旧代码
        grayscale: 是否使用灰度匹配
    """
    
    # 如果传入的是单个路径，转换为列表
    if isinstance(template_paths, str):
        template_paths = [template_paths]
    
    print(f"[find_and_click_template] 查找模板: {template_paths}, 阈值: {confidence}, 区域: {region}")
    
    for template_path in template_paths:
        print(f"[find_and_click_template] 尝试模板: {template_path}")
        
        for attempt in range(max_attempts):
            try:
                # 首先获取实际最高匹配度用于调试
                actual_confidence = get_actual_max_similarity(template_path, region, grayscale=grayscale)
                if actual_confidence is not None:
                    print(f"[find_and_click_template] 模板 {template_path} 实际最高匹配度: {actual_confidence:.3f} (阈值: {confidence})")
                else:
                    print(f"[find_and_click_template] 模板 {template_path} 在区域内完全未找到匹配")
                
                # 使用现有的 find_and_click_image 函数
                result = find_and_click_image(
                    image_path=template_path,
                    confidence=confidence,
                    region=region,
                    click=True,
                    grayscale=grayscale,
                    use_multiscale=True
                )
                
                if result:
                    print(f"[find_and_click_template] 成功找到并点击: {template_path}")
                    return True
                elif attempt < max_attempts - 1:
                    print(f"[find_and_click_template] 第{attempt + 1}次尝试失败，等待重试...")
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"[find_and_click_template] 发生错误: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(0.5)
        
        print(f"[find_and_click_template] 模板 {template_path} 所有尝试失败")
    
    print(f"[find_and_click_template] 所有模板尝试失败: {template_paths}")
    return False

# 新增：save_debug_screenshot 函数
def save_debug_screenshot(screenshot, filename_prefix, region=None):
    """保存调试截图"""
    try:
        # 创建screenshots目录如果不存在
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        timestamp = int(time.time())
        if region:
            filename = f"screenshots/{filename_prefix}_region_{region[0]}_{region[1]}_{region[2]}_{region[3]}_{timestamp}.png"
        else:
            filename = f"screenshots/{filename_prefix}_{timestamp}.png"
        
        if isinstance(screenshot, np.ndarray):
            # 如果是numpy数组，使用OpenCV保存
            cv2.imwrite(filename, screenshot)
        else:
            # 如果是PIL图像，直接保存
            screenshot.save(filename)
        
        print(f"[debug] 保存调试截图: {filename}")
        return filename
    except Exception as e:
        print(f"[debug] 保存截图失败: {str(e)}")
        return None

def find_and_click_image(image_path, confidence=0.8, region=None, click=True, fixed_coords=None, grayscale=True, use_multiscale=True):
    """
    通用的图片匹配和点击函数
    支持多尺度模板匹配以适应不同窗口大小
    """
    # 如果提供了固定坐标，直接点击
    if fixed_coords:
        x, y = fixed_coords
        if click:
            # 使用窗口消息方式点击，不移动鼠标
            hwnd = find_window_by_title(window_title)
            if hwnd:
                click_at_window_coord(hwnd, x, y)
                print(f"使用固定坐标点击: {fixed_coords}")
            time.sleep(0.5)
        return {"x": x, "y": y}
    
    try:
        # 获取截图区域
        if region:
            screenshot_region = region
        else:
            # 获取窗口区域
            hwnd = find_window_by_title(window_title)
            if hwnd:
                x, y, width, height = get_window_position(hwnd)
                screenshot_region = (x, y, width, height)
            else:
                screenshot_region = None
        
        # 截取屏幕区域
        if screenshot_region:
            screenshot = pyautogui.screenshot(region=screenshot_region)
        else:
            screenshot = pyautogui.screenshot()
        
        # 转换为OpenCV格式
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 使用多尺度匹配或普通匹配
        if use_multiscale:
            match_result = multiscale_find_template(screenshot_cv, image_path, confidence, grayscale)
            
            if match_result:
                # 计算中心点坐标
                x = screenshot_region[0] + match_result['location'][0] + match_result['size'][0] // 2
                y = screenshot_region[1] + match_result['location'][1] + match_result['size'][1] // 2
                
                if click:
                    # 使用窗口消息方式点击
                    hwnd = find_window_by_title(window_title)
                    if hwnd:
                        click_at_window_coord(hwnd, x, y)
                        mode_text = "黑白模式" if grayscale else "彩色模式"
                        scale_text = f"缩放比例: {match_result['scale']:.2f}"
                        print(f"成功点击图片: {image_path}, 相似度: {match_result['confidence']:.3f}, 位置: ({x}, {y}), 模式: {mode_text}, {scale_text}")
                    time.sleep(0.5)
                
                # 返回匹配信息
                return {
                    'x': x, 
                    'y': y,
                    'left': screenshot_region[0] + match_result['location'][0],
                    'top': screenshot_region[1] + match_result['location'][1],
                    'width': match_result['size'][0],
                    'height': match_result['size'][1],
                    'confidence': match_result['confidence'],
                    'scale': match_result['scale']
                }
            else:
                mode_text = "黑白模式" if grayscale else "彩色模式"
                print(f"图片 {image_path} 在多尺度匹配下未找到, 模式: {mode_text}")
                return None
        else:
            # 原有的pyautogui匹配方式（作为备选）
            if screenshot_region:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=screenshot_region, grayscale=grayscale)
            else:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=grayscale)
            
            if location:
                if click:
                    # 使用窗口消息方式点击，不移动鼠标
                    hwnd = find_window_by_title(window_title)
                    if hwnd:
                        click_x = location.left + location.width//2
                        click_y = location.top + location.height//2
                        click_at_window_coord(hwnd, click_x, click_y)
                        time.sleep(0.5)
                        mode_text = "黑白模式" if grayscale else "彩色模式"
                        print(f"成功点击图片: {image_path}, 相似度: {confidence}, 位置: {location}, 模式: {mode_text}")
                else:
                    mode_text = "黑白模式" if grayscale else "彩色模式"
                    print(f"找到图片但未点击: {image_path}, 相似度: {confidence}, 位置: {location}, 模式: {mode_text}")
                return location
            else:
                mode_text = "黑白模式" if grayscale else "彩色模式"
                print(f"图片 {image_path} 未达到匹配阈值 {confidence}，模式: {mode_text}")
                return None
            
    except Exception as e:
        print(f"查找图片 {image_path} 时发生异常: {e}")
        return None

# 新增: 多尺度查找图片位置函数
def find_image_position_multiscale(image_path, confidence=0.8, region=None, grayscale=True):
    """
    使用多尺度匹配查找图片在屏幕上的位置
    """
    return find_and_click_image(
        image_path, 
        confidence=confidence, 
        region=region, 
        click=False, 
        grayscale=grayscale,
        use_multiscale=True
    )

# 查找指定图片所在位置
def find_image_position(image_path, confidence=0.8, region=None, grayscale=True):
    """
    查找图片在屏幕上的位置，但不点击
    
    参数:
        image_path: 图片路径
        confidence: 匹配置信度阈值 (默认0.8)
        region: 搜索区域 (left, top, width, height)，为None时搜索全屏
        grayscale: 是否将图片转换为灰度
    
    返回:
        dict: 图片位置信息，包含 'x', 'y', 'width', 'height', 'confidence'
        None: 未找到图片
    """
    try:
        # 如果没有指定region，则在游戏窗口范围内查找
        if region:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale)
        else:
            # 当region为None时，在游戏窗口范围内查找
            hwnd = find_window_by_title(window_title)
            if hwnd:
                x, y, width, height = get_window_position(hwnd)
                window_region = (x, y, width, height)
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=window_region, grayscale=grayscale)
            else:
                # 如果找不到窗口，则在整个屏幕范围内查找
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=grayscale)
        
        if location:
            # 计算中心点坐标
            center_x = location.left + location.width // 2
            center_y = location.top + location.height // 2
            
            # 获取实际相似度
            actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale)
            
            position_info = {
                'x': center_x,
                'y': center_y,
                'left': location.left,
                'top': location.top,
                'width': location.width,
                'height': location.height,
                'confidence': actual_confidence if actual_confidence else confidence
            }
            
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"找到图片: {image_path}, 位置: ({center_x}, {center_y}), 相似度: {position_info['confidence']:.2f}, 模式: {mode_text}")
            return position_info
        else:
            # 获取实际相似度并输出
            actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale)
            if actual_confidence is not None:
                mode_text = "黑白模式" if grayscale else "彩色模式"
                print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
            else:
                mode_text = "黑白模式" if grayscale else "彩色模式"
                print(f"图片 {image_path} 在区域内完全未找到匹配, 模式: {mode_text}")
            return None
            
    except pyautogui.ImageNotFoundException:
        # 获取实际相似度并输出
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale)
        if actual_confidence is not None:
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"图片 {image_path} 未达到匹配阈值 {confidence}，实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        else:
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"图片 {image_path} 在区域内完全未找到匹配, 模式: {mode_text}")
        return None
    except Exception as e:
        print(f"查找图片 {image_path} 位置时发生异常: {e}")
        # 获取实际相似度并输出
        actual_confidence = get_actual_max_similarity(image_path, region, grayscale=grayscale)
        if actual_confidence is not None:
            mode_text = "黑白模式" if grayscale else "彩色模式"
            print(f"图片 {image_path} 实际最高相似度: {actual_confidence:.2f}, 模式: {mode_text}")
        return None