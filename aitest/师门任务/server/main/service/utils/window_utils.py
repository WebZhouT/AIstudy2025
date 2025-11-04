"""
窗口操作和模板匹配工具类
提供窗口查找、位置获取、点击操作和模板匹配等公共方法
"""

import win32gui
import win32con
import win32api
import pyautogui
import cv2
import numpy as np
import time
from rapidocr_onnxruntime import RapidOCR
color_templates = ["public/shimen/task/sj.png"]  # 需要彩色匹配的图片列表
# 获取窗口等信息
from .config import window_title
def find_window_by_title(title):
    """
    根据窗口标题查找窗口句柄
    
    Args:
        title (str): 窗口标题
        
    Returns:
        int: 窗口句柄，如果未找到返回None
    """
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None


def get_window_position(hwnd):
    """
    获取窗口位置和大小
    
    Args:
        hwnd (int): 窗口句柄
        
    Returns:
        tuple: (x, y, width, height) 窗口位置和大小
    """
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height


def click_top_center(hwnd):
    """
    点击窗口上方中间位置
    
    Args:
        hwnd (int): 窗口句柄
    """
    x, y, width, height = get_window_position(hwnd)
    click_x = x + width // 2
    click_y = y + 20
    pyautogui.moveTo(click_x, click_y, duration=0.1)
    pyautogui.click(click_x, click_y)
    print(f"[click_top_center] 点击窗口顶部中心: ({click_x}, {click_y})")
    time.sleep(0.1)
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

