import cv2
import numpy as np
import pyautogui
import time
import os
import datetime
from PIL import ImageGrab
from image_utils import find_image_position
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 导入自定义的图像工具模块
from image_utils import find_and_click_image, click_at_window_coord, mark_and_save_screenshot
def carry_animals_out():
    """1. 携带出游"""
    print('\n=== 开始携带出游流程 ===')
    
    # 设置最大循环次数防止无限循环
    max_attempts = 12
    attempt_count = 0
    
    while attempt_count < max_attempts:
        attempt_count += 1
        print(f"\n--- 第 {attempt_count} 轮搜索 ---")
        
        # 获取图片路径列表
        image_paths = getExitAnimal()
        if not image_paths:
            print("未找到动物图片路径，退出循环")
            break
            
        # 等待多个动物图片出现
        matches = wait_for_multiple_images(image_paths, confidence=0.65)
        
        # 检查是否找到匹配结果
        if matches:
            print(f"找到 {len(matches)} 个动物")
            
            # 遍历所有匹配结果并点击
            image_path, position = matches[0]
            print(f"点击动物: {os.path.basename(image_path)} 位置: ({position['x']}, {position['y']})")
            
            # 获取窗口句柄
            hwnd = find_window_by_title(window_title)
            if hwnd:
                # 点击动物
                click_at_window_coord(hwnd, position['x'], position['y'])
                time.sleep(1)
                
                # 携带出游按钮
                find_and_click_image('./breeding_image/play.png', confidence=0.65)
                time.sleep(0.5)
            else:
                print("未找到游戏窗口")
                break
                    
            # 点击完一轮后等待一段时间再继续搜索
            print("完成一轮点击，等待1秒后继续搜索...")
            time.sleep(0.5)
        else:
            print("未找到任何动物图片，退出循环")
            break
            
    print(f"携带出游流程完成，共执行 {attempt_count} 轮搜索")
    
    # 如果达到最大尝试次数，给出提示
    if attempt_count >= max_attempts:
        print("已达到最大尝试次数，强制退出循环")

""" 截图DEBUG调试用的函数 """
# def mark_multiple_matches_and_save_screenshot(screenshot, matches, offset_x, offset_y, image_paths=None):
#     """
#     在截图上标记所有匹配的图片位置并保存
    
#     参数:
#         screenshot: 屏幕截图 (OpenCV格式)
#         matches: 匹配结果列表 [(image_path, position), ...]
#         offset_x: X轴偏移量
#         offset_y: Y轴偏移量,
#         image_paths: 所有尝试匹配的图片路径列表（可选）
    
#     返回:
#         str: 保存的截图文件路径
#     """
#     try:
#         # 复制截图用于标记
#         marked_image = screenshot.copy()
        
#         # 为每个匹配项绘制标记
#         for image_path, position in matches:
#             # 计算实际绘制坐标
#             top_left_x = int(position['x'] - offset_x - position['width'] // 2)
#             top_left_y = int(position['y'] - offset_y - position['height'] // 2)
#             bottom_right_x = int(top_left_x + position['width'])
#             bottom_right_y = int(top_left_y + position['height'])
            
#             # 绘制矩形框
#             cv2.rectangle(marked_image, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 255, 0), 2)
            
#             # 添加标签
#             label = f"{os.path.basename(image_path)}: {position['confidence']:.2f}"
#             cv2.putText(marked_image, label, (top_left_x, top_left_y - 10), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
#         # 生成文件名并保存
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         filename = os.path.join("debug_screenshots", f"multiple_matches_{timestamp}.png")
        
#         # 确保目录存在
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
        
#         cv2.imwrite(filename, marked_image)
#         return filename
#     except Exception as e:
#         print(f"保存标记截图时出错: {e}")
#         return None

# def save_screenshot_without_matches(screenshot):
#     """
#     保存没有匹配项的截图
    
#     参数:
#         screenshot: 屏幕截图 (OpenCV格式)
    
#     返回:
#         str: 保存的截图文件路径
#     """
#     try:
#         # 生成文件名并保存
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         filename = os.path.join("debug_screenshots", f"no_matches_{timestamp}.png")
        
#         # 确保目录存在
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
        
#         cv2.imwrite(filename, screenshot)
#         return filename
#     except Exception as e:
#         print(f"保存原始截图时出错: {e}")
#         return None
    

