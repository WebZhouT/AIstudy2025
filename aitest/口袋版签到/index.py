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
# 添加cv2导入用于图像处理
import cv2
import numpy as np
# 添加RapidOCR导入
from rapidocr_onnxruntime import RapidOCR
import json

# 初始化 OCR 引擎
ocr = RapidOCR()
# 全局变量控制运行状态
running = False
stop_event = threading.Event()
# 定义角色名列表，按照优先级排序
# userlist=[]
userlist = ["50J的铁","家具存放123","宝石存放12","鱼的仓库","6070书铁仓库"]
# 当前操作的目标角色名字
aimData=''
# 当前匹配的角色索引
current_character_index = -1
# 切换账号图片
changerole = "changerole.png"
# 账号登录图片
login_img = "login.png"
# 选择账号切换图片
switch_img = "switch.png"
# 需要登录的用户名信息
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
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None


def get_window_position(hwnd):
    """获取窗口位置和大小"""
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height

# 添加新函数：在窗口中查找图片位置
def find_image_in_window(window_title, image_path, confidence=0.8):
    """
    在指定窗口中查找图片位置
    
    参数:
    window_title: 窗口标题
    image_path: 图片路径
    confidence: 相似度阈值 (默认0.8)
    
    返回:
    tuple: (x, y, width, height) 图片在窗口中的位置和大小，未找到则返回(None, None, None, None)
    """
    # 查找窗口
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        return None, None, None, None
    
    # 获取窗口位置和大小
    win_x, win_y, win_width, win_height = get_window_position(hwnd)
    
    # 截取窗口截图
    screenshot = pyautogui.screenshot(region=(win_x, win_y, win_width, win_height))
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 读取模板图片
    template = cv2.imread(image_path)
    if template is None:
        print(f"无法读取图片: {image_path}")
        return None, None, None, None
    
    # 模板匹配
    result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    # 检查匹配度是否满足要求
    if max_val >= confidence:
        # 获取匹配位置
        x, y = max_loc
        height, width = template.shape[:2]
        # 返回相对于窗口的位置
        return x, y, width, height
    else:
        print(f"未找到匹配图片，最高相似度: {max_val:.2f}")
        return None, None, None, None

# 修改函数：点击图像中心位置，接受窗口位置和图像位置参数
def click_image_center_in_window(window_pos, image_pos):
    """
    在窗口中点击图像的中心位置
    
    参数:
    window_pos: 窗口位置 (win_x, win_y, win_width, win_height)
    image_pos: 图像位置 (x, y, width, height)
    """
    win_x, win_y, _, _ = window_pos
    x, y, width, height = image_pos
    
    # 计算图像中心点在屏幕上的绝对坐标
    center_x = win_x + x + width // 2
    center_y = win_y + y + height // 2
    
    # 点击中心位置
    pyautogui.click(center_x, center_y)
    print(f"已点击位置: ({center_x}, {center_y})")

