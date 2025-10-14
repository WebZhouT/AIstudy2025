import os
import pyautogui
import time
import win32gui
import win32con
import cv2
import numpy as np
import keyboard
import threading
# 添加RapidOCR导入
from rapidocr_onnxruntime import RapidOCR
import json
import ctypes
from ctypes import wintypes

# 初始化 OCR 引擎
ocr = RapidOCR()

# 全局变量控制运行状态
running = False
stop_event = threading.Event()
# 定义角色名列表，按照优先级排序
# 手机1
userlist = ["依然爱你","兄弟情义无情","垃圾书铁到50","金创仓库123","50环仓库125","3J药品123","植物种子堆","变身卡仓11","鱼的仓库", "50J环仓库3", "50J环仓库41", "2药存放仓库3", "药材仓库234", "药材仓库12", "2J药材44", "10到40垃圾书", "50J的铁", "50J书仓库", "70级Tie", "垃圾书仓库", "社区装饰123","2J药仓库234", "暗器库19", "家具存放", "2J药仓库125", "仓库整", "0仓整2","50J的铁","家具存放123","宝石存放12","鱼的仓库","6070书铁仓库","2J药材料11","2J药仓库125","环装131","乐器花13","鱼的仓库2","社区装饰123","兽决仓库002", "1儿童用具", "珍珠阵法", "6070人造装", "50J环仓库2", "善本书匣子", "长寿图库", "麒麟图库", "五庄图转手", "女儿图书城", "傲来哦是", "朱紫啊国", "鱼的仓库2", "普陀山图", "烹饪啊才", "盒子多多1", "钨金1",]
# userlist = []
# 手机2
# userlist = ["heart","傻傻","残","妲己","兄弟情义无情","依然爱你","猪","小小"]
# 已经完成的角色名字
exitname=[]
# 当前操作的目标角色名字
aimData=''
# 当前匹配的角色索引
current_character_index = -1
# 窗口标题
window_title = "Phone-OBN7WS7D99EYFI49"
# window_title = "Phone-E6EDU20429087631"

# Windows API 相关定义
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# 定义常量
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001

# 预加载模板图像以提高匹配速度
template_cache = {}

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), 
                ("y", ctypes.c_long)]

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

def click_top_center(hwnd):
    """点击窗口上方中间位置"""
    x, y, width, height = get_window_position(hwnd)
    click_x = x + width // 2
    click_y = y + 20
    # 使用Windows API点击而不移动鼠标
    click_at_window_coord(hwnd, click_x, click_y)
    print(f"[click_top_center] 点击窗口顶部中心: ({click_x}, {click_y})")
    time.sleep(0.05)  # 进一步减少等待时间

def click_at_window_coord(hwnd, x, y):
    """在窗口坐标处点击，不移动鼠标"""
    # 将屏幕坐标转换为窗口客户区坐标
    point = (x, y)
    client_point = win32gui.ScreenToClient(hwnd, point)
    
    # 发送点击消息到窗口
    lParam = (client_point[1] << 16) | (client_point[0] & 0xFFFF)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

def drag_from_to_window(hwnd, start_x, start_y, end_x, end_y):
    """
    在窗口内从起始坐标拖拽到终止坐标，不移动鼠标
    """
    print(f"[drag_from_to_window] 执行拖拽操作: 从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
    
    # 转换起始点坐标为客户区坐标
    start_point = (start_x, start_y)
    client_start_point = win32gui.ScreenToClient(hwnd, start_point)
    
    # 转换终点坐标为客户区坐标
    end_point = (end_x, end_y)
    client_end_point = win32gui.ScreenToClient(hwnd, end_point)
    
    # 发送鼠标按下消息
    start_lParam = (client_start_point[1] << 16) | (client_start_point[0] & 0xFFFF)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, start_lParam)
    
    # 增加移动步数以使拖拽更平滑，减小滚动幅度
    steps = 30  # 从5增加到15，使拖拽更细致
    for i in range(steps + 1):
        intermediate_x = client_start_point[0] + (client_end_point[0] - client_start_point[0]) * i // steps
        intermediate_y = client_start_point[1] + (client_end_point[1] - client_start_point[1]) * i // steps
        intermediate_lParam = (intermediate_y << 16) | (intermediate_x & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, intermediate_lParam)
        time.sleep(0.01)  # 增加等待时间，从0.005增加到0.01
    
    # 发送鼠标抬起消息
    end_lParam = (client_end_point[1] << 16) | (client_end_point[0] & 0xFFFF)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, end_lParam)
    
    time.sleep(0.1)  # 增加等待时间，从0.05增加到0.1