def match_and_click_template(screenshot, template_path, threshold, region=None, do_click=True):
    """
    匹配模板并执行点击操作
    
    Args:
        screenshot (numpy.ndarray): 屏幕截图
        template_path (str): 模板图片路径
        threshold (float): 匹配阈值
        region (tuple, optional): 区域参数 (x,y,width,height)
        do_click (bool): 是否执行点击操作，默认为True
        
    Returns:
        tuple: (是否匹配成功, 点击坐标)
    """
    try:
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[match_and_click_template] 警告: 无法读取模板图片 {template_path}")
            return False, None
            
        # 确保截图和模板图片类型一致
        # 检查截图和模板的通道数
        if len(screenshot.shape) != len(template.shape):
            if len(screenshot.shape) == 2 and len(template.shape) == 3:
                # 截图为灰度图，模板为彩色图，转换模板为灰度图
                template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            elif len(screenshot.shape) == 3 and len(template.shape) == 2:
                # 截图为彩色图，模板为灰度图，转换截图为灰度图
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        elif len(screenshot.shape) == 3 and len(template.shape) == 3:
            # 都是彩色图，确保通道顺序一致
            if screenshot.shape[2] != template.shape[2]:
                if screenshot.shape[2] == 3:
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
                else:
                    template = cv2.cvtColor(template, cv2.COLOR_RGB2BGR)
        
        # 确保数据类型正确
        if screenshot.dtype != template.dtype:
            template = template.astype(screenshot.dtype)
            
        # 彩色匹配
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[match_and_click_template] 当前匹配度: {max_val:.2f} (阈值: {threshold})")
        
        if max_val >= threshold:
            h, w = template.shape[:2] if len(template.shape) == 3 else template.shape
            x, y = max_loc
            
            if region:
                # 区域参数为(x,y,width,height)
                region_x, region_y, region_w, region_h = region
                
                # 计算模板中心点相对于全屏的坐标
                center_x = region_x + x + w // 2
                center_y = region_y + y + h // 2
                
                # 验证坐标是否在区域内
                if not (region_x <= center_x <= region_x + region_w and 
                        region_y <= center_y <= region_y + region_h):
                    print(f"[match_and_click_template] 警告: 计算坐标({center_x},{center_y})超出区域{region}")
            else:
                # 如果没有提供区域，则直接使用匹配位置
                center_x = x + w // 2
                center_y = y + h // 2
            
            print(f"[match_and_click_template] 匹配成功，坐标: ({center_x}, {center_y})")
            
            if do_click:
                print(f"[match_and_click_template] 执行点击操作")
                # 实际执行鼠标移动和点击操作 - 物理移动方式
                current_x, current_y = pyautogui.position()
                distance = ((center_x - current_x)**2 + (center_y - current_y)**2)**0.5
                
                # 根据距离动态调整移动时间
                move_duration = min(0.1, max(0.05, distance / 1000))
                
                # 物理移动鼠标
                pyautogui.moveTo(center_x, center_y, duration=move_duration, tween=pyautogui.easeInOutQuad)
                time.sleep(0.05)
                
                # 物理点击
                pyautogui.click()
                time.sleep(0.02)
                
                print(f"[match_and_click_template] 已物理点击坐标: ({center_x}, {center_y})")
                time.sleep(0.05)
            else:
                print(f"[match_and_click_template] 不执行点击操作，仅返回坐标")
            
            return True, (center_x, center_y)
        else:
            print(f"[match_and_click_template] 匹配度不足阈值({threshold:.2f})")
            return False, None
            
    except Exception as e:
        print(f"[match_and_click_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def find_and_click_template(template_path, threshold, do_click=True, region=None):
    """
    在指定区域查找并点击模板，支持多尺度匹配
    
    Args:
        template_path (str): 模板图片路径
        threshold (float): 匹配阈值
        do_click (bool): 是否执行点击操作，默认为True
        region (tuple, optional): 指定区域 (x,y,width,height)，如果为None则使用窗口区域
        
    Returns:
        bool: 如果do_click为True，返回是否匹配并点击成功；如果do_click为False，返回是否匹配成功
    """
    try:
        # 如果未提供region，则使用窗口区域
        if region is None:
            hwnd = find_window_by_title(window_title)
            x, y, width, height = get_window_position(hwnd)
            region = (x, y, width, height)
        
        # 获取当前屏幕截图
        screenshot = pyautogui.screenshot(region=region)
        
        # 根据模板类型决定截图处理方式
        if template_path in color_templates:
            # 彩色模板，截图转换为BGR格式
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            print(f"[find_and_click_template] 使用彩色匹配查找: {template_path}")
        else:
            # 灰度模板，截图转换为灰度
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            print(f"[find_and_click_template] 使用灰度匹配查找: {template_path}")
        
        # 读取模板图片
        if template_path in color_templates:
            template = cv2.imread(template_path)
        else:
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            
        if template is None:
            print(f"[find_and_click_template] 无法读取模板图片: {template_path}")
            return False
        
        # 定义缩放比例范围
        scales = [0.8, 0.9, 1.0, 1.1, 1.2]
        best_match = None
        best_confidence = 0
        
        # 多尺度模板匹配
        for scale in scales:
            try:
                # 调整模板大小
                width = int(template.shape[1] * scale)
                height = int(template.shape[0] * scale)
                
                # 确保调整后的尺寸有效
                if width <= 0 or height <= 0 or width > screenshot_cv.shape[1] or height > screenshot_cv.shape[0]:
                    continue
                    
                resized_template = cv2.resize(template, (width, height))
                
                # 执行模板匹配
                result = cv2.matchTemplate(screenshot_cv, resized_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # 更新最佳匹配
                if max_val > best_confidence:
                    best_confidence = max_val
                    best_match = {
                        'confidence': max_val,
                        'location': max_loc,
                        'size': (width, height),
                        'scale': scale
                    }
                    
                print(f"[find_and_click_template] 缩放比例 {scale}: 最大相似度 {max_val:.3f}")
                
            except Exception as e:
                print(f"[find_and_click_template] 缩放比例 {scale} 匹配失败: {str(e)}")
                continue
        
        # 检查是否找到匹配
        if best_match and best_confidence >= threshold:
            print(f"[find_and_click_template] 找到最佳匹配: 相似度 {best_confidence:.3f}, 缩放比例 {best_match['scale']}")
            
            if do_click:
                # 计算点击位置
                loc_x, loc_y = best_match['location']
                width, height = best_match['size']
                
                center_x = region[0] + loc_x + width // 2
                center_y = region[1] + loc_y + height // 2
                
                # 点击匹配位置
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    click_at_window_coord(hwnd, center_x, center_y)
                    print(f"[find_and_click_template] 点击位置: ({center_x}, {center_y})")
                    return True
                else:
                    print("[find_and_click_template] 未找到窗口句柄，无法点击")
                    return False
            else:
                return True
        else:
            print(f"[find_and_click_template] 未找到匹配 (最高相似度: {best_confidence:.3f}, 阈值: {threshold})")
            return False
            
    except Exception as e:
        print(f"[find_and_click_template] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def ocr_text_in_region_with_rapidocr(region, ocr_engine=None):
    """
    使用RapidOCR对指定屏幕区域进行文字识别
    
    Args:
        region (tuple): 屏幕区域坐标 (x, y, width, height)
        ocr_engine (RapidOCR, optional): OCR引擎实例，如果未提供则创建新的实例
        
    Returns:
        dict: 包含识别结果的字典
              {
                  'success': bool, 是否成功识别
                  'text': str, 识别的文字内容（合并后的文本）
                  'texts': list, 识别的文字列表（每个识别项的详细信息）
                  'region': tuple, 识别区域坐标
              }
    """
    try:
        # 如果没有提供OCR引擎实例，则创建一个新的
        if ocr_engine is None:
            ocr_engine = RapidOCR()
        
        # 截取指定区域的屏幕截图
        screenshot = pyautogui.screenshot(region=region)
        screenshot_np = np.array(screenshot)
        
        # 使用RapidOCR进行文字识别
        ocr_result, _ = ocr_engine(screenshot_np)
        
        # 处理识别结果
        if ocr_result:
            # 提取所有识别到的文字及详细信息
            texts = []
            for item in ocr_result:
                if len(item) >= 3:  # 确保数据完整性
                    # item格式: [坐标点, 识别文字, 置信度]
                    text_info = {
                        'text': item[1],
                        'confidence': float(item[2]),
                        'coordinates': item[0].tolist() if hasattr(item[0], 'tolist') else item[0]
                    }
                    texts.append(text_info)
            
            # 合并所有文字为一个字符串
            full_text = "".join([item[1] for item in ocr_result if len(item) >= 2])
            
            print(f"[ocr_text_in_region_with_rapidocr] OCR识别成功，识别到文字: {full_text}")
            
            return {
                'success': True,
                'text': full_text,
                'texts': texts,
                'region': region
            }
        else:
            print("[ocr_text_in_region_with_rapidocr] 未识别到任何文字")
            return {
                'success': False,
                'text': '',
                'texts': [],
                'region': region
            }
            
    except Exception as e:
        print(f"[ocr_text_in_region_with_rapidocr] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'text': '',
            'texts': [],
            'region': region if 'region' in locals() else None
        }


def ocr_text_in_template_area(hwnd, template_path, threshold=0.8, ocr_engine=None):
    """
    在窗口中匹配模板，然后对匹配到的区域进行OCR文字识别
    支持多尺度模板匹配
    
    Args:
        hwnd (int): 窗口句柄
        template_path (str): 模板图片路径
        threshold (float): 模板匹配阈值，默认0.8
        ocr_engine (RapidOCR, optional): OCR引擎实例，如果未提供则创建新的实例
        
    Returns:
        dict: 包含识别结果和匹配信息的字典
              {
                  'success': bool, 是否成功识别
                  'matched': bool, 是否匹配到模板
                  'text': str, 识别的文字内容
                  'texts': list, 识别的文字列表（详细信息）
                  'region': tuple, 识别区域坐标(x, y, width, height)
                  'confidence': float, 模板匹配置信度
                  'scale': float, 匹配使用的缩放比例
              }
    """
    try:
        # 如果没有提供OCR引擎实例，则创建一个新的
        if ocr_engine is None:
            ocr_engine = RapidOCR()
        
        # 获取窗口位置
        window_x, window_y, window_width, window_height = get_window_position(hwnd)
        window_region = (window_x, window_y, window_width, window_height)
        
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[ocr_text_in_template_area] 警告: 无法读取模板图片 {template_path}")
            return {
                'success': False,
                'matched': False,
                'text': '',
                'texts': [],
                'region': None,
                'confidence': 0.0,
                'scale': 1.0
            }
        
        # 截取整个窗口区域的屏幕截图
        window_screenshot = pyautogui.screenshot(region=window_region)
        screenshot_cv = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
        
        # 定义缩放比例范围
        scales = [0.8, 0.9, 1.0, 1.1, 1.2]
        best_match = None
        best_confidence = 0
        
        # 多尺度模板匹配
        for scale in scales:
            try:
                # 调整模板大小
                width = int(template.shape[1] * scale)
                height = int(template.shape[0] * scale)
                
                # 确保调整后的尺寸有效
                if width <= 0 or height <= 0 or width > screenshot_cv.shape[1] or height > screenshot_cv.shape[0]:
                    print(f"[ocr_text_in_template_area] 缩放比例 {scale} 无效，跳过")
                    continue
                    
                resized_template = cv2.resize(template, (width, height))
                
                # 执行模板匹配
                res = cv2.matchTemplate(screenshot_cv, resized_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                
                print(f"[ocr_text_in_template_area] 缩放比例 {scale}: 模板匹配度: {max_val:.3f}")
                
                # 更新最佳匹配
                if max_val > best_confidence:
                    best_confidence = max_val
                    best_match = {
                        'confidence': max_val,
                        'location': max_loc,
                        'size': (width, height),
                        'scale': scale
                    }
                    
            except Exception as e:
                print(f"[ocr_text_in_template_area] 缩放比例 {scale} 匹配失败: {str(e)}")
                continue
        
        # 检查是否找到匹配
        if best_match and best_confidence >= threshold:
            print(f"[ocr_text_in_template_area] 找到最佳匹配: 相似度 {best_confidence:.3f}, 缩放比例 {best_match['scale']}")
            
            # 获取模板尺寸
            loc_x, loc_y = best_match['location']
            width, height = best_match['size']
            
            # 计算匹配区域在屏幕上的绝对坐标
            # max_loc是匹配到的位置，为相对坐标，需要加上窗口的屏幕坐标
            region_x = window_x + loc_x
            region_y = window_y + loc_y
            region_width = width
            region_height = height
            
            # 定义匹配区域 (x, y, width, height)
            match_region = (region_x, region_y, region_width, region_height)
            
            # 对匹配区域进行OCR识别
            ocr_result = ocr_text_in_region_with_rapidocr(match_region, ocr_engine)
            
            return {
                'success': ocr_result['success'],
                'matched': True,
                'text': ocr_result['text'],
                'texts': ocr_result['texts'],
                'region': match_region,
                'confidence': best_confidence,
                'scale': best_match['scale']
            }
        else:
            print(f"[ocr_text_in_template_area] 模板匹配度不足阈值({threshold:.2f})，最高相似度: {best_confidence:.3f}")
            return {
                'success': False,
                'matched': False,
                'text': '',
                'texts': [],
                'region': None,
                'confidence': best_confidence,
                'scale': 1.0
            }
            
    except Exception as e:
        print(f"[ocr_text_in_template_area] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'matched': False,
            'text': '',
            'texts': [],
            'region': None,
            'confidence': 0.0,
            'scale': 1.0
        }
    

def find_template_in_window(hwnd, template_path, threshold=0.8):
    """
    在指定窗口中查找模板图片的位置
    
    Args:
        hwnd (int): 窗口句柄
        template_path (str): 模板图片路径
        threshold (float): 匹配阈值，默认0.8
        
    Returns:
        dict: 包含匹配结果的字典
              {
                  'found': bool, 是否找到匹配
                  'position': tuple, 匹配位置坐标 (x, y, width, height)
                  'center': tuple, 匹配区域中心坐标 (center_x, center_y)
                  'confidence': float, 匹配置信度
                  'region': tuple, 窗口区域坐标 (window_x, window_y, window_width, window_height)
              }
    """
    try:
        import cv2
        import numpy as np
        from ..utils.window_utils import get_window_position
        
        # 获取窗口位置和大小
        window_x, window_y, window_width, window_height = get_window_position(hwnd)
        window_region = (window_x, window_y, window_width, window_height)
        
        # 截取整个窗口区域的屏幕截图
        window_screenshot = pyautogui.screenshot(region=window_region)
        screenshot_cv = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
        
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[find_template_in_window] 警告: 无法读取模板图片 {template_path}")
            return {
                'found': False,
                'position': None,
                'center': None,
                'confidence': 0.0,
                'region': window_region
            }
        
        # 进行模板匹配
        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[find_template_in_window] 模板匹配度: {max_val:.2f} (阈值: {threshold})")
        
        if max_val >= threshold:
            # 获取模板尺寸
            h, w = template.shape[:2]
            
            # 计算匹配区域在屏幕上的绝对坐标
            match_x, match_y = max_loc
            region_x = window_x + match_x
            region_y = window_y + match_y
            region_width = w
            region_height = h
            
            # 计算中心点坐标
            center_x = region_x + w // 2
            center_y = region_y + h // 2
            
            # 定义匹配区域
            match_region = (
                region_x,
                region_y,
                region_width,
                region_height
            )
            
            print(f"[find_template_in_window] 找到模板，位置: {match_region}, 中心点: ({center_x}, {center_y})")
            
            return {
                'found': True,
                'position': match_region,
                'center': (center_x, center_y),
                'confidence': max_val,
                'region': window_region
            }
        else:
            print(f"[find_template_in_window] 模板匹配度不足阈值({threshold:.2f})")
            return {
                'found': False,
                'position': None,
                'center': None,
                'confidence': max_val,
                'region': window_region
            }
            
    except Exception as e:
        print(f"[find_template_in_window] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'found': False,
            'position': None,
            'center': None,
            'confidence': 0.0,
            'region': window_region if 'window_region' in locals() else None
        }