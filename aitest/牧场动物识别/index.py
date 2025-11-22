import cv2
import numpy as np
import pyautogui
import time
from PIL import ImageGrab
import threading
import os
import json
from datetime import datetime
import win32gui
import win32con
import datetime
# 图像识别
from rapidocr_onnxruntime import RapidOCR
import keyboard
import traceback
import ctypes  # 用于系统弹窗
# 导入自定义的图像工具模块
from image_utils import find_and_click_image, click_at_window_coord, mark_and_save_screenshot
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 鼠标拖拽指定区域识别文字
from drag_scroll import find_drag_area_and_scroll
# 匹配指定窗口内的图片信息区域，进行ocr识别返回文字
from get_picture_ocrTxt import get_ocr_text_from_template
# 分析牧场动物信息
from pasture_animal_parser import get_all_pasture_animals
# 在你的主循环中添加
from role_selector import cycle_select_roles, roleList
# 等待指定图片出现后执行
from wait_utils import wait_for_image, wait_for_image_disappear, wait_for_multiple_images, wait_for_condition
from breeding.index import animal_breeding
from recognize_simple_target import aim,recognize_simple_target
# 在文件开头添加全局变量
running = False
stop_event = threading.Event()
hwnd = find_window_by_title(window_title)
# 动物识别
class AnimalRecognizer:
    def __init__(self, window_title, confidence_threshold=0.8,):
        self.window_title = window_title
        self.confidence_threshold = confidence_threshold
        self.templates = {}  # 存储模板和相关信息
        self.is_running = False
    def find_window_by_title(self, title):
        """根据窗口标题查找窗口句柄"""
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
                hwnds.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None

    def get_window_position(self, hwnd):
        """获取窗口位置和大小"""
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        return x, y, width, height

    
    def load_animal_templates_from_json(self, json_file_path):
        """
        从JSON文件加载动物模板配置
        json_file_path: JSON配置文件路径
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                animals_config = json.load(f)
            
            for animal_data in animals_config.get('animals', []):
                name = animal_data['name']
                image_paths = animal_data['image_paths']
                click_priority = animal_data.get('click_priority', 1)
                color = tuple(animal_data.get('color', [0, 255, 0]))  # 默认绿色
                
                # 添加动物类型信息，用于优先级排序
                animal_type = animal_data.get('type', '其他')
                
                if name not in self.templates:
                    self.templates[name] = {
                        'images': [],
                        'click_priority': click_priority,
                        'last_click_time': 0,
                        'click_cooldown': animal_data.get('click_cooldown', 1.0),
                        'color': color,
                        'template_size': None,
                        'type': animal_type  # 添加类型信息
                    }
                
                for path in image_paths:
                    template = cv2.imread(path, 0)  # 以灰度模式读取
                    if template is not None:
                        self.templates[name]['images'].append(template)
                        if self.templates[name]['template_size'] is None:
                            self.templates[name]['template_size'] = template.shape[::-1]  # (宽, 高)
                
                print(f"已为动物 '{name}' 添加 {len(self.templates[name]['images'])} 个模板")
                
        except FileNotFoundError:
            print(f"错误: 找不到配置文件 {json_file_path}")
        except json.JSONDecodeError:
            print(f"错误: 配置文件 {json_file_path} 格式不正确")
        except Exception as e:
            print(f"加载配置文件时出错: {e}")

    def capture_screen(self):
        """捕获窗口区域屏幕"""
        hwnd = self.find_window_by_title(self.window_title)
        if not hwnd:
            print(f"未找到窗口: {self.window_title}")
            return None
            
        # 检查窗口是否最小化
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
        
        # 获取窗口区域
        x, y, width, height = self.get_window_position(hwnd)
        region = (x, y, x + width, y + height)
        
        # 截取窗口区域
        screenshot = ImageGrab.grab(bbox=region)
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        return screenshot
    
    def find_animals(self, screen_image):
        """在屏幕图像中查找所有动物"""
        if screen_image is None:
            return []
            
        gray_screen = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
        found_animals = []
        
        for name, template_data in self.templates.items():
            for template in template_data['images']:
                # 模板匹配
                result = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= self.confidence_threshold)
                
                # 处理匹配结果
                for pt in zip(*locations[::-1]):  # 交换columns和rows
                    # 获取匹配区域的中心点
                    center_x = pt[0] + template.shape[1] // 2
                    center_y = pt[1] + template.shape[0] // 2
                    
                    # 检查是否已经找到相近位置的同一动物（避免重复检测）
                    is_duplicate = False
                    for existing in found_animals:
                        dist = np.sqrt((center_x - existing['x'])**2 + (center_y - existing['y'])**2)
                        if dist < 20:  # 如果两个点距离小于20像素，认为是同一个动物
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        found_animals.append({
                            'name': name,
                            'x': center_x,
                            'y': center_y,
                            'confidence': result[pt[1], pt[0]],
                            'priority': template_data['click_priority'],
                            'last_click_time': template_data['last_click_time'],
                            'template_w': template.shape[1],
                            'template_h': template.shape[0],
                            'pt_x': pt[0],
                            'pt_y': pt[1],
                            'color': template_data['color']
                        })
        
        return found_animals

    
    def click_animal(self, animal):
        global hwnd
        """点击动物"""
        current_time = time.time()
        # 检查冷却时间
        if current_time - animal['last_click_time'] < self.templates[animal['name']]['click_cooldown']:
            return False
        
        # 查找窗口句柄以获取准确位置
        hwnd = self.find_window_by_title(self.window_title)
        if not hwnd:
            return False
            
        # 获取窗口位置
        x, y, width, height = self.get_window_position(hwnd)
        
        # 计算实际点击位置（相对于屏幕）
        click_x = x + animal['x']
        click_y = y + animal['y']
        
        # 移动鼠标并点击
        pyautogui.moveTo(click_x, click_y, duration=0.1)
        click_at_window_coord(hwnd,click_x, click_y)
        
        # 更新最后点击时间
        self.templates[animal['name']]['last_click_time'] = current_time
        animal['last_click_time'] = current_time
        
        print(f"点击了 {animal['name']} 在位置 ({click_x}, {click_y}) 相似度: {animal['confidence']:.2f}")
        return True
    
    def process_frame(self, save_screenshot=True):
        """处理一帧"""
        screen = self.capture_screen()
        animals = self.find_animals(screen)
        
        # 保存标记的截图
        if save_screenshot and animals:
            screenshot_path = self.mark_and_save_screenshot(screen, animals)
            if screenshot_path:
                print(f"已保存标记截图: {screenshot_path}")
        
        # 定义动物类型优先级：珍惜动物 > 哺乳动物 > 禽鸟动物 > 其他
        type_priority = {
            '珍惜动物': 0,
            '哺乳动物': 1,
            '禽鸟动物': 2,
            '其他': 3
        }
        
        # 按类型优先级和配置优先级排序
        animals.sort(key=lambda x: (type_priority.get(x['type'], 3), x['priority']))
        
        # 点击找到的动物
        for animal in animals:
            self.click_animal(animal)
            time.sleep(0.1)  # 点击间隔
            
        # 当没有识别出动物时执行第二条逻辑
        if not animals:
            self.process_secondary_logic(screen)

    def process_secondary_logic(self, screen):
        """
        处理没有识别到动物时的第二条逻辑
        可以在这里实现其他操作，例如：
        - 点击固定位置
        - 执行特定操作序列
        - 发送通知等
        """
        # 示例：打印提示信息
        print("未检测到动物，执行第二条逻辑")
        
        # 示例：可以在这里添加点击固定位置的逻辑
        # hwnd = self.find_window_by_title(self.window_title)
        # if hwnd:
        #     x, y, width, height = self.get_window_position(hwnd)
        #     # 点击窗口中心位置
        #     center_x = x + width // 2
        #     center_y = y + height // 2
        #     pyautogui.click(center_x, center_y)
        #     print(f"点击窗口中心位置: ({center_x}, {center_y})")
    
    def start(self, process_interval=0.5, save_screenshot=True):
        """开始识别和点击"""
        self.is_running = True
        
        def recognition_loop():
            while self.is_running:
                try:
                    self.process_frame(save_screenshot)
                    time.sleep(process_interval)
                except Exception as e:
                    print(f"处理过程中出现错误: {e}")
                    time.sleep(1)
        
        # 在单独线程中运行识别循环
        self.thread = threading.Thread(target=recognition_loop)
        self.thread.daemon = True
        self.thread.start()
        print("动物识别已启动")
    
    def stop(self):
        """停止识别"""
        self.is_running = False
        print("动物识别已停止")

""" ===================方法==================== """

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
""" 1.识别管理员操作（喂养，打扫，动物状态查看） """

def click_animal_manager():
    global hwnd
    """识别并点击管理员"""
    if running and not stop_event.is_set():
        print("正在识别管理员...")
        # 重试3次
        max_retries = 10
        retry_count = 0
        admin_position = None
        while running and not stop_event.is_set() and retry_count < max_retries and admin_position == None:
            admin_position = recognize_simple_target(aim)    
            if admin_position:
                print(f"找到管理员，位置: {admin_position}，相似度: {admin_position.get('confidence', 0):.2f}")
                hwnd = find_window_by_title(window_title)
                click_at_window_coord(hwnd,admin_position['x'], admin_position['y'])
                time.sleep(3)
                # 无论find_drag_area_and_scroll是否成功，我们都退出循环，因为已经点击了管理员
                # 第一次尝试执行牧场操作
                try:
                    success = execute_pasture_operations()
                    if success:
                        print("执行牧场操作成功")
                        return
                    else:
                        # 如果第一次没成功，也尝试偏移点击
                        raise Exception("第一次执行牧场操作失败")
                except Exception as e:
                    print(f"执行打开牧场界面时出错: {e}")
                    traceback.print_exc()  # 打印堆栈信息
                    # 找到了管理员但是点击没反应，那么就偏移20，进行点击，这个时候角色移动会靠近NPC的位置
                    print("尝试偏移点击靠近NPC...")
                    admin_position = recognize_simple_target(aim)
                    time.sleep(4)  # 增加等待时间，确保角色移动完成
                    # 再次点击管理员
                    print("再次点击管理员...")
                    click_at_window_coord(hwnd,int(admin_position['x']), int(admin_position['y']))
                    time.sleep(1)
                    # 重新执行牧场操作
                    try:
                        # 查找离开牧场选项
                        leave_coordinates = find_drag_area_and_scroll("./pasture/scroll.png", "离开牧场")
                        if leave_coordinates:
                            x, y = leave_coordinates
                            click_at_window_coord(hwnd,x, y)
                            time.sleep(1)
                            print("成功离开牧场")
                            # 点击设置按钮
                            find_and_click_image('./pasture/setting.png', confidence=0.65)
                            time.sleep(1)
                            # 点击退出游戏按钮
                            find_and_click_image('./pasture/quit.png', confidence=0.65)
                            time.sleep(1)
                            find_and_click_image('./pasture/sure.png', confidence=0.65)
                            time.sleep(1)
                        else:
                            print("未找到离开牧场选项")
                    except Exception as e2:
                        print(f"偏移点击后执行牧场操作仍然出错: {e2}")
                    return
            else:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"未找到管理员，第{retry_count}次重试，3秒后重试...")
                    # 点击弹框关闭按钮
                    find_and_click_image('./pasture/close.png', confidence=0.65)
                    time.sleep(3)
                else:
                    print("重试3次仍未找到管理员，停止程序")
                    show_alert("重试3次仍未找到管理员，程序已停止", use_toast=True)
                    stop_script()
                    return

# 定义一个函数出售老年动物
def deal_old_animals():
    global hwnd
    """识别并点击管理员"""
    if running and not stop_event.is_set():
        print("正在识别管理员...")
        # 重试3次
        max_retries = 10
        retry_count = 0
        admin_position = None
        x, y, width, height = get_window_position(hwnd)
        while running and not stop_event.is_set() and retry_count < max_retries and admin_position == None:
            admin_position = recognize_simple_target(aim)    
            if admin_position:
                print(f"找到管理员，位置: {admin_position}，相似度: {admin_position.get('confidence', 0):.2f}")
                hwnd = find_window_by_title(window_title)
                # 点击管理员
                click_at_window_coord(hwnd,admin_position['x'], admin_position['y'])
                time.sleep(0.5)
                # 点击出售动物和动物产品的按钮
                find_and_click_image('./sale_image/saleAnimalBtnle.png', confidence=0.65)
                time.sleep(0.5)
                # 点击确认按钮
                find_and_click_image('./sale_image/salebtn.png', confidence=0.65)
                # 文字识别滚动区域并出售老年动物
                from sale_elderly_animals import sell_elderly_animals
                sold_count = sell_elderly_animals('./sale_image/scroll3.png')
                print(f"成功出售 {sold_count} 只老年动物")
                # 点击关闭按钮
                find_and_click_image('./pasture/closearea.png', confidence=0.65)
                # 生成文件名并保存(调试图片)
                # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                # filename = os.path.join("debug_screenshots", f"multiple_matches_{timestamp}.png")
                # # 截取指定区域并保存图片到本地
                # screenshot = pyautogui.screenshot(region=(x, y, width, height))
                # os.makedirs(os.path.dirname(filename), exist_ok=True)
                # screenshot.save(filename)
                return
            else:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"未找到管理员，第{retry_count}次重试，3秒后重试...")
                    # 点击弹框关闭按钮
                    find_and_click_image('./pasture/close.png', confidence=0.65)
                    time.sleep(3)
                else:
                    print("重试3次仍未找到管理员，停止程序")
                    show_alert("重试3次仍未找到管理员，程序已停止", use_toast=True)
                    stop_script()
                    return
# 定义一个函数来执行打开牧场的操作，方便重复调用（点击管理员打开牧场界面）
def execute_pasture_operations():
    global hwnd
    coordinates = find_drag_area_and_scroll("./pasture/scroll.png", "打开牧场界面")
    if coordinates:
        x, y = coordinates
        # 后续可以点击这个坐标
        click_at_window_coord(hwnd,x, y)
        time.sleep(1)
        # 获取牧场状态（识别牧场饲料和牧场清洁度）
        pastureCondition = get_ocr_text_from_template('./pasture/pastureCondition.png',confidence=0.4, parse_type='pasture')
        if pastureCondition:
            print(f"牧场饲料数量: {pastureCondition.get('feed_amount', '未识别')}")
            print(f"牧场清洁度: {pastureCondition.get('cleanliness', '未识别')}")
            print(f"原始文本: {pastureCondition.get('raw_text', '无')}")
            
            # 修复清洁度判断逻辑
            cleanliness = pastureCondition.get('cleanliness')
            if cleanliness is not None and cleanliness != 100:
                print(f"清洁度不是100，需要清洁，当前清洁度为: {cleanliness}")
                # 点击牧场清洁度按钮去打扫卫生
                if find_and_click_image('./pasture/cleanbtn.png', confidence=0.65):
                    time.sleep(1)
                    # 整理牧场按钮
                    if find_and_click_image('./pasture/cleanbtn2.png', confidence=0.65):
                        time.sleep(1)
                        # 确定关闭对话框
                        find_and_click_image('./pasture/close.png', confidence=0.65)
                        print("关闭对话框操作完成")
                    else:
                        print("未找到关闭对话框按钮，跳过清洁")
                else:
                    print("未找到清洁按钮，跳过清洁")
            else:
                print(f"清洁度已经是{cleanliness}，无需清洁")
        else:
            print('未找到牧场状态信息')
        # 使用新的动物解析模块识别所有牧场动物的信息
        print("开始解析牧场动物信息...")
        all_animals_count = get_all_pasture_animals('./pasture/scroll2.png')
        time.sleep(3)
        if all_animals_count is not None:
            print(f"成功解析到 {all_animals_count} 个进入生育期的珍惜动物")
        else:
            print('未找到牧场动物信息或解析失败')
        # # 如果有显示关闭按钮，就点击关闭按钮
        find_and_click_image('./pasture/closearea.png', confidence=0.65)
        time.sleep(1)
        # 无论是否找到动物，都执行退出操作
        print('开始牧场繁殖流程')
        animal_breeding()
        print("开始退出牧场流程...")
        
        # 查找点击牧场管理人位置
        # 修改为与前面相同的重试机制，最多重试30次
        print("正在识别管理员...")
        # 管理员退出的时候重试次数识别
        max_retries = 30
        retry_count = 0
        admin_position = None
        while running and not stop_event.is_set() and retry_count < max_retries and admin_position is None:
            admin_position = recognize_simple_target(aim)    
            if not admin_position:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"未找到管理员，第{retry_count}次重试，3秒后重试...")
                    time.sleep(3)
                else:
                    print("重试30次仍未找到管理员，无法退出牧场")
                    show_alert("重试30次仍未找到管理员，无法退出牧场", use_toast=True)
                    break
            else:
                print(f"找到管理员111，位置: {admin_position}")
        
        time.sleep(2)
        if admin_position:
            # 点击管理人
            print(f"点击管理员122，位置: {admin_position}")
            click_at_window_coord(hwnd,admin_position['x'], admin_position['y'])
            time.sleep(1)
            # 查找离开牧场选项
            leave_coordinates = find_drag_area_and_scroll("./pasture/scroll.png", "离开牧场")
            if leave_coordinates:
                x, y = leave_coordinates
                click_at_window_coord(hwnd,x, y)
                time.sleep(1)
                print("成功离开牧场")
                # 点击设置按钮
                find_and_click_image('./pasture/setting.png', confidence=0.65)
                time.sleep(1)
                # 点击退出游戏按钮
                find_and_click_image('./pasture/quit.png', confidence=0.65)
                time.sleep(1)
                find_and_click_image('./pasture/sure.png', confidence=0.65)
                time.sleep(1)
            else:
                print("未找到离开牧场选项")
        else:
            print("多次尝试后仍未找到管理员，无法退出牧场")
        
        print("牧场操作流程完成")
        return True
    else:
        print("未找到牧场界面，请检查是否已打开牧场界面")
        return False




""" 2.动物识别点击 """
def animal_recognition_task():
    """动物识别任务 - 作为主循环中的第2个模块"""
    recognizer = AnimalRecognizer(
        window_title=window_title,
        confidence_threshold=0.8,
        screenshot_dir="detection_screenshots"
    )
    
    # 从JSON文件加载动物模板
    recognizer.load_animal_templates_from_json("animals_config.json")
    
    while running and not stop_event.is_set():
        try:
            recognizer.process_frame(save_screenshot=True)
            time.sleep(0.5)  # 处理间隔
        except Exception as e:
            print(f"动物识别错误: {e}")
            time.sleep(1)



def other_task_2():
    """其他任务2 - 示例"""
    if running and not stop_event.is_set():
        print("执行其他任务2...")
        # 这里添加你的其他操作逻辑

# 主函数
def main_loop():
    """主循环函数"""
    error_count = 0
    max_errors = 10
    global running, window_title  # 声明所有需要的全局变量
    # 重置所有状态变量
    loop_count = 0
    max_loop_count = 1  # 最大循环次数
    # 最大角色数量
    max_roles = len(roleList)
    global hwnd
    running = True
    while True:

        # # 先执行动物管理员相关操作
        if running and not stop_event.is_set():
            try:
                # 句柄窗口检测========================start===================
                # 查找游戏窗口
                hwnd = find_window_by_title(window_title)
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
                
                # 只有第一次循环才点击窗口顶部中间位置以获得焦点
                if loop_count == 0:
                    focus_window(x, y, width, height)
                if loop_count > max_loop_count:
                    print("达到最大循环次数，脚本将停止")
                    show_alert("脚本已达到最大循环次数，自动停止")
                    stop_script()
                    break
                # 句柄窗口检测========================end===================
                # 进入游戏前进行角色选择操作。
                print("开始角色选择操作...")
                print(f"开始选择第{loop_count + 1}个角色...")
                # 如果所有角色都处理完毕，停止脚本
                if loop_count >= max_roles:
                    print("所有角色都已处理完毕")
                    stop_script()
                else:
                    # 退出当前角色，回到选择界面
                    print("退出当前角色，回到选择界面...")
                    # 这里需要添加退出游戏的代码
                    # 例如：点击退出按钮等
                    time.sleep(2)
                success = cycle_select_roles(loop_count)
                if success:
                    print(f"角色选择成功，准备进入游戏...")
                    # # 等待角色加载进入游戏
                    time.sleep(1)
                    # # 新增: 增加循环计数
                    loop_count += 1
                    # 点击进入互通版按钮
                    find_and_click_image("./role_selector/enter_communication.png", confidence=0.65, region=(x, y, width, height))
                    time.sleep(6)
                    find_and_click_image("./role_selector/autoinput.png", confidence=0.6, region=(x, y, width, height))
                    # 等待指定图片出现后执行下面的代码
                    success_position = wait_for_image("./role_selector/into.png", confidence=0.12, region=(x, y, width, height), timeout=60)
                    # success_position = wait_for_multiple_images(['./role_selector/enter_communication_success.png','./role_selector/enter_communication_success1.png'], confidence=0.65)
                    if success_position:
                        print("成功进入互通版，继续执行后续操作")
                        # 这里添加进入游戏后的操作 
                        # 点击关闭按钮（在有广告的情况下）
                        time.sleep(1)
                        """ 签到答题种类1 """
                        find_and_click_image("./pasture/qiandaoClose.png", confidence=0.65, region=(x, y, width, height))
                        time.sleep(1)
                        # 如果存在答题每日签到的开关按钮，就点击关闭(这里有2种样式)
                        question = find_and_click_image("./pasture/signin1.png", confidence=0.65, region=(x, y, width, height))
                        if question:
                            time.sleep(1)
                            # 关闭答题签到
                            find_and_click_image("./pasture/signin1close.png", confidence=0.65, region=(x, y, width, height))
                        """ 签到答题种类2 """
                        find_and_click_image("./pasture/qiandaoClose.png", confidence=0.65, region=(x, y, width, height))
                        time.sleep(1)
                        # 如果存在答题每日签到的开关按钮，就点击关闭(这里有2种样式)
                        question2 = find_and_click_image("./pasture/signin2.png", confidence=0.65, region=(x, y, width, height))
                        if question2:
                            time.sleep(1)
                            # 关闭答题签到
                            find_and_click_image("./pasture/signin2close.png", confidence=0.65, region=(x, y, width, height))
                            time.sleep(1)
                            find_and_click_image("./pasture/signin2close.png", confidence=0.65, region=(x, y, width, height))
                        time.sleep(1)
                        # 点击车夫传送回家
                        find_and_click_image("./pasture/chefu.png", confidence=0.6, region=(x, y, width, height))
                        # 识别我要进入自己的牧场文字进行点击
                        # 获取打开牧场的坐标文字位置
                        time.sleep(1)
                        try:
                            openRanch  = find_drag_area_and_scroll("./pasture/gohome.png", "我要进入自己的牧场")
                            if openRanch:
                                x, y = openRanch
                                # 后续可以点击这个坐标
                                click_at_window_coord(hwnd,x, y)
                                time.sleep(2)
                                # 执行老年动物出售相关逻辑
                                deal_old_animals()
                                # # 执行牧场管理员养殖相关操作
                                click_animal_manager()
                            else:
                                print("未找到打开牧场界面，停止脚本")
                        except Exception as e:
                            print(f"调用find_drag_area_and_scroll时出错: {e}")
                            traceback.print_exc()
                    else:
                        print("进入互通版失败，停止脚本")
                        stop_script()
                        return

                    # print("已完成，执行下面的内容")
                    
                    # 这里可以添加其他游戏内操作
                else:
                    print("角色选择失败")
                # 写这里
                print("已完成，执行下面的内容")
                # stop_script()
                # # 执行动物识别
                # animal_recognition_task()
                # time.sleep(0.1)
                
                # other_task_2()
                # time.sleep(0.1)
                # click_animal_manager()

                stop_script()
                error_count = 0  # 重置错误计数
                
            except Exception as e:
                error_count += 1
                print(f"主循环错误 ({error_count}/{max_errors}): {e}")
                stop_script()
                if error_count >= max_errors:
                    print("错误次数过多，停止脚本")
                    stop_script()
                time.sleep(1)
        else:
            time.sleep(0.1)  # 脚本未运行时降低CPU占用

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
    except Exception as e:
        print(f"\n程序发生未处理的异常: {type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        stop_event.set()
        keyboard.unhook_all()

# 使用示例
if __name__ == "__main__":
    main()
