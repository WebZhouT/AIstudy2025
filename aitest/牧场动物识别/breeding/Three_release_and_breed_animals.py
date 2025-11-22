import cv2
import numpy as np
import pyautogui
import time
import os
import datetime
from PIL import ImageGrab
# 图像识别
from rapidocr_onnxruntime import RapidOCR
from image_utils import find_image_position

# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 导入自定义的图像工具模块
from image_utils import find_and_click_image, click_at_window_coord, mark_and_save_screenshot
# 初始化OCR引擎
ocr = RapidOCR()

def release_and_breed_animals():
    """3. 放出动物繁殖回收"""
    print('\n=== 放出动物繁殖回收 ===')
    
    # 点击宠物
    find_and_click_image('./breeding_image/pet.png', confidence=0.65)
    time.sleep(1)
    # 点击牧场空间
    find_and_click_image('./breeding_image/area.png', confidence=0.65)
    time.sleep(0.5)
    # 点击全部放出
    find_and_click_image('./breeding_image/giveout.png', confidence=0.65)
    time.sleep(1)
    # 点击关闭按钮
    find_and_click_image('./breeding_image/close.png', confidence=0.65)
    # 要查找的文字(匹配对应动物)
    target_text = "来自"
    
    # 获取窗口句柄
    hwnd = find_window_by_title(window_title)
    # 设置最大循环次数（每个动物3次，最多30次，预留次数防止出错）
    max_attempts = 55
    attempt_count = 0
    while attempt_count < max_attempts:
        attempt_count += 1
        print(f"\n--- 第 {attempt_count} 轮搜索 ---")
        
        # 查找目标文字的所有位置
        positions = find_text_positions_in_window(target_text)
        if positions:
            # 点击第一个匹配的位置
            position_x, position_y = positions[0]
            print(f"点击第一个匹配位置: ({position_x}, {position_y})")
            # 使用click_at_window_coord点击（点击动物繁殖连续点3次）
            click_at_window_coord(hwnd, position_x, position_y)
            print(f"成功点击: {target_text}")
            time.sleep(0.5)
            # 点击繁殖按钮
            exit = find_and_click_image('./breeding_image/get.png', confidence=0.65)
            if exit:
              # 截取识别区域进行OCR
              x, y, width, height = get_window_position(hwnd)
              window_region = (x, y, width, height)
              screenshot = pyautogui.screenshot(region=window_region)
              screenshot_np = np.array(screenshot)
              #判断是否包含指定文字请明天再来或者已繁殖出宝宝窝 
              # 使用OCR识别文字
              ocr_result, _ = ocr(screenshot_np)
              # print(f"识别结果:{ocr_result}")
              for text_info in ocr_result:
                  if text_info and len(text_info) > 1:
                      text = text_info[1]
                      
                      # 检查是否包含"请明天再来什么都没发生"
                      if "明天再" in text or "已经努力繁殖过3次" in text or "休息一下" in text:
                          # 如果匹配到明天再来，点击相同位置，然后点击动物回收
                          print("点击相同位置，已经努力繁殖过3次然后点击动物收回")
                          click_at_window_coord(hwnd, position_x, position_y)
                          print("点击相同位置1")
                          time.sleep(0.5)
                          find_and_click_image('./breeding_image/takeback.png', confidence=0.65)
              # # 保存当前窗口句柄的图片
              # # 生成文件名并保存
              # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
              # filename = os.path.join("debug_screenshots", f"breed_animals_{timestamp}.png")
              
              # # 确保目录存在
              # os.makedirs(os.path.dirname(filename), exist_ok=True)
              # cv2.imwrite(filename, cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR))
              # print(f"已保存状态截图: {filename}")
            else:
              print("点击繁殖失败，重新执行繁殖循环")
        else:
            print(f"未找到: {target_text}，退出循环")
            break
        
    # 以防万一，还要点动物去收回全部
    # 点击宠物
    find_and_click_image('./breeding_image/pet.png', confidence=0.65)
    time.sleep(0.5)
    # 点击牧场空间
    find_and_click_image('./breeding_image/area.png', confidence=0.65)
    time.sleep(0.5)
    # 点击收回全部
    find_and_click_image('./breeding_image/givebackall.png', confidence=0.65)
    time.sleep(0.5)
    # 确认收回确定按钮
    find_and_click_image('./breeding_image/takebackBtn.png', confidence=0.65)
    time.sleep(0.5)
    # 拜访结束
    find_and_click_image('./breeding_image/close.png', confidence=0.65)
    print("放出动物结束")
