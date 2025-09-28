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

class AnimalRecognizer:
    def __init__(self, window_title, confidence_threshold=0.8, screenshot_dir="screenshots"):
        self.window_title = window_title
        self.confidence_threshold = confidence_threshold
        self.templates = {}  # 存储模板和相关信息
        self.is_running = False
        self.screenshot_dir = screenshot_dir
        
        # 创建截图目录
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
    
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
    
    def mark_and_save_screenshot(self, screen_image, animals):
        """在截图上标记动物并保存"""
        if screen_image is None or not animals:
            return None
            
        marked_image = screen_image.copy()
        
        # 绘制所有检测到的动物框
        for animal in animals:
            top_left = (animal['pt_x'], animal['pt_y'])
            bottom_right = (animal['pt_x'] + animal['template_w'], animal['pt_y'] + animal['template_h'])
            
            # 绘制矩形框
            cv2.rectangle(marked_image, top_left, bottom_right, animal['color'], 2)
            
            # 添加标签（动物名称和相似度）
            label = f"{animal['name']}: {animal['confidence']:.2f}"
            cv2.putText(marked_image, label, 
                       (top_left[0], top_left[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, animal['color'], 2)
        
        # 生成文件名并保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.screenshot_dir, f"detection_{timestamp}.png")
        cv2.imwrite(filename, marked_image)
        
        return filename
    
    def click_animal(self, animal):
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
        pyautogui.click()
        
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

# 使用示例
if __name__ == "__main__":
    # 创建识别器实例，指定窗口标题
    recognizer = AnimalRecognizer(
        window_title="Phone-E6EDU20429087631",  # 替换为你的游戏窗口标题
        confidence_threshold=0.8, 
        screenshot_dir="detection_screenshots"
    )
    
    # 从JSON文件加载动物模板
    recognizer.load_animal_templates_from_json("animals_config.json")
    
    # 启动识别
    recognizer.start(save_screenshot=True)
    
    try:
        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序被用户中断")
        recognizer.stop()
