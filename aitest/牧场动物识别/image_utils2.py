# image_utils.py 这个是用来图片匹配在界面中的位置，并且点击的。操作鼠标点击
import pyautogui
import time
import os
import pyautogui
from PIL import ImageGrab
# 获取窗口句柄位置和信息
from getWindows import find_window_by_title, get_window_position, window_title
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
            screenshot.save(f"./screenshots/screenshot_find_{image_path.split('/')[-1].split('.')[0]}_{timestamp}.png")
        else:
            # 修改: 当region为None时，在游戏窗口范围内查找而不是整个屏幕
            # 获取当前游戏窗口位置和大小
            # hwnd = find_window_by_title("Phone-E6EDU20429087631")
            hwnd = find_window_by_title(window_title)
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
            # 修改: 将截图保存到screenshots文件夹下
            screenshot.save(f"./screenshots/screenshot_find_{image_path.split('/')[-1].split('.')[0]}.png")
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