def find_text_positions_in_window(target_text, confidence_threshold=0.7):
    """
    在句柄窗口区域内识别指定文字，返回所有匹配到的坐标位置
    
    Args:
        target_text: 要查找的目标文字
        confidence_threshold: OCR置信度阈值
        
    Returns:
        list: 包含所有匹配位置坐标的列表，格式为[(x1, y1), (x2, y2), ...]
    """
    print(f"[find_text_positions_in_window] 开始查找文字: {target_text}")
    
    # 获取窗口句柄和位置
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        print("[find_text_positions_in_window] 未找到窗口句柄")
        return []
    
    x, y, width, height = get_window_position(hwnd)
    window_region = (x, y, width, height)
    print(f"[find_text_positions_in_window] 窗口区域: {window_region}")
    
    # 截取窗口区域进行OCR识别
    try:
        screenshot = pyautogui.screenshot(region=window_region)
        screenshot_np = np.array(screenshot)
        
        # 使用OCR识别文字
        if ocr is None:
            print("[find_text_positions_in_window] OCR引擎未初始化")
            return []
            
        ocr_result, _ = ocr(screenshot_np)
        print(f"[find_text_positions_in_window] 识别结果:{ocr_result}")
        # 收集所有匹配的位置
        recognized_positions = []
        
        for text_info in ocr_result:
            if text_info and len(text_info) > 1:
                text = text_info[1]
                conf = text_info[2] if len(text_info) > 2 else 0
                import re
                pattern = r'.*来自.*家$'
                # 检查是否匹配目标文字
                if re.match(pattern, text) and conf >= confidence_threshold:
                    # 获取文字位置信息
                    box = text_info[0]  # 文字包围盒
                    # 计算文字区域中心点
                    x_coords = [point[0] for point in box]
                    y_coords = [point[1] for point in box]
                    center_x = sum(x_coords) / len(x_coords)
                    center_y = sum(y_coords) / len(y_coords)
                    
                    # 转换为屏幕坐标（基于整个屏幕）
                    screen_x = window_region[0] + int(center_x)+5
                    screen_y = window_region[1] + int(center_y)-20
                    
                    print(f"[find_text_positions_in_window] 找到目标文字 '{target_text}'，坐标: ({screen_x}, {screen_y})，置信度: {conf:.4f}")
                    recognized_positions.append((screen_x, screen_y))
                elif '来自' in text and conf >= confidence_threshold:
                    # 获取文字位置信息
                    box = text_info[0]  # 文字包围盒
                    # 计算文字区域中心点
                    x_coords = [point[0] for point in box]
                    y_coords = [point[1] for point in box]
                    center_x = sum(x_coords) / len(x_coords)
                    center_y = sum(y_coords) / len(y_coords)
                    
                    # 转换为屏幕坐标（基于整个屏幕）
                    screen_x = window_region[0] + int(center_x)+5
                    screen_y = window_region[1] + int(center_y)-15
                    
                    print(f"[find_text_positions_in_window] 找到目标文字 '{target_text}'，坐标: ({screen_x}, {screen_y})，置信度: {conf:.4f}")

        print(f"[find_text_positions_in_window] 总共找到 {len(recognized_positions)} 个匹配位置")
        
        # # 保存截图用于调试
        # if recognized_positions:
        #     # 标记匹配位置并保存截图
        #     marked_screenshot = mark_text_positions_and_save_screenshot(
        #         screenshot_np, 
        #         recognized_positions, 
        #         target_text,
        #         x,  # offset_x
        #         y   # offset_y
        #     )
        #     if marked_screenshot:
        #         print(f"[find_text_positions_in_window] 已保存标记截图: {marked_screenshot}")
        # else:
        #     # 保存没有匹配项的截图
        #     screenshot_path = save_screenshot_without_matches(screenshot_np)
        #     if screenshot_path:
        #         print(f"[find_text_positions_in_window] 未找到匹配项，已保存原始截图: {screenshot_path}")
        
        return recognized_positions
        
    except Exception as e:
        print(f"[find_text_positions_in_window] OCR识别出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

# """ 截图DEBUG调试用的函数 """
# def mark_text_positions_and_save_screenshot(screenshot, positions, target_text, offset_x, offset_y):
#     """
#     在截图上标记所有匹配的文字位置并保存（黑白灰度）
#     """
#     try:
#         # 复制截图用于标记
#         marked_image = screenshot.copy()
        
#         # 确保图像是灰度图
#         if len(marked_image.shape) == 3:  # 如果是彩色图像
#             marked_image = cv2.cvtColor(marked_image, cv2.COLOR_BGR2GRAY)
        
#         # 为每个匹配位置绘制标记（使用白色标记）
#         for i, (x, y) in enumerate(positions):
#             # 计算实际绘制坐标（相对于截图）
#             local_x = int(x - offset_x)
#             local_y = int(y - offset_y)
            
#             # 绘制圆形标记（白色）
#             cv2.circle(marked_image, (local_x, local_y), 10, 255, 2)  # 255 = 白色
            
#             # 绘制十字标记（白色）
#             cv2.line(marked_image, (local_x-15, local_y), (local_x+15, local_y), 255, 2)
#             cv2.line(marked_image, (local_x, local_y-15), (local_x, local_y+15), 255, 2)
            
#             # 添加标签（白色）
#             label = f"{target_text}_{i+1}"
#             cv2.putText(marked_image, label, (local_x+15, local_y-15), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 1)
        
#         # 生成文件名并保存
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         filename = os.path.join("debug_screenshots", f"text_matches_{timestamp}.png")
        
#         # 确保目录存在
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
        
#         # 保存为灰度图
#         cv2.imwrite(filename, marked_image)
#         return filename
#     except Exception as e:
#         print(f"保存标记截图时出错: {e}")
#         return None

# def save_screenshot_without_matches(screenshot):
#     """
#     保存没有匹配项的截图（黑白灰度）
#     """
#     try:
#         # 确保图像是灰度图
#         if len(screenshot.shape) == 3:  # 如果是彩色图像
#             screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
#         # 生成文件名并保存
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         filename = os.path.join("debug_screenshots", f"no_text_matches_{timestamp}.png")
        
#         # 确保目录存在
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
        
#         # 保存为灰度图
#         cv2.imwrite(filename, screenshot)
#         return filename
#     except Exception as e:
#         print(f"保存原始截图时出错: {e}")
#         return None

# """ 截图DEBUG调试用的函数=================End ================= """