def find_drag_area_and_scroll(region, drag_area_template, character_names, threshold=0.8):
    """
    匹配拖拽区域并实现上下滚动功能
    
    Args:
        region: 窗口区域 (x, y, width, height)
        drag_area_template: 拖拽区域模板图片路径
        character_names: 角色名列表，按优先级排序
        threshold: 匹配阈值
        
    Returns:
        bool: 是否成功匹配并执行滚动操作
    """
    global aimData, current_character_index, window_title  # 添加 window_title 到全局变量
    
    # 1. 匹配拖拽区域
    print("[find_drag_area_and_scroll] 开始匹配拖拽区域...")
    # 修改: 使用窗口标题而不是窗口位置来查找图像
    drag_area_matched = find_image_in_window(window_title, drag_area_template, threshold)
    
    if drag_area_matched:
        print("[find_drag_area_and_scroll] 成功匹配拖拽区域")
        # 获取拖拽区域的坐标信息
        # 这里需要根据实际模板匹配结果来确定拖拽区域的具体坐标
        # 由于find_and_click_template已经实现了点击操作，我们这里主要关注区域匹配
        
        # 2. 循环查找角色名
        max_scroll_attempts = 40  # 最大拖拽次数
        scroll_count = 0
        
        while scroll_count < max_scroll_attempts and not stop_event.is_set() and running:
            # 截取当前区域进行OCR识别
            try:
                # 截取整个窗口区域进行OCR
                screenshot = pyautogui.screenshot(region=region)
                screenshot_np = np.array(screenshot)
                
                # 使用RapidOCR识别文字
                ocr_result, _ = ocr(screenshot_np)
                print(f"[find_drag_area_and_scroll] OCR识别结果: {ocr_result}")
                
                # 检查是否有识别结果
                if ocr_result:
                    # 提取所有识别到的文本
                    recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
                    
                    # 检查当前索引对应的角色名是否在识别结果中
                    if current_character_index < len(character_names):
                        current_character = character_names[current_character_index]
                        # 检查当前角色名是否在任一识别到的文本中
                        for text_info in ocr_result:
                            if len(text_info) > 1 and current_character in text_info[1]:
                                # 获取文字位置信息
                                box = text_info[0]  # 文字包围盒
                                # 计算文字区域中心点
                                x_coords = [point[0] for point in box]
                                y_coords = [point[1] for point in box]
                                center_x = sum(x_coords) / len(x_coords)
                                center_y = sum(y_coords) / len(y_coords)
                                
                                # 转换为屏幕坐标
                                screen_x = region[0] + int(center_x)
                                screen_y = region[1] + int(center_y)
                                
                                print(f"[find_drag_area_and_scroll] 找到角色 {current_character}，点击坐标: ({screen_x}, {screen_y})")
                                # 保存角色名到全局变量
                                aimData = current_character
                                # 点击角色名字
                                pyautogui.moveTo(screen_x, screen_y, duration=0.1)
                                pyautogui.click(screen_x, screen_y)
                                # 找到目标角色并点击后，不再执行拖拽，直接返回
                                return True
                
                # 如果没有找到当前角色名，执行拖拽操作
                print(f"[find_drag_area_and_scroll] 未找到目标角色 {character_names[current_character_index] if current_character_index < len(character_names) else 'N/A'}，执行拖拽操作...")
                
                # 根据窗口区域计算拖拽起始和结束点
                x, y, w, h = region
                # 设置拖拽起始点（区域中部偏下）
                start_x = x + w // 2
                start_y = y + int(h * 0.7)
                # 设置拖拽结束点（区域中部偏上）
                end_x = x + w // 2
                # end_y = y + int(h * 0.3)-250
                end_y = y + int(h * 0.5)
                
                # 执行拖拽操作
                drag_from_to(start_x, start_y, end_x, end_y)
                time.sleep(0.5)  # 等待拖拽效果
                scroll_count += 1
                
            except Exception as e:
                print(f"[find_drag_area_and_scroll] OCR识别出错: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # 即使OCR出错，也执行拖拽操作
                # 根据窗口区域计算拖拽起始和结束点
                x, y, w, h = region
                # 设置拖拽起始点（区域中部偏下）
                start_x = x + w // 2
                start_y = y + int(h * 0.7)
                # 设置拖拽结束点（区域中部偏上）
                end_x = x + w // 2
                end_y = y + int(h * 0.5)
                
                # 执行拖拽操作
                drag_from_to(start_x, start_y, end_x, end_y)
                time.sleep(0.5)
                scroll_count += 1
        
        if scroll_count >= max_scroll_attempts:
            print("[find_drag_area_and_scroll] 已达到最大拖拽次数，未找到目标角色")
        
        return True
    else:
        print("[find_drag_area_and_scroll] 未匹配到拖拽区域")
        return False

# 主函数包含所有程序逻辑
def main_loop():
    # 定义图片内容
    global running, current_character_index, window_title  # 声明所有需要的全局变量
    window_title = "Phone-OBN7WS7D99EYFI49" 
    error_count = 0  # 初始化错误计数
    max_errors = 5   # 最大错误次数
    # 初始化current_character_index
    current_character_index = 0
    while not stop_event.is_set():
        if running:
            print(f"[主循环] 正在监听窗口: {window_title}")
            # 查找游戏窗口
            hwnd = find_window_by_title(window_title)  # 需要替换为实际的游戏窗口标题
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
                
                # 查找图像位置并点击中心位置（简化为2行代码）
                # 第一行：在指定窗口中查找图像，返回图像位置信息（x, y, width, height）
                image_pos = find_image_in_window(window_title, changerole, confidence=0.8)
                # 第二行：判断是否所有坐标都不为None（即找到了图像），然后获取窗口位置并点击图像中心
                if all(coord is not None for coord in image_pos):
                    # 获取窗口在屏幕上的绝对位置和尺寸
                    window_pos = get_window_position(hwnd)
                    # 点击图像的中心位置
                    click_image_center_in_window(window_pos, image_pos)
                    time.sleep(1)
                    
                    # 处理拖拽区域（新添加的功能）
                    # 需要准备一个拖拽区域的模板图片，例如 "drag_area.png"
                    drag_area_template = "drag_area.png"  # 请确保该图片文件存在
                    # 修改: 传递窗口位置作为region参数，而不是窗口标题
                    result = find_drag_area_and_scroll(window_pos, drag_area_template, userlist, 0.3)
                    
                    # 如果成功找到并点击了角色，则更新索引以切换到下一个角色
                    if result:
                        current_character_index += 1
                        # 如果已遍历完所有角色，则重置索引为0
                        if current_character_index >= len(userlist):
                            current_character_index = 0
                            # 所有角色都已处理完毕，可以添加相应的提示或操作
                            print("所有角色已处理完毕，重新开始")
                    
                    time.sleep(1)
                else:
                    # 添加未识别到图像的错误提示
                    print(f"未能识别到图像 {changerole}，请检查图像是否存在或清晰度")
                    error_count += 1
                    if error_count >= max_errors:
                        print("连续未识别到图像次数过多，脚本将停止")
                        show_alert("图像识别失败次数过多，脚本已停止")
                        stop_script()
                    time.sleep(1)
                    continue

def drag_from_to(start_x, start_y, end_x, end_y):
    """
    从起始坐标拖拽到终止坐标
    
    Args:
        start_x: 起始点x坐标
        start_y: 起始点y坐标
        end_x: 终止点x坐标
        end_y: 终止点y坐标
    """
    print(f"[drag_from_to] 执行拖拽操作: 从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
    
    # 执行拖拽操作：鼠标左键按住、拖动、放开
    # 注意：这里先注释掉实际的鼠标操作，供您测试
    '''

    '''
    pyautogui.moveTo(start_x, start_y, duration=0.1)
    pyautogui.mouseDown()
    pyautogui.moveTo(end_x, end_y, duration=0.3)
    pyautogui.mouseUp()
    # 添加测试用的延时
    time.sleep(0.1)

def perform_drag_scroll(window_region):
    """
    在指定区域内执行拖拽滚动操作
    
    Args:
        window_region: 窗口区域 (x, y, width, height)
    """
    # 根据窗口区域计算拖拽起始和结束点
    x, y, w, h = window_region
    
    # 设置拖拽起始点（区域中部偏下）
    start_x = x + w // 2
    start_y = y + int(h * 0.7)
    
    # 设置拖拽结束点（区域中部偏上）
    end_x = x + w // 2
    end_y = y + int(h * 0.3)
    
    # 调用通用拖拽函数
    drag_from_to(start_x, start_y, end_x, end_y)
def start_script():
    """启动脚本"""
    global running
    running = True
    print("\n===== 脚本已启动 =====")

def stop_script():
    """停止脚本"""
    global running
    running = False
    print("\n===== 脚本已停止 =====")


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