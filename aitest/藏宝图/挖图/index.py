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

# 点击藏宝图
def click_treasure_maps(locations, x, y, width, height):
    """根据坐标数组依次点击藏宝图"""
    # 这里可以根据需要扩展点击逻辑
    print(f"找到{len(locations)}个藏宝图位置")
    for loc in locations:
        if not running:  # 检查是否已停止
            break
        pyautogui.click(loc.left + loc.width//2, loc.top + loc.height//2)
        time.sleep(0.5)


# 新增: 通用图片匹配和点击函数
def find_and_click_image(image_path, confidence=0.8, region=None, click=True):
    """
    通用的图片匹配和点击函数
    
    参数:
    image_path: 图片路径
    confidence: 匹配相似度
    region: 匹配区域 (left, top, width, height)
    click: 是否点击匹配位置
    
    返回:
    匹配位置或None
    """
    try:
        if region:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
        else:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            
        if location and click:
            pyautogui.click(location.left + location.width//2, location.top + location.height//2)
            time.sleep(0.5)  # 添加点击后的延迟
            
        return location
    except pyautogui.ImageNotFoundException:
        return None

# 新增: 查找所有匹配图片的位置
def find_all_images(image_path, confidence=0.8, region=None):
    """
    查找所有匹配的图片位置
    
    参数:
    image_path: 图片路径
    confidence: 匹配相似度
    region: 匹配区域 (left, top, width, height)
    
    返回:
    匹配位置列表
    """
    try:
        if region:
            locations = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence, region=region))
        else:
            locations = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
        return locations
    except pyautogui.ImageNotFoundException:
        return []  # 返回空列表而不是抛出异常