def get_template_image(template_path):
    """获取模板图像，使用缓存提高性能"""
    if template_path not in template_cache:
        template = cv2.imread(template_path)
        if template is not None:
            template_cache[template_path] = template
        return template
    return template_cache[template_path]

def match_and_click_template(screenshot, template_path, threshold, region=None):
    """
    匹配模板并执行点击操作
    """
    try:
        # 读取模板图片（使用缓存）
        template = get_template_image(template_path)
        if template is None:
            print(f"[match_and_click_template] 警告: 无法读取模板图片 {template_path}")
            return False, None
            
        # 彩色匹配
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[match_and_click_template] 当前匹配度: {max_val:.2f} (阈值: {threshold})")
        
        if max_val >= threshold:
            h, w = template.shape[:2]
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
            
            print(f"[match_and_click_template] 匹配成功，点击坐标: ({center_x}, {center_y})")
            
            # 使用窗口消息方式点击，不移动鼠标
            hwnd = find_window_by_title(window_title)
            if hwnd:
                click_at_window_coord(hwnd, center_x, center_y)
                print(f"[match_and_click_template] 已通过窗口消息点击坐标: ({center_x}, {center_y})")
            time.sleep(0.03)  # 进一步减少等待时间
            
            return True, (center_x, center_y)
        else:
            print(f"[match_and_click_template] 匹配度不足阈值({threshold:.2f})")
            return False, None
            
    except Exception as e:
        print(f"[match_and_click_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def find_and_click_template(region, template_path, threshold, max_attempts=3):
    """在指定区域查找并点击模板，增加最大尝试次数参数"""
    for attempt in range(max_attempts):
        try:
            # 获取当前屏幕彩色截图
            screenshot = pyautogui.screenshot(region=region)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 进行模板匹配并点击
            matched, pos = match_and_click_template(screenshot_cv, template_path, threshold, region)
            
            if matched:
                return True
            elif attempt < max_attempts - 1:
                time.sleep(0.1)  # 短暂等待后重试
                
        except Exception as e:
            print(f"[find_and_click_template] 发生错误: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(0.1)
    
    return False

def find_drag_area_and_scroll(region, drag_area_template, character_names, threshold=0.7):
    """
    匹配拖拽区域并实现上下滚动功能
    """
    global aimData, current_character_index
    
    # 1. 匹配拖拽区域
    print("[find_drag_area_and_scroll] 开始匹配拖拽区域...")
    drag_area_matched = find_and_click_template(region, drag_area_template, threshold)
    
    if drag_area_matched:
        print("[find_drag_area_and_scroll] 成功匹配拖拽区域")
        
        # 2. 循环查找角色名
        max_scroll_attempts = 30  # 减少最大拖拽次数
        scroll_count = 0
        
        while scroll_count < max_scroll_attempts and not stop_event.is_set() and running:
            # 截取当前区域进行OCR识别
            try:
                # 截取整个窗口区域进行OCR
                screenshot = pyautogui.screenshot(region=region)
                screenshot_np = np.array(screenshot)
                
                # 使用RapidOCR识别文字
                ocr_result, _ = ocr(screenshot_np)
                
                # 检查是否有识别结果
                if ocr_result:
                    # 检查当前索引对应的角色名是否在识别结果中
                    if current_character_index < len(character_names):
                        current_character = character_names[current_character_index]
                        # 检查当前角色名是否在任一识别到的文本中
                        for text_info in ocr_result:
                            if len(text_info) > 1 and current_character in text_info[1]:
                                # 获取文字位置信息
                                box = text_info[0]
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
                                hwnd = find_window_by_title(window_title)
                                if hwnd:
                                    click_at_window_coord(hwnd, screen_x, screen_y)
                                # 找到目标角色并点击后，不再执行拖拽，直接返回
                                return True
                
                # 如果没有找到当前角色名，执行拖拽操作
                print(f"[find_drag_area_and_scroll] 未找到目标角色 {character_names[current_character_index] if current_character_index < len(character_names) else 'N/A'}，执行拖拽操作...")
                
                # 根据窗口区域计算拖拽起始和结束点，减小拖拽距离以减少滚动幅度
                x, y, w, h = region
                # 设置拖拽起始点（区域中部偏下）
                start_x = x + w // 2
                start_y = y + int(h * 0.75)  # 从0.7调整到0.75，减小起始点和终点的差距
                # 设置拖拽结束点（区域中部偏上）
                end_x = x + w // 2
                end_y = y + int(h * 0.55)  # 从0.65调整到0.7，减小起始点和终点的差距
                
                # 执行拖拽操作
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    drag_from_to_window(hwnd, start_x, start_y, end_x, end_y)
                time.sleep(0.5)  # 增加等待时间，从0.3增加到0.5
                scroll_count += 1
                
            except Exception as e:
                print(f"[find_drag_area_and_scroll] OCR识别出错: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # 即使OCR出错，也执行拖拽操作
                x, y, w, h = region
                start_x = x + w // 2
                start_y = y + int(h * 0.75)  # 从0.7调整到0.75
                end_x = x + w // 2
                end_y = y + int(h * 0.7)  # 从0.65调整到0.7
                
                # 执行拖拽操作
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    drag_from_to_window(hwnd, start_x, start_y, end_x, end_y)
                time.sleep(0.5)  # 增加等待时间，从0.3增加到0.5
                scroll_count += 1
        
        if scroll_count >= max_scroll_attempts:
            print("[find_drag_area_and_scroll] 已达到最大拖拽次数，未找到目标角色")
        
        return True
    else:
        print("[find_drag_area_and_scroll] 未匹配到拖拽区域")
        return False

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
def main_loop():
    """主循环函数"""
    global running, current_character_index
    # 设备1
    # 设备2
    template_path = "1.png"  # 今日礼包
    template_path2 = "2.png"  # 去签到
    close1 = "3.png"  # 今日礼包关闭
    more = "more.png"  # 更多按钮
    rolebtn = "4.png"  # 领奖角色按钮
    index = 0
    print(f"[主循环] 正在监听窗口: {window_title}")
    
    while not stop_event.is_set():
        if running:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                print(f"[主循环] 找到窗口句柄: {hwnd}")
                
                # 获取窗口区域
                region = get_window_position(hwnd)
                print(f"[主循环] 窗口区域: {region}")
                
                # 检查窗口是否最小化
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.03)
                
                # 激活窗口
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    pass
                
                if index == 0:
                    time.sleep(0.05)
                    # 点击窗口顶部激活窗口
                    click_top_center(hwnd)
                    index = 1
                
                # 循环查找第一个模板直到找到为止
                found_today_gift = False
                max_attempts = 10  # 设置最大尝试次数
                attempt_count = 0

                while not stop_event.is_set() and running and attempt_count < max_attempts:
                    success = find_and_click_template(region, template_path, 0.8, 2)  # 最多尝试2次
                    if success:
                        print("[主循环] 成功点击今日礼包")
                        time.sleep(1.5)  # 减少等待时间
                        found_today_gift = True
                        break
                    else:
                        print("[主循环] 未找到今日礼包，0.5秒后继续查找...")
                        time.sleep(0.5)  # 减少等待时间
                        attempt_count += 1

                # 只有在找到今日礼包的情况下才继续执行后续操作
                if not found_today_gift:
                    print("[主循环] 达到最大尝试次数仍未找到今日礼包，跳过本次循环")
                    continue
                
                # 如果脚本仍在运行，继续查找第二个对话模板去签到按钮点击
                if not stop_event.is_set() and running:
                    # 添加一个标志来控制是否需要重新开始主循环
                    restart_main_loop = False
                    success2 = find_and_click_template(region, template_path2, 0.7, 2)  # 最多尝试2次
                    if success2:
                        print("[主循环] 点击去签到按钮")
                        time.sleep(3)  # 减少等待时间
                    else:
                        print("[主循环] 未找到去签到按钮")
                        # 增加角色索引以匹配下一个角色
                        current_character_index += 1
                        
                        # 检查是否已经遍历完所有角色
                        if current_character_index >= len(userlist):
                            print("[主循环] 已遍历完所有角色，程序结束")
                            running = False
                            return
                        
                        # 未找到去签到按钮，就关闭今日礼包
                        find_and_click_template(region, close1, 0.8, 2)
                        time.sleep(0.5)
                        # 点击更多按钮
                        find_and_click_template(region, more, 0.8, 2)
                        time.sleep(0.5)
                        # 点击领奖角色按钮
                        find_and_click_template(region, rolebtn, 0.3, 2)
                        time.sleep(0.5)
                        # 处理拖拽区域
                        drag_area_template = "drag_area.png"
                        find_drag_area_and_scroll(region, drag_area_template, userlist, 0.3)
                        time.sleep(0.5)
                        # 点击领取奖励按钮
                        find_and_click_template(region, "5.png", 0.3, 2)
                        time.sleep(0.5)
                        # 处理完拖拽区域后，设置标志以重新开始主循环
                        restart_main_loop = True
                    
                    # 如果设置了重新开始主循环的标志，则跳过后续代码
                    if restart_main_loop:
                        continue
                
                # 点击出现的弹框奖励领取成功，开心收下
                success = find_and_click_template(region, './7.png', 0.8, 2)
                if success:
                    print("[主循环] 点击出现的弹框奖励领取成功，开心收下")
                    time.sleep(2)
                else:
                    print("[主循环] 未找到弹框奖励领取成功按钮")
                    time.sleep(1)
                
                # 点击去抽奖的按钮
                success = find_and_click_template(region, './6.png', 0.8, 2)
                if success:
                    print("[主循环] 点击去抽奖的按钮")
                    time.sleep(2)
                else:
                    print("[主循环] 未找到去抽奖按钮")
                    time.sleep(1)
                
                # 点击开心收下的按钮
                success = find_and_click_template(region, './7.png', 0.8, 2)
                if success:
                    print("[主循环] 点击开心收下的按钮")
                    
                    # 识别goods.png所在区域的文字并保存到日志文件
                    try:
                        hwnd = find_window_by_title(window_title)
                        
                        if hwnd:
                            window_region = get_window_position(hwnd)
                            
                            # 先截取整个窗口用于匹配goods.png
                            window_screenshot = pyautogui.screenshot(region=window_region)
                            
                            # 查找goods.png模板在窗口中的位置
                            goods_template_path = "goods.png"
                            template = get_template_image(goods_template_path)
                            if template is not None:
                                open_cv_image = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
                                
                                # 在窗口截图中匹配goods.png模板
                                res = cv2.matchTemplate(open_cv_image, template, cv2.TM_CCOEFF_NORMED)
                                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                                
                                threshold = 0.8
                                if max_val >= threshold:
                                    h, w = template.shape[:2]
                                    top_left = (window_region[0] + max_loc[0], window_region[1] + max_loc[1])
                                    
                                    # 截取匹配区域
                                    goods_region = (top_left[0], top_left[1], w, h)
                                    goods_screenshot = pyautogui.screenshot(region=goods_region)
                                    
                                    # 对截取的区域进行OCR识别
                                    img = cv2.cvtColor(np.array(goods_screenshot), cv2.COLOR_RGB2BGR)
                                    ocr_result, elapse = ocr(img)
                                    
                                    print("[主循环] goods.png区域OCR识别结果:")
                                    full_text = ""
                                    if ocr_result:
                                        recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
                                        full_text = "\n".join(recognized_texts)
                                        for line in recognized_texts:
                                            print(line)
                                    else:
                                        print("[主循环] 未识别到文字")
                                        full_text = "未识别到文本"
                                    
                                    # 获取当前时间戳
                                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                    
                                    # 创建日志条目
                                    log_entry = {
                                        "name": aimData,
                                        "result": full_text,
                                        "timestamp": timestamp
                                    }
                                    
                                    # 读取现有日志文件（如果存在）
                                    log_file = "result.json"
                                    logs = []
                                    if os.path.exists(log_file):
                                        try:
                                            with open(log_file, 'r', encoding='utf-8') as f:
                                                logs = json.load(f)
                                        except Exception as e:
                                            print(f"[主循环] 读取日志文件出错: {str(e)}")
                                    
                                    # 添加新条目
                                    logs.append(log_entry)
                                    
                                    # 保存到日志文件
                                    try:
                                        with open(log_file, 'w', encoding='utf-8') as f:
                                            json.dump(logs, f, ensure_ascii=False, indent=2)
                                        print(f"[主循环] 已保存奖励日志: {aimData}")
                                    except Exception as e:
                                        print(f"[主循环] 保存日志文件出错: {str(e)}")
                                else:
                                    print(f"[主循环] 未能在窗口中找到goods.png模板，最高匹配度: {max_val:.2f}")
                                    # 记录未匹配到模板的情况
                                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                    log_entry = {
                                        "name": aimData,
                                        "result": "未匹配到对应区域",
                                        "timestamp": timestamp
                                    }
                                    
                                    log_file = "result.json"
                                    logs = []
                                    if os.path.exists(log_file):
                                        try:
                                            with open(log_file, 'r', encoding='utf-8') as f:
                                                logs = json.load(f)
                                        except Exception as e:
                                            print(f"[主循环] 读取日志文件出错: {str(e)}")
                                    
                                    logs.append(log_entry)
                                    
                                    try:
                                        with open(log_file, 'w', encoding='utf-8') as f:
                                            json.dump(logs, f, ensure_ascii=False, indent=2)
                                        print(f"[主循环] 已保存奖励日志: {aimData}")
                                    except Exception as e:
                                        print(f"[主循环] 保存日志文件出错: {str(e)}")
                            else:
                                print(f"[主循环] 无法读取模板图片 {goods_template_path}")
                        else:
                            print(f"[主循环] 未找到窗口: {window_title}")
                    except Exception as e:
                        print(f"[主循环] goods.png区域文字识别出错: {str(e)}")
                        import traceback
                        traceback.print_exc()
                    
                    time.sleep(0.3)
                
                print("[主循环] 等待下一次扫描...")
            else:
                print("[主循环] 未找到窗口")
            
            # 等待时间减少到2秒
            for i in range(10, 0, -1):
                if not running or stop_event.is_set():
                    break
                print(f"\r[主循环] 下次扫描倒计时: {i/10:.1f}秒", end="", flush=True)
                time.sleep(0.1)
            print("\r" + " " * 30, end="\r")
        else:
            # 脚本停止状态，检查间隔减少
            time.sleep(0.05)

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
    finally:
        stop_event.set()
        keyboard.unhook_all()

if __name__ == "__main__":
    main()
