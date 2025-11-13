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
import mss
import mss.tools
# 初始化 OCR 引擎
ocr = RapidOCR()

# 全局变量控制运行状态
running = False
stop_event = threading.Event()
# 定义角色名列表，按照优先级排序
# 手机1
userlist = [ "尹天雪",  "兄弟情义无情", "垃圾书铁到50", "金创仓库123", "50环仓库125", "药品123", "植物种子堆","变身卡仓库11","仓存整", "变身卡仓11", "鱼的仓库", "环仓库3", "环仓库41", "2药存放仓库3", "药材仓库234", "药材仓库12", "药材44", "10到40垃圾书", "的铁", "书仓库", "70级Tie", "垃圾书仓库", "社区装饰123", "药仓库234", "暗器库19", "家具存放002", "药仓库125", "仓库整", "0仓整2", "家具存放123", "宝石存放12", "6070书铁仓库", "药材料11", "环装131", "乐器花13", "普陀山图", "烹饪啊才", "盒子多多1", "钨金1", "兽决仓库002", "1儿童用具","珍珠阵法", "6070人造装", "50J环仓库2", "善本书匣子", "长寿图库", "麒麟图库", "五庄图转手", "女儿图书城", "傲来哦是", "朱紫啊国", "50J环仓库3", "50J环仓库41", "2J药材44", "50J的铁", "50J书仓库", "2J药仓库234", "2J药仓库125"]
# 手机2
# userlist = ['鱼的仓库2','cbt2','扔垃圾','金创344',"尹天奇", '星河','青灯','沁春','夏沫','染秋','冬','四季','天雪','蒂娜','残枫','断弦天奇','妙手摘星','嘻哈玩命','师驼岭杀手','兄弟情义感觉','芊','含烟','佑手','不详','众人']
# 
# 已经完成的角色名字
exitname=[]
# 当前操作的目标角色名字
aimData=''
# 当前匹配的角色索引
current_character_index = -1
# 窗口标题
window_title = "Phone-OBN7WS7D99EYFI49"
# window_title = "Phone-E6EDU20429087631"
# window_title = "Phone-192.168.0.106:5555"

# Windows API 相关定义
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# 定义常量
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001

# 预加载模板图像以提高匹配速度
template_cache = {}

# 需要彩色匹配的模板列表
color_templates = ["goods.png"]  # 可以根据需要添加其他需要彩色匹配的模板

def get_screenshot_virtual_desktop(region=None):
    """
    使用虚拟桌面坐标截图，支持多显示器
    region: (left, top, width, height) 基于虚拟桌面的坐标
    """
    with mss.mss() as sct:
        # 监控器0代表整个虚拟桌面
        if region:
            monitor = {
                "left": region[0],
                "top": region[1], 
                "width": region[2],
                "height": region[3]
            }
        else:
            # 截取整个虚拟桌面
            monitor = sct.monitors[0]
        
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

def get_window_region_virtual(hwnd):
    """
    获取窗口在虚拟桌面中的区域
    返回: (left, top, width, height)
    """
    try:
        # 获取窗口在虚拟桌面中的位置
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        return (x, y, width, height)
    except Exception as e:
        print(f"获取窗口区域失败: {e}")
        return None