# 全局变量控制运行状态
running = False
stop_event = threading.Event()
# 新增: 存储提取的坐标
extracted_coordinate = None
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
    },
    {
      'name':"0",
      'png':"./keyboard/0.png"
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
        else:
            screenshot = pyautogui.screenshot()
            
        # 保存临时截图用于OCR识别
        temp_image = "temp_ocr_image.png"
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
    根据坐标值点击数字键盘图片输入坐标
    
    参数:
    coordinate: 坐标数组 [x, y]
    """
    global extracted_coordinate  # 新增: 声明全局变量
    if not coordinate or len(coordinate) != 2:
        print("坐标数据不正确")
        return
    
    x, y = coordinate
    extracted_coordinate = [x, y]  # 新增: 保存提取的坐标
    
    # 输入X坐标
    print(f"正在输入X坐标: {x}")
    for digit in str(x):
        # 查找对应的数字图片并点击
        for key_info in area:
            if key_info['name'] == digit:
                find_and_click_image(key_info['png'], confidence=0.98)
                time.sleep(0.3)  # 添加点击后的延迟
                break
    #点击确认按钮
    find_and_click_image('./keyboard/sure.png', confidence=0.85) 
    time.sleep(1)     
    # # 点击Y坐标输入框（假设存在ybtn.png图片）
    # find_and_click_image('ybtn.png', confidence=0.8)
    # time.sleep(2)
    
    # 输入Y坐标
    print(f"正在输入Y坐标: {y}")
    for digit in str(y):
        # 查找对应的数字图片并点击
        for key_info in area:
            if key_info['name'] == digit:
                find_and_click_image(key_info['png'], confidence=0.98)
                time.sleep(1)  # 添加点击后的延迟
                break
    #点击确认按钮
    find_and_click_image('./keyboard/sure.png', confidence=0.85) 
    time.sleep(3) 
    print("坐标输入完成")
    # 点击关闭地图按钮
    find_and_click_image('close.png', confidence=0.8)
    # 坐标输入完成后，启动自动寻路监听
    listen_for_navigation_coordinates()

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
    area_btn_location = None
    try:
        area_btn_location = pyautogui.locateOnScreen('./areabtn.png', confidence=0.6)
        print(f"areabtn.png位置: {area_btn_location}")
    except pyautogui.ImageNotFoundException:
        area_btn_location = None
        print("未找到areabtn.png")
    
    if area_btn_location:
        # 基于areabtn.png位置定义识别区域，稍微扩大一些范围以包含坐标文本
        target_region = (
            int(area_btn_location.left),
            int(area_btn_location.top),
            int(area_btn_location.width),
            int(area_btn_location.height)
        )
        print(f"基于areabtn.png定义的识别区域: {target_region}")
    else:
        print("没找到监听区域")
        return False  # 修改为返回False，表示未找到监听区域
    
    # 保存上一次识别的结果
    previous_result = None
    same_count = 0  # 连续相同结果计数器
    
    for i in range(20):  # 最多监听20次，约1分钟
        if not running:
            break
            
        try:
            # 截取指定区域
            screenshot = pyautogui.screenshot(region=target_region)
            temp_image = "temp_navigation_ocr.png"
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

# 新增函数：监听指定图片直到消失
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
        except pyautogui.ImageNotFoundException:
            # 图片不存在，说明已消失
            print(f"图片 {image_path} 已消失")
            return True
        except Exception as e:
            print(f"监听图片时出错: {e}")
            
        # 等待1秒后继续
        time.sleep(1)
    
    return False

# 主函数包含所有程序逻辑
def main_loop():
    error_count = 0  # 添加错误计数器
    max_errors = 10  # 最大连续错误次数
    # 定义图片内容
    global running, current_character_index  # 声明所有需要的全局变量
    window_title = "Phone-E6EDU20429087631" 
    while not stop_event.is_set():
        if running:
            # 根据右侧道具/行囊区域的图片，匹配到窗口内的区域获取到对应的匹配区域
            # 这里假设已经获取到窗口句柄hwnd和位置信息
            try:
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
                    
                x, y, width, height = get_window_position(hwnd)
                print(f"窗口位置: x={x}, y={y}, width={width}, height={height}")
                
                # 截取右侧道具/行囊区域
                right_region = pyautogui.screenshot(region=(x + width//2, y, width//2, height - 50))  # 假设右半部分为道具/行囊区域
                right_region.save(img_right)
                
                # 匹配道具栏
                prop_location = find_and_click_image(prop, confidence=0.8)
                print(f"道具栏位置: {prop_location}")
                treasure_found = False
                
                if prop_location:
                    # 检查道具栏是否存在藏宝图，限定在右侧区域
                    try:
                        treasure_in_prop = find_and_click_image(
                            img_content, 
                            confidence=0.6,  # 降低置信度以提高匹配成功率
                            region=(x + width//2, y, width//2, height - 50),
                            click=False
                        )
                        print(f"在道具栏中查找藏宝图结果: {treasure_in_prop}")
                    except pyautogui.ImageNotFoundException:
                        treasure_in_prop = None
                        print("未在道具栏中找到藏宝图")
                        
                    if treasure_in_prop:
                        # 道具栏存在藏宝图，返回所有可点击的藏宝图对象，限定在右侧区域
                        try:
                            treasure_locations = find_all_images(img_content, confidence=0.6, region=(x + width//2, y, width//2, height - 50))
                            # print(f"找到的藏宝图列表: {treasure_locations}")
                        except pyautogui.ImageNotFoundException:
                            treasure_locations = []
                        # print(f"在道具栏找到{len(treasure_locations)}个藏宝图")
                        # 点击第一个藏宝图后停止循环操作
                        if treasure_locations and running:
                            # 只点击第一个找到的藏宝图
                            first_treasure = treasure_locations[0]
                            pyautogui.click(first_treasure.left + first_treasure.width//2, first_treasure.top + first_treasure.height//2)
                            print("已点击第一个藏宝图，停止继续查找")
                            time.sleep(1)
                            treasure_found = True
                            # 点击藏宝图后进行OCR识别
                            print("正在进行藏宝图结果OCR识别...")
                            # 修改: 先匹配藏宝图结果区域，再进行OCR识别
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
                                find_and_click_image('close.png', confidence=0.8)
                                time.sleep(1)
                                # 点击界面左上角出现地图内容
                                print("正在点击areabtn.png...")
                                area_btn_result = find_and_click_image('./areabtn.png', confidence=0.6)
                                print(f"areabtn.png点击结果: {area_btn_result}")
                                if area_btn_result is None:
                                    print("警告: 未找到areabtn.png按钮")
                                    stop_script()
                                time.sleep(1)
                                # 点击x输入框，输入识别结果中的x坐标
                                print("正在点击xbtn.png...")
                                x_btn_result = find_and_click_image('xbtn.png', confidence=0.8)
                                print(f"xbtn.png点击结果: {x_btn_result}")
                                if x_btn_result is None:
                                    print("警告: 未找到xbtn.png按钮")
                                    stop_script()
                                # 新增: 输入坐标
                                if recognized_text:
                                    input_coordinates_via_keyboard(recognized_text)
                                # 识别键盘内容
                                # 修改: 调用监听函数并根据返回值决定是否停止脚本（坐标监听结束）
                                if listen_for_navigation_coordinates():
                                    # stop_script()
                                    time.sleep(1)
                                    result = find_and_click_image('tool.png', confidence=0.8)
                                    if result is None:
                                        print("警告: 未找到tool.png按钮")
                                    time.sleep(2)
                                    pyautogui.click(first_treasure.left + first_treasure.width//2, first_treasure.top + first_treasure.height//2)
                                    time.sleep(1)
                                    # 点击使用地图
                                    find_and_click_image('usermap.png', confidence=0.8)
                                    time.sleep(1)

                                    # 截取当前屏幕并保存到指定文件夹
                                    import os
                                    import datetime
                                    screenshot_folder = "screenshots"
                                    if not os.path.exists(screenshot_folder):
                                        os.makedirs(screenshot_folder)
                                    
                                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                    screenshot_path = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")
                                    # 修改为截取当前窗口而不是整个屏幕
                                    hwnd = find_window_by_title(window_title)
                                    if hwnd:
                                        x, y, width, height = get_window_position(hwnd)
                                        screenshot = pyautogui.screenshot(region=(x, y, width, height))
                                        screenshot.save(screenshot_path)
                                        print(f"窗口截图已保存至: {screenshot_path}")
                                    else:
                                        # 如果找不到窗口则截取全屏
                                        pyautogui.screenshot(screenshot_path)
                                        print(f"屏幕截图已保存至: {screenshot_path}")
                                    
                                    # 新增: 等待state\1.png图片消失
                                    if wait_for_image_to_disappear('./state/1.png', confidence=0.8):
                                        # 从头开始重新执行函数
                                        continue
                                    else:
                                        # 如果图片未消失或超时，继续执行
                                        continue
                            
                            else:
                                print("未找到藏宝图结果区域")
                                recognized_text = ""
                            # 点击藏宝图后停止脚本
                            print("已找到并点击藏宝图，脚本已停止2")
                            # stop_script()
                            continue
                            # break  # 跳出当前循环
                    else:
                        print("在道具栏中未找到藏宝图，尝试在全屏范围内查找")
                        # 如果在道具栏没找到，尝试在整个屏幕范围内查找
                        try:
                            all_treasures = find_all_images(img_content, confidence=0.6)
                            print(f"全屏找到的藏宝图列表: {all_treasures}")
                            if all_treasures:
                                first_treasure = all_treasures[0]
                                pyautogui.click(first_treasure.left + first_treasure.width//2, first_treasure.top + first_treasure.height//2)
                                print("已点击全屏找到的第一个藏宝图")
                                treasure_found = True
                        except pyautogui.ImageNotFoundException:
                            print("全屏未找到藏宝图")

                # 如果都没有找到藏宝图，则提示并停止脚本
                print(f"treasure_found状态: {treasure_found}")
                if not treasure_found:
                    show_alert("整理已经结束，未找到更多藏宝图")
                    stop_script()
                        
            except Exception as e:
                error_count += 1
                # 修改: 打印详细的异常信息
                print(f"发生错误: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()  # 打印完整的错误堆栈信息
                if error_count >= max_errors:
                    print("连续错误次数过多，脚本将停止")
                    show_alert("程序出现连续错误，脚本已停止")
                    stop_script()
                    break  # 修改: 确保在停止脚本后退出循环
                time.sleep(1)
                continue
        time.sleep(0.1)  # 避免CPU占用过高

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