# wait_utils.py
# 用于等待指定图片出现后执行后续逻辑
import cv2
import numpy as np
import pyautogui
import time
from PIL import ImageGrab
from image_utils import find_image_position

def wait_for_image(image_path, confidence=0.65, region=None, timeout=30, check_interval=0.5):
    """
    等待指定图片出现
    
    参数:
        image_path: 要等待的图片路径
        confidence: 匹配置信度阈值 (默认0.8)
        region: 搜索区域 (x, y, width, height)，为None时搜索全屏
        timeout: 超时时间，秒 (默认30秒)
        check_interval: 检查间隔，秒 (默认0.5秒)
    
    返回:
        dict: 图片位置信息，包含 'x', 'y', 'width', 'height', 'confidence'
        None: 超时未找到图片
    """
    print(f"等待图片出现: {image_path} (超时: {timeout}秒)")
    
    start_time = time.time()
    elapsed_time = 0
    
    while elapsed_time < timeout:
        # 查找图片位置
        position = find_image_position(image_path, confidence, region)
        
        if position:
            print(f"图片已出现: {image_path} (位置: {position['x']}, {position['y']}), 耗时: {elapsed_time:.1f}秒")
            return position
        
        # 等待下一次检查
        time.sleep(check_interval)
        elapsed_time = time.time() - start_time
    
    print(f"等待图片超时: {image_path} (超过 {timeout}秒)")
    return None

def wait_for_image_disappear(image_path, confidence=0.65, region=None, timeout=30, check_interval=0.5):
    """
    等待指定图片消失
    
    参数:
        image_path: 要等待消失的图片路径
        confidence: 匹配置信度阈值 (默认0.8)
        region: 搜索区域 (x, y, width, height)，为None时搜索全屏
        timeout: 超时时间，秒 (默认30秒)
        check_interval: 检查间隔，秒 (默认0.5秒)
    
    返回:
        bool: True - 图片已消失, False - 超时图片仍然存在
    """
    print(f"等待图片消失: {image_path} (超时: {timeout}秒)")
    
    start_time = time.time()
    elapsed_time = 0
    
    while elapsed_time < timeout:
        # 查找图片位置
        position = find_image_position(image_path, confidence, region)
        
        if not position:
            print(f"图片已消失: {image_path}, 耗时: {elapsed_time:.1f}秒")
            return True
        
        # 等待下一次检查
        time.sleep(check_interval)
        elapsed_time = time.time() - start_time
    
    print(f"等待图片消失超时: {image_path} (超过 {timeout}秒)")
    return False

def wait_for_multiple_images(image_paths, confidence=0.65, region=None, timeout=30, check_interval=0.5):
    """
    等待多个图片中的任意一个出现
    
    参数:
        image_paths: 图片路径列表
        confidence: 匹配置信度阈值 (默认0.8)
        region: 搜索区域 (x, y, width, height)，为None时搜索全屏
        timeout: 超时时间，秒 (默认30秒)
        check_interval: 检查间隔，秒 (默认0.5秒)
    
    返回:
        tuple: (图片路径, 位置信息) 或 (None, None) 如果超时
    """
    print(f"等待多个图片中的任意一个出现: {image_paths} (超时: {timeout}秒)")
    
    start_time = time.time()
    elapsed_time = 0
    
    while elapsed_time < timeout:
        for image_path in image_paths:
            position = find_image_position(image_path, confidence, region)
            if position:
                print(f"图片已出现: {image_path} (位置: {position['x']}, {position['y']}), 耗时: {elapsed_time:.1f}秒")
                return image_path, position
        
        # 等待下一次检查
        time.sleep(check_interval)
        elapsed_time = time.time() - start_time
    
    print(f"等待多个图片超时: {image_paths} (超过 {timeout}秒)")
    return None, None

def wait_for_condition(condition_func, timeout=30, check_interval=0.5, condition_name="条件"):
    """
    等待自定义条件满足
    
    参数:
        condition_func: 条件函数，返回True表示条件满足
        timeout: 超时时间，秒 (默认30秒)
        check_interval: 检查间隔，秒 (默认0.5秒)
        condition_name: 条件名称，用于日志输出
    
    返回:
        bool: True - 条件满足, False - 超时条件未满足
    """
    print(f"等待条件满足: {condition_name} (超时: {timeout}秒)")
    
    start_time = time.time()
    elapsed_time = 0
    
    while elapsed_time < timeout:
        if condition_func():
            print(f"条件已满足: {condition_name}, 耗时: {elapsed_time:.1f}秒")
            return True
        
        # 等待下一次检查
        time.sleep(check_interval)
        elapsed_time = time.time() - start_time
    
    print(f"等待条件超时: {condition_name} (超过 {timeout}秒)")
    return False