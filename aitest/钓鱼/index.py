# 图像识别
from rapidocr_onnxruntime import RapidOCR
import keyboard
import threading
import time
import traceback
import pyautogui
import os
from datetime import datetime
# 匹配指定窗口内的图片信息区域，进行ocr识别返回文字
from get_picture_ocrTxt import get_ocr_text_from_template
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title

# 在文件开头添加全局变量
running = False
stop_event = threading.Event()

# 创建调试截图目录
debug_screenshot_dir = "fishing_debug"
if not os.path.exists(debug_screenshot_dir):
    os.makedirs(debug_screenshot_dir)

# 图片模板路径
POWER_BAR_TEMPLATE = "power_bar.png"
START_TRIANGLE_TEMPLATE = "start_triangle.png"
END_TRIANGLE_TEMPLATE = "end_triangle.png"
MOVING_MARKER_TEMPLATE = "moving_marker.png"
HOOK_BUTTON_TEMPLATE = "hook_button.png"

""" ===================钓鱼游戏自动化方法==================== """

def match_template(template_path, confidence=0.8, region=None, save_debug=True):
    """
    在指定区域内匹配模板图片
    
    Args:
        template_path: 模板图片路径
        confidence: 匹配阈值
        region: 匹配区域 (x, y, width, height)，None表示全窗口
        save_debug: 是否保存调试图片
        
    Returns:
        pyautogui.Location or None: 匹配到的位置
    """
    try:
        # 获取窗口句柄和位置
        hwnd = find_window_by_title(window_title)
        if not hwnd:
            print(f"[match_template] 未找到窗口: {window_title}")
            return None
        
        x, y, width, height = get_window_position(hwnd)
        window_region = (x, y, width, height)
        
        # 如果指定了区域，则使用指定区域，否则使用整个窗口
        if region:
            search_region = (
                x + region[0],
                y + region[1],
                region[2],
                region[3]
            )
        else:
            search_region = window_region
        
        print(f"[match_template] 在区域 {search_region} 中查找模板: {template_path}")
        
        # 匹配模板
        location = pyautogui.locateOnScreen(
            template_path, 
            confidence=confidence, 
            region=search_region, 
            grayscale=True
        )
        
        if location:
            print(f"[match_template] 找到模板 {template_path} 位置: {location}")
            
            # 保存调试图片
            if save_debug:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_path = os.path.join(debug_screenshot_dir, f"match_{os.path.basename(template_path)}_{timestamp}.png")
                
                # 截取匹配区域
                match_region = (
                    location.left,
                    location.top,
                    location.width,
                    location.height
                )
                screenshot = pyautogui.screenshot(region=match_region)
                screenshot.save(debug_path)
                print(f"[match_template] 已保存匹配区域截图: {debug_path}")
            
            return location
        else:
            print(f"[match_template] 未找到模板: {template_path}")
            return None
            
    except Exception as e:
        print(f"[match_template] 匹配模板时出错: {str(e)}")
        traceback.print_exc()
        return None

def get_marker_position():
    """
    获取移动标志的位置
    
    Returns:
        dict or None: 包含移动标志位置信息的字典
    """
    # 先定位力量槽，缩小搜索范围
    power_bar = match_template(POWER_BAR_TEMPLATE, confidence=0.7)
    if not power_bar:
        print("[get_marker_position] 未找到力量槽")
        return None
    
    # 在力量槽上方区域搜索移动标志
    marker_region = (
        power_bar.left,
        power_bar.top - 50,  # 力量槽上方50像素
        power_bar.width,
        60  # 搜索高度
    )
    
    marker = match_template(MOVING_MARKER_TEMPLATE, confidence=0.7, region=marker_region)
    if marker:
        return {
            "left": marker.left,
            "top": marker.top,
            "right": marker.left + marker.width,
            "bottom": marker.top + marker.height,
            "center_x": marker.left + marker.width // 2,
            "center_y": marker.top + marker.height // 2
        }
    
    return None