def click_at_virtual_coord(hwnd, virtual_x, virtual_y):
    """
    在虚拟桌面坐标处点击
    """
    try:
        # 将虚拟桌面坐标转换为窗口客户区坐标
        point = (virtual_x, virtual_y)
        client_point = win32gui.ScreenToClient(hwnd, point)
        
        # 发送点击消息
        lParam = (client_point[1] << 16) | (client_point[0] & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        
        print(f"[click_at_virtual_coord] 点击虚拟坐标: ({virtual_x}, {virtual_y})")
        return True
    except Exception as e:
        print(f"点击虚拟坐标失败: {e}")
        return False

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

def drag_in_virtual_coords(hwnd, start_x, start_y, end_x, end_y):
    """
    在虚拟桌面坐标中执行拖拽
    """
    try:
        print(f"[drag_in_virtual_coords] 虚拟坐标拖拽: 从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
        
        # 转换起始点坐标
        start_point = (start_x, start_y)
        client_start_point = win32gui.ScreenToClient(hwnd, start_point)
        
        # 转换终点坐标
        end_point = (end_x, end_y)
        client_end_point = win32gui.ScreenToClient(hwnd, end_point)
        
        # 发送鼠标按下消息
        start_lParam = (client_start_point[1] << 16) | (client_start_point[0] & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, start_lParam)
        
        # 移动步骤
        steps = 20
        for i in range(steps + 1):
            intermediate_x = client_start_point[0] + (client_end_point[0] - client_start_point[0]) * i // steps
            intermediate_y = client_start_point[1] + (client_end_point[1] - client_start_point[1]) * i // steps
            intermediate_lParam = (intermediate_y << 16) | (intermediate_x & 0xFFFF)
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, intermediate_lParam)
            time.sleep(0.01)
        
        # 发送鼠标抬起消息
        end_lParam = (client_end_point[1] << 16) | (client_end_point[0] & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, end_lParam)
        
        time.sleep(0.1)
        return True
    except Exception as e:
        print(f"虚拟坐标拖拽失败: {e}")
        return False

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
    匹配模板并执行点击操作（使用虚拟坐标）
    支持多尺度模板匹配以适应不同窗口大小
    """
    try:
        # 获取缓存的模板
        template = get_template_image(template_path)
        if template is None:
            print(f"[match_and_click_template] 警告: 无法读取模板图片 {template_path}")
            return False, None
        
        # 根据模板类型决定匹配方式
        if template_path in color_templates:
            # 彩色匹配
            if len(screenshot.shape) == 3:  # 截图已经是彩色
                screenshot_for_match = screenshot
            else:  # 截图是灰度，需要转换为彩色
                screenshot_for_match = cv2.cvtColor(screenshot, cv2.COLOR_GRAY2BGR)
            match_type = "彩色"
        else:
            # 灰度匹配
            if len(screenshot.shape) == 3:  # 截图是彩色，转换为灰度
                screenshot_for_match = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            else:  # 截图已经是灰度
                screenshot_for_match = screenshot
            
            # 如果模板是彩色的，转换为灰度
            if len(template.shape) == 3:
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            else:
                template_gray = template
            match_type = "灰度"
        
        # 多尺度模板匹配
        found = None
        best_scale = 1.0
        
        # 定义缩放比例范围，适应窗口大小的变化
        scales = [1.0]
        
        for scale in scales:
            # 根据当前缩放比例调整模板大小
            if match_type == "彩色":
                resized_template = cv2.resize(template, (
                    int(template.shape[1] * scale), 
                    int(template.shape[0] * scale)
                ))
            else:
                resized_template = cv2.resize(template_gray, (
                    int(template_gray.shape[1] * scale), 
                    int(template_gray.shape[0] * scale)
                ))
            
            # 如果调整后的模板比截图还大，跳过这个比例
            if (resized_template.shape[0] > screenshot_for_match.shape[0] or 
                resized_template.shape[1] > screenshot_for_match.shape[1]):
                continue
            
            # 执行模板匹配
            if match_type == "彩色":
                res = cv2.matchTemplate(screenshot_for_match, resized_template, cv2.TM_CCOEFF_NORMED)
            else:
                res = cv2.matchTemplate(screenshot_for_match, resized_template, cv2.TM_CCOEFF_NORMED)
            
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            # 如果找到更好的匹配，更新结果
            if found is None or max_val > found[0]:
                found = (max_val, max_loc, scale, resized_template.shape)
        
        if found is not None:
            max_val, max_loc, best_scale, template_shape = found
            
            # 打印匹配信息
            print(f"[match_and_click_template] {match_type}匹配度: {max_val:.2f} (阈值: {threshold}, 缩放比例: {best_scale:.2f})")
            
            if max_val >= threshold:
                w, h = template_shape[1], template_shape[0]
                x, y = max_loc
                
                if region:
                    # 计算模板中心点相对于虚拟桌面的坐标
                    center_x = region[0] + x + w // 2
                    center_y = region[1] + y + h // 2
                    
                    # 验证坐标是否在区域内
                    if not (region[0] <= center_x <= region[0] + region[2] and 
                            region[1] <= center_y <= region[1] + region[3]):
                        print(f"[match_and_click_template] 警告: 计算坐标({center_x},{center_y})超出区域{region}")
                else:
                    center_x = x + w // 2
                    center_y = y + h // 2
                
                print(f"[match_and_click_template] 匹配成功，点击虚拟坐标: ({center_x}, {center_y})")
                
                # 使用虚拟坐标点击
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    click_at_virtual_coord(hwnd, center_x, center_y)
                    print(f"[match_and_click_template] 已通过窗口消息点击虚拟坐标: ({center_x}, {center_y})")
                time.sleep(0.03)
                
                return True, (center_x, center_y)
            else:
                print(f"[match_and_click_template] 所有缩放比例下匹配度均不足阈值({threshold:.2f})")
                return False, None
        else:
            print(f"[match_and_click_template] 在所有缩放比例下均未找到匹配")
            return False, None
            
    except Exception as e:
        print(f"[match_and_click_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None
def find_and_click_template(region, template_path, threshold, max_attempts=3):
    """在指定区域查找并点击模板"""
    for attempt in range(max_attempts):
        try:
            # 使用虚拟桌面坐标截图
            screenshot_cv = get_screenshot_virtual_desktop(region)
            
            # 进行模板匹配
            matched, pos = match_and_click_template(screenshot_cv, template_path, threshold, region)
            
            if matched:
                return True
            elif attempt < max_attempts - 1:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"[find_and_click_template] 发生错误: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(0.1)
    
    return False

def find_drag_area_and_scroll(region, drag_area_template, character_names, threshold=0.7):
    """
    匹配拖拽区域并实现上下滚动功能（使用虚拟坐标）
    通过比较列表内容区域判断是否到达边界
    """
    global aimData, current_character_index
    
    # 1. 匹配拖拽区域
    print("[find_drag_area_and_scroll] 开始匹配拖拽区域...")
    drag_area_matched = find_and_click_template(region, drag_area_template, threshold)
    
    if drag_area_matched:
        print("[find_drag_area_and_scroll] 成功匹配拖拽区域")
        
        # 定义列表内容区域（假设列表占据窗口中间部分）
        x, y, w, h = region
        # 列表区域：从窗口顶部向下20%开始，到窗口底部向上20%结束
        list_region = (x, y + int(h * 0.2), w, int(h * 0.6))
        
        # 新增变量用于检测是否到达边界
        last_list_screenshot = None  # 上一次的列表区域截图
        consecutive_same_count = 0  # 连续相同次数
        max_consecutive_same = 2  # 连续相同多少次后反向
        scroll_direction = "down"  # 初始滚动方向：向下
        
        # 2. 循环查找角色名
        max_scroll_attempts = 50  # 增加最大尝试次数，因为可能需要来回滚动
        scroll_count = 0
        
        while scroll_count < max_scroll_attempts and not stop_event.is_set() and running:
            # 截取当前区域进行OCR识别
            try:
                # 截取整个窗口区域进行OCR
                screenshot_np = get_screenshot_virtual_desktop(region)
                
                # 截取列表区域用于比较
                list_screenshot_np = get_screenshot_virtual_desktop(list_region)
                
                # 检查列表区域截图是否与上一次相同（判断是否到达边界）
                if last_list_screenshot is not None:
                    # 计算两张截图的差异
                    if last_list_screenshot.shape == list_screenshot_np.shape:
                        # 转换为灰度图进行比较
                        if len(last_list_screenshot.shape) == 3:
                            last_gray = cv2.cvtColor(last_list_screenshot, cv2.COLOR_BGR2GRAY)
                            current_gray = cv2.cvtColor(list_screenshot_np, cv2.COLOR_BGR2GRAY)
                        else:
                            last_gray = last_list_screenshot
                            current_gray = list_screenshot_np
                        
                        # 使用OpenCV计算图像差异
                        diff = cv2.absdiff(last_gray, current_gray)
                        mean_diff = np.mean(diff)
                        
                        # 如果差异很小，认为截图相同
                        # 调整阈值，因为列表区域变化应该比整个窗口更明显
                        if mean_diff < 1:  # 增加阈值到10
                            consecutive_same_count += 1
                            print(f"[find_drag_area_and_scroll] 连续第 {consecutive_same_count} 次列表区域几乎相同 (平均差异: {mean_diff:.2f})")
                        else:
                            consecutive_same_count = 0
                            print(f"[find_drag_area_and_scroll] 列表区域发生变化，平均差异: {mean_diff:.2f}")
                    else:
                        consecutive_same_count = 0
                        print(f"[find_drag_area_and_scroll] 截图尺寸发生变化，重置比较")
                
                # 保存当前列表区域截图用于下次比较
                last_list_screenshot = list_screenshot_np.copy()
                
                # 如果连续相同次数达到阈值，改变滚动方向
                if consecutive_same_count >= max_consecutive_same:
                    # if scroll_direction == "down":
                    #     scroll_direction = "up"
                    #     print("[find_drag_area_and_scroll] 检测到底部，改变滚动方向为向上")
                    # else:
                    scroll_direction = "down"
                    #     print("[find_drag_area_and_scroll] 检测到顶部，改变滚动方向为向下")
                    
                    consecutive_same_count = 0  # 重置计数
                    # 改变方向后立即执行一次拖拽
                    x, y, w, h = region
                    start_x = x + w // 2
                    end_x = x + w // 2
                    
                    if scroll_direction == "down":
                        # 向下滚动：从底部向上拖动（内容向下移动）
                        start_y = y + int(h * 0.65)
                        end_y = y + int(h * 0.55)
                    else:
                        # 向上滚动：从顶部向下拖动（内容向上移动）
                        start_y = y + int(h * 0.55)
                        end_y = y + int(h * 0.65)
                    
                    print(f"[find_drag_area_and_scroll] 改变方向后立即拖拽: 从({start_x}, {start_y})到({end_x}, {end_y})")
                    
                    # 执行虚拟坐标拖拽
                    hwnd = find_window_by_title(window_title)
                    if hwnd:
                        drag_in_virtual_coords(hwnd, start_x, start_y, end_x, end_y)
                    time.sleep(0.5)
                    scroll_count += 1
                    
                    # 跳过本次循环的剩余部分，直接进入下一次循环
                    continue
                
                # 使用RapidOCR识别文字
                ocr_result, _ = ocr(screenshot_np)
                
                # 检查是否有识别结果
                if ocr_result:
                    if current_character_index < len(character_names):
                        current_character = character_names[current_character_index]
                        found_character = False
                        for text_info in ocr_result:
                            if len(text_info) > 1 and current_character in text_info[1]:
                                box = text_info[0]
                                x_coords = [point[0] for point in box]
                                y_coords = [point[1] for point in box]
                                center_x = sum(x_coords) / len(x_coords)
                                center_y = sum(y_coords) / len(y_coords)
                                
                                # 转换为虚拟桌面坐标
                                screen_x = region[0] + int(center_x)
                                screen_y = region[1] + int(center_y)
                                
                                print(f"[find_drag_area_and_scroll] 找到角色 {current_character}，点击虚拟坐标: ({screen_x}, {screen_y})")
                                aimData = current_character
                                
                                # 使用虚拟坐标点击
                                hwnd = find_window_by_title(window_title)
                                if hwnd:
                                    click_at_virtual_coord(hwnd, screen_x, screen_y)
                                found_character = True
                                return True
                        
                        # 如果找到了其他角色但没有找到目标角色，继续滚动
                        if not found_character and ocr_result:
                            print(f"[find_drag_area_and_scroll] 当前屏幕有其他角色，但没有找到目标角色 {current_character}")
                
                # 如果没有找到当前角色名，执行拖拽操作
                print(f"[find_drag_area_and_scroll] 未找到目标角色 {current_character}，执行{scroll_direction}方向拖拽操作...")
                
                # 使用虚拟坐标计算拖拽点
                x, y, w, h = region
                start_x = x + w // 2
                end_x = x + w // 2
                
                if scroll_direction == "down":
                    # 向下滚动：从底部向上拖动（内容向下移动）
                    start_y = y + int(h * 0.65)
                    end_y = y + int(h * 0.55)
                else:
                    # 向上滚动：从顶部向下拖动（内容向上移动）
                    start_y = y + int(h * 0.55)
                    end_y = y + int(h * 0.65)
                
                print(f"[find_drag_area_and_scroll] 拖拽: 从({start_x}, {start_y})到({end_x}, {end_y})")
                
                # 执行虚拟坐标拖拽
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    drag_in_virtual_coords(hwnd, start_x, start_y, end_x, end_y)
                time.sleep(0.5)
                scroll_count += 1
                
            except Exception as e:
                print(f"[find_drag_area_and_scroll] 处理过程中出错: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # 即使出错，也执行拖拽操作（默认向下）
                x, y, w, h = region
                start_x = x + w // 2
                start_y = y + int(h * 0.65)
                end_x = x + w // 2
                end_y = y + int(h * 0.55)
                
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    drag_in_virtual_coords(hwnd, start_x, start_y, end_x, end_y)
                time.sleep(0.5)
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
                    success = find_and_click_template(region, template_path, 0.7, 2)  # 最多尝试2次
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
                    success2 = find_and_click_template(region, "2.png", 0.7, 1)  # 最多尝试2次
                    if success2:
                        print("[主循环] 点击去签到按钮")
                        time.sleep(3)  # 减少等待时间
                        # 点击开心收下的按钮
                        success = find_and_click_template(region, './7.png', 0.7, 2)
                        time.sleep(3)
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
                        find_and_click_template(region, close1, 0.6, 2)
                        time.sleep(1)
                        # # 未找到的话就再次尝试点击今日礼包
                        # find_and_click_template(region, template_path, 0.7, 2)
                        # print("[主循环] 未找到的话就再次尝试点击今日礼包")
                        # time.sleep(2)
                        # 点击更多按钮
                        find_and_click_template(region, more, 0.7, 2)
                        print("[主循环] 点击更多按钮")
                        time.sleep(3)
                        # 点击领奖角色按钮
                        find_and_click_template(region, rolebtn, 0.7, 2)
                        print("[主循环] 点击领奖角色按钮")
                        time.sleep(0.5)
                        # 处理拖拽区域
                        drag_area_template = "drag_area.png"
                        find_drag_area_and_scroll(region, drag_area_template, userlist, 0.3)
                        time.sleep(0.5)
                        print("[主循环] 处理拖拽区域")
                        # 点击领取奖励按钮
                        find_and_click_template(region, "5.png", 0.7, 2)
                        time.sleep(0.5)
                        print("[主循环] 点击领取奖励按钮")
                        # 点击出现的弹框奖励领取成功，开心收下
                        success = find_and_click_template(region, './7.png', 0.7, 2)
                        if success:
                            print("[主循环] 点击出现的弹框奖励领取成功，开心收下")
                            time.sleep(2)
                        else:
                            print("[主循环] 未找到弹框奖励领取成功按钮")
                            time.sleep(1)
                        # 处理完拖拽区域后，设置标志以重新开始主循环
                        restart_main_loop = True
                        
                        # 如果设置了重新开始主循环的标志，则跳过后续代码
                        if restart_main_loop:
                            continue
                # 点击去抽奖的按钮
                success = find_and_click_template(region, './6.png', 0.7, 2)
                if success:
                    print("[主循环] 点击去抽奖的按钮")
                    time.sleep(2)
                else:
                    print("[主循环] 未找到去抽奖按钮")
                    time.sleep(1)
                
                # 点击开心收下的按钮
                success = find_and_click_template(region, './7.png', 0.7, 2)
                if success:
                    print("[主循环] 点击开心收下的按钮")
                    
                    # 识别goods.png所在区域的文字并保存到日志文件
                    try:
                        hwnd = find_window_by_title(window_title)
                        
                        if hwnd:
                            window_region = get_window_position(hwnd)
                            
                            # 先截取整个窗口用于匹配goods.png
                            window_screenshot_np = get_screenshot_virtual_desktop(window_region)
                            
                            # 查找goods.png模板在窗口中的位置
                            goods_template_path = "goods.png"
                            template = get_template_image(goods_template_path)
                            if template is not None:
                                open_cv_image = window_screenshot_np
                                
                                # 在窗口截图中匹配goods.png模板
                                res = cv2.matchTemplate(open_cv_image, template, cv2.TM_CCOEFF_NORMED)
                                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                                
                                threshold = 0.5
                                if max_val >= threshold:
                                    h, w = template.shape[:2]
                                    top_left = (window_region[0] + max_loc[0], window_region[1] + max_loc[1])
                                    
                                    # 截取匹配区域
                                    goods_region = (top_left[0], top_left[1], w, h)
                                    goods_screenshot_np = get_screenshot_virtual_desktop(goods_region)
                                    
                                    # 对截取的区域进行OCR识别
                                    img = goods_screenshot_np
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