""" 截图DEBUG调试用的函数=================End ================= """

def wait_for_multiple_images(image_paths, confidence=0.65, region=None):
    """
    等待多个图片中的任意一个出现
    
    参数:
        image_paths: 图片路径列表
        confidence: 匹配置信度阈值 (默认0.8)
        region: 搜索区域 (x, y, width, height)，为None时搜索句柄窗口区域
    
    返回:
        tuple: (图片路径, 位置信息) 或 (None, None) 如果未找到
    """
    # 如果region为None，则使用句柄窗口区域
    if region is None:
        hwnd = find_window_by_title(window_title)
        if hwnd:
            x, y, width, height = get_window_position(hwnd)
            region = (x, y, x + width, y + height)
            print(f"使用窗口区域: {region}")
        else:
            print("未找到窗口句柄，将搜索全屏")
    
    print(f"查找多个图片中的任意一个: {image_paths}")
    
    # 获取屏幕截图用于标记
    if region:
        screenshot = ImageGrab.grab(bbox=region)
        offset_x, offset_y = region[0], region[1]
    else:
        screenshot = ImageGrab.grab()
        offset_x, offset_y = 0, 0
    
    # 转换为OpenCV格式并转为灰度图
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_screenshot = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
    
    # 用于保存所有匹配结果的列表
    matches = []
    
    # 为每个模板图片进行匹配
    for image_path in image_paths:
        # 读取模板图片并转换为灰度图
        with open(image_path, 'rb') as f:
            file_bytes = np.frombuffer(f.read(), np.uint8)
            template = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"无法读取模板图片: {image_path}")
                continue
                
            # 执行模板匹配
            result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 输出最大匹配度
            print(f"图片 {image_path} 的最大匹配度: {max_val:.4f}")
            
            # 如果最大匹配度超过阈值，则认为匹配成功
            if max_val >= confidence:
                # 计算匹配位置
                top_left = max_loc
                center_x = offset_x + top_left[0] + template.shape[1] // 2
                center_y = offset_y + top_left[1] + template.shape[0] // 2
                
                position = {
                    'x': center_x,
                    'y': center_y,
                    'width': template.shape[1],
                    'height': template.shape[0],
                    'confidence': max_val
                }
                
                # 收集匹配项
                matches.append((image_path, position))
                print(f"图片 {image_path} 匹配成功，位置: ({center_x}, {center_y})，匹配度: {max_val:.4f}")
            else:
                print(f"图片 {image_path} 匹配失败，最大匹配度: {max_val:.4f} < {confidence}")
    
    # 如果找到了匹配项
    if matches:
        # # 标记所有匹配区域并保存截图
        # marked_screenshot = mark_multiple_matches_and_save_screenshot(
        #     screenshot_cv, 
        #     matches, 
        #     offset_x, 
        #     offset_y,
        #     image_paths
        # )
        # if marked_screenshot:
        #     print(f"已保存标记截图: {marked_screenshot}")
        
        # 返回所有匹配项，而不是第一个
        print(f"找到 {len(matches)} 个匹配项")
        return matches  # 返回整个matches列表
    else:
        # 即使没有匹配到也保存截图
        # screenshot_path = save_screenshot_without_matches(screenshot_cv)
        # if screenshot_path:
        #     print(f"未找到匹配项，已保存原始截图: {screenshot_path}")
        
        print(f"未找到任何匹配的图片: {image_paths}")
        return []  # 返回空列表而不是None

def getExitAnimal():
    print('动物携带拜访繁殖')
    # 获取breeding文件夹下所有图片文件
    current_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(current_dir)  # 获取上级目录
    breeding_folder = os.path.join(project_root, 'image', 'breeding')
    
    # 确保使用正确的编码处理路径
    breeding_folder = os.path.normpath(breeding_folder)
    image_paths = []
    
    if os.path.exists(breeding_folder):
        for filename in os.listdir(breeding_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # 使用normpath确保路径格式正确
                full_path = os.path.normpath(os.path.join(breeding_folder, filename))
                image_paths.append(full_path)
        print(f"找到 {len(image_paths)} 个图片文件用于匹配")
    else:
        print(f"文件夹 {breeding_folder} 不存在")
        return []
    
    return image_paths  # 只返回图片路径列表