def get_triangle_positions():
    """
    获取两个三角图标的位置
    
    Returns:
        dict or None: 包含两个三角图标位置信息的字典
    """
    # 先定位力量槽
    power_bar = match_template(POWER_BAR_TEMPLATE, confidence=0.7)
    if not power_bar:
        print("[get_triangle_positions] 未找到力量槽")
        return None
    
    # 在力量槽下方区域搜索三角图标
    triangle_region = (
        power_bar.left,
        power_bar.bottom,  # 力量槽底部
        power_bar.width,
        50  # 搜索高度
    )
    
    start_triangle = match_template(START_TRIANGLE_TEMPLATE, confidence=0.7, region=triangle_region)
    end_triangle = match_template(END_TRIANGLE_TEMPLATE, confidence=0.7, region=triangle_region)
    
    if start_triangle and end_triangle:
        # 确定哪个是开始三角，哪个是结束三角（根据x坐标）
        if start_triangle.left < end_triangle.left:
            start = start_triangle
            end = end_triangle
        else:
            start = end_triangle
            end = start_triangle
        
        return {
            "start_triangle": {
                "left": start.left,
                "top": start.top,
                "right": start.left + start.width,
                "bottom": start.top + start.height,
                "center_x": start.left + start.width // 2,
                "center_y": start.top + start.height // 2
            },
            "end_triangle": {
                "left": end.left,
                "top": end.top,
                "right": end.left + end.width,
                "bottom": end.top + end.height,
                "center_x": end.left + end.width // 2,
                "center_y": end.top + end.height // 2
            },
            "valid_range_start": start.left + start.width,  # 有效范围开始（开始三角的右侧）
            "valid_range_end": end.left,  # 有效范围结束（结束三角的左侧）
            "valid_range_width": end.left - (start.left + start.width)  # 有效范围宽度
        }
    
    print(f"[get_triangle_positions] 未找到两个三角图标，找到开始三角: {start_triangle is not None}, 结束三角: {end_triangle is not None}")
    return None

def is_marker_in_valid_range(marker_pos, triangle_pos):
    """
    判断移动标志是否在有效范围内
    
    Args:
        marker_pos: 移动标志位置信息
        triangle_pos: 三角图标位置信息
        
    Returns:
        bool: 是否在有效范围内
    """
    if not marker_pos or not triangle_pos:
        return False
    
    marker_center_x = marker_pos["center_x"]
    valid_start = triangle_pos["valid_range_start"]
    valid_end = triangle_pos["valid_range_end"]
    
    in_range = valid_start <= marker_center_x <= valid_end
    
    print(f"[is_marker_in_valid_range] 移动标志位置: {marker_center_x}, 有效范围: [{valid_start}, {valid_end}], 是否在范围内: {in_range}")
    
    return in_range

def click_hook_button():
    """
    点击起竿按钮
    
    Returns:
        bool: 是否成功点击
    """
    hook_button = match_template(HOOK_BUTTON_TEMPLATE, confidence=0.7)
    if hook_button:
        button_center = (
            hook_button.left + hook_button.width // 2,
            hook_button.top + hook_button.height // 2
        )
        
        print(f"[click_hook_button] 点击起竿按钮位置: {button_center}")
        pyautogui.click(button_center[0], button_center[1])
        show_alert("已点击起竿按钮")
        return True
    
    print("[click_hook_button] 未找到起竿按钮")
    return False

def save_composite_debug_image(marker_pos, triangle_pos, in_range):
    """
    保存复合调试图片，显示所有元素位置和状态
    
    Args:
        marker_pos: 移动标志位置
        triangle_pos: 三角图标位置
        in_range: 是否在有效范围内
    """
    try:
        import cv2
        import numpy as np
        
        # 获取窗口截图
        hwnd = find_window_by_title(window_title)
        if not hwnd:
            return
        
        x, y, width, height = get_window_position(hwnd)
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot_np = np.array(screenshot)
        debug_image = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # 绘制移动标志位置
        if marker_pos:
            cv2.rectangle(debug_image, 
                         (marker_pos["left"] - x, marker_pos["top"] - y),
                         (marker_pos["right"] - x, marker_pos["bottom"] - y),
                         (0, 255, 0) if in_range else (0, 0, 255), 2)  # 绿色表示在范围内，红色表示不在范围内
            cv2.putText(debug_image, f"Marker: {marker_pos['center_x']}", 
                       (marker_pos["left"] - x, marker_pos["top"] - y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if in_range else (0, 0, 255), 1)
        
        # 绘制三角图标位置和有效范围
        if triangle_pos:
            # 开始三角
            start = triangle_pos["start_triangle"]
            cv2.rectangle(debug_image,
                         (start["left"] - x, start["top"] - y),
                         (start["right"] - x, start["bottom"] - y),
                         (255, 255, 0), 2)  # 青色
            cv2.putText(debug_image, "Start",
                       (start["left"] - x, start["top"] - y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # 结束三角
            end = triangle_pos["end_triangle"]
            cv2.rectangle(debug_image,
                         (end["left"] - x, end["top"] - y),
                         (end["right"] - x, end["bottom"] - y),
                         (255, 255, 0), 2)  # 青色
            cv2.putText(debug_image, "End",
                       (end["left"] - x, end["top"] - y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # 有效范围
            valid_start = triangle_pos["valid_range_start"]
            valid_end = triangle_pos["valid_range_end"]
            cv2.line(debug_image,
                    (valid_start - x, start["top"] - y - 20),
                    (valid_start - x, start["bottom"] - y + 20),
                    (255, 255, 0), 2)
            cv2.line(debug_image,
                    (valid_end - x, end["top"] - y - 20),
                    (valid_end - x, end["bottom"] - y + 20),
                    (255, 255, 0), 2)
            
            # 有效范围文本
            range_text = f"Range: {valid_start}-{valid_end} (Width: {triangle_pos['valid_range_width']})"
            cv2.putText(debug_image, range_text,
                       (x + 10, y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # 状态文本
        status_text = f"In Range: {in_range}"
        status_color = (0, 255, 0) if in_range else (0, 0, 255)
        cv2.putText(debug_image, status_text,
                   (x + 10, y + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # 保存图片
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = os.path.join(debug_screenshot_dir, f"fishing_debug_{timestamp}.png")
        cv2.imwrite(debug_path, debug_image)
        print(f"[save_composite_debug_image] 已保存复合调试图片: {debug_path}")
        
    except ImportError:
        print("[save_composite_debug_image] 未安装cv2，跳过复合调试图片保存")
    except Exception as e:
        print(f"[save_composite_debug_image] 保存复合调试图片时出错: {str(e)}")

def stop_script():
    """停止脚本"""
    global running
    running = False
    stop_event.set()
    print("\n===== 脚本已停止 =====")

def start_script():
    """启动脚本"""
    global running
    running = True
    stop_event.clear()
    print("\n===== 脚本已启动 =====")

# 主函数
def main_loop():
    """钓鱼游戏主循环"""
    print("开始钓鱼游戏自动化...")
    
    last_hook_time = 0
    hook_cooldown = 2  # 起竿冷却时间（秒）
    
    while not stop_event.is_set():
        if not running:
            time.sleep(0.1)
            continue
            
        try:
            # 获取移动标志位置
            marker_pos = get_marker_position()
            
            # 获取三角图标位置
            triangle_pos = get_triangle_positions()
            
            # 判断是否在有效范围内
            in_range = is_marker_in_valid_range(marker_pos, triangle_pos)
            
            # 保存复合调试图片
            save_composite_debug_image(marker_pos, triangle_pos, in_range)
            
            # 如果在有效范围内且冷却时间已过，点击起竿按钮
            current_time = time.time()
            if in_range and (current_time - last_hook_time) > hook_cooldown:
                print("[main_loop] 移动标志在有效范围内，尝试起竿...")
                if click_hook_button():
                    last_hook_time = current_time
                    print("[main_loop] 起竿成功!")
                else:
                    print("[main_loop] 起竿失败!")
            
            # 控制循环频率
            time.sleep(0.2)  # 200ms刷新一次
            
        except Exception as e:
            print(f"[main_loop] 发生错误: {str(e)}")
            traceback.print_exc()
            time.sleep(1)  # 出错后等待1秒再继续

def main():
    # 注册热键
    keyboard.add_hotkey('f1', start_script)
    keyboard.add_hotkey('f2', stop_script)
    
    print("钓鱼游戏自动化脚本")
    print("提示: 按 F1 启动脚本，按 F2 停止脚本")
    print("确保以下图片文件存在于当前目录:")
    print(f"  - {POWER_BAR_TEMPLATE} (力量槽)")
    print(f"  - {START_TRIANGLE_TEMPLATE} (开始三角图标)")
    print(f"  - {END_TRIANGLE_TEMPLATE} (结束三角图标)")
    print(f"  - {MOVING_MARKER_TEMPLATE} (移动标志)")
    print(f"  - {HOOK_BUTTON_TEMPLATE} (起竿按钮)")
    
    try:
        # 启动主循环
        main_loop()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"\n程序发生未处理的异常: {type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        stop_event.set()
        keyboard.unhook_all()

# 使用示例
if __name__ == "__main__":
    main()