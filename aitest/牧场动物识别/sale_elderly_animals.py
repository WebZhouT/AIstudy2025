# sale_elderly_animals.py
import pyautogui
import numpy as np
import time
import traceback
import threading
from collections import defaultdict
# 图像识别
from rapidocr_onnxruntime import RapidOCR
# 导入自定义的图像工具模块
from image_utils import click_at_window_coord
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, window_title
# 导入自定义的图像工具模块
from image_utils import find_and_click_image, click_at_window_coord, mark_and_save_screenshot
# 初始化OCR引擎
ocr = RapidOCR()
stop_event = threading.Event()
hwnd = find_window_by_title(window_title)

class ElderlyAnimalSeller:
    def __init__(self):
        self.scroll_region = None  # 滑动区域坐标
        self.sold_count = 0  # 成功出售的老年动物数量
        self.sale_positions = []  # 存储所有需要点击的出售按钮位置
        
    def find_scroll_area(self, template_path, confidence=0.5):
        """找到滑动区域"""
        try:
            print(f"[ElderlyAnimalSeller] 正在查找滑动区域模板: {template_path}")
            hwnd = find_window_by_title(window_title)
            if not hwnd:
                print("[ElderlyAnimalSeller] 未找到游戏窗口")
                return False
                
            x, y, width, height = get_window_position(hwnd)
            
            # 查找滑动区域模板
            scroll_location = pyautogui.locateOnScreen(template_path, confidence=confidence, region=(x, y, width, height))
            if not scroll_location:
                print(f"[ElderlyAnimalSeller] 未找到滑动区域模板: {template_path}")
                return False
                
            # 设置滑动区域
            self.scroll_region = (
                int(scroll_location.left),
                int(scroll_location.top),
                int(scroll_location.width),
                int(scroll_location.height)
            )
            print(f"[ElderlyAnimalSeller] 成功找到滑动区域: {self.scroll_region}")
            return True
        except Exception as e:
            print(f"[ElderlyAnimalSeller] 查找滑动区域时出错: {str(e)}")
            return False
    
    def scroll_to_top(self):
        """滚动到顶部"""
        if not self.scroll_region:
            print("[ElderlyAnimalSeller] 没有滑动区域，无法滚动")
            return False
            
        print("[ElderlyAnimalSeller] 开始滚动到顶部...")
        max_scroll_attempts = 10
        scroll_count = 0
        last_recognized_texts = []
        
        while scroll_count < max_scroll_attempts and not stop_event.is_set():
            # 截取当前区域进行OCR识别
            screenshot = pyautogui.screenshot(region=self.scroll_region)
            screenshot_np = np.array(screenshot)
            
            ocr_result, _ = ocr(screenshot_np)
            current_recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
            
            # 判断是否到达顶部：连续2次OCR结果相同
            if (len(last_recognized_texts) > 0 and 
                len(current_recognized_texts) > 0 and
                set(last_recognized_texts) == set(current_recognized_texts)):
                print("[ElderlyAnimalSeller] 已滚动到顶部")
                break
                
            last_recognized_texts = current_recognized_texts.copy()
            
            # 执行向上拖拽操作
            x, y, w, h = self.scroll_region
            start_x = x + w // 2
            start_y = y + int(h * 0.3)
            end_x = x + w // 2
            end_y = y + int(h * 0.7)
            
            self.drag_from_to(start_x, start_y, end_x, end_y)
            scroll_count += 1
            time.sleep(0.5)
            
        return True
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        if not self.scroll_region:
            print("[ElderlyAnimalSeller] 没有滑动区域，无法滚动")
            return False
            
        print("[ElderlyAnimalSeller] 开始滚动到底部...")
        max_scroll_attempts = 50
        scroll_count = 0
        last_recognized_texts = []
        
        while scroll_count < max_scroll_attempts and not stop_event.is_set():
            # 截取当前区域进行OCR识别
            screenshot = pyautogui.screenshot(region=self.scroll_region)
            screenshot_np = np.array(screenshot)
            
            ocr_result, _ = ocr(screenshot_np)
            current_recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
            
            # 判断是否到达底部：连续2次OCR结果相同
            if (len(last_recognized_texts) > 0 and 
                len(current_recognized_texts) > 0 and
                set(last_recognized_texts) == set(current_recognized_texts)):
                print("[ElderlyAnimalSeller] 已滚动到底部")
                break
                
            last_recognized_texts = current_recognized_texts.copy()
            
            # 执行向下拖拽操作
            self.scroll_down()
            scroll_count += 1
            
        return True
    
    def drag_from_to(self, start_x, start_y, end_x, end_y):
        """执行拖拽操作"""
        pyautogui.moveTo(start_x, start_y, duration=0.1)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=0.3)
        pyautogui.mouseUp()
        time.sleep(0.1)
    
    def scroll_down(self):
        """向下滑动一屏"""
        if not self.scroll_region:
            print("[ElderlyAnimalSeller] 没有滑动区域，无法滚动")
            return
            
        x, y, w, h = self.scroll_region
        start_x = x + w // 2
        start_y = y + int(h * 0.8)
        end_x = x + w // 2
        end_y = y + int(h * 0.5)
        
        self.drag_from_to(start_x, start_y, end_x, end_y)
        time.sleep(0.5)
    
    def group_texts_by_row(self, text_items):
        """将文本按行分组"""
        if not text_items:
            return []
            
        # 按Y坐标排序
        text_items.sort(key=lambda item: item['y'])
        
        # 按行分组
        rows = []
        current_row = [text_items[0]]
        current_y = text_items[0]['y']
        
        for item in text_items[1:]:
            if abs(item['y'] - current_y) <= 20:  # 简化行高判断
                current_row.append(item)
            else:
                current_row.sort(key=lambda x: x['x'])
                rows.append(current_row)
                current_row = [item]
                current_y = item['y']
        
        if current_row:
            current_row.sort(key=lambda x: x['x'])
            rows.append(current_row)
            
        return rows
    
    def find_all_elderly_animals(self):
        """找到所有老年动物并记录出售按钮位置"""
        print("[ElderlyAnimalSeller] 开始查找所有老年动物...")
        
        self.sale_positions = []  # 清空之前的位置记录
        
        max_scroll_attempts = 50
        scroll_count = 0
        last_recognized_texts = []
        consecutive_same_count = 0
        
        # 先滚动到顶部
        self.scroll_to_top()
        
        while scroll_count < max_scroll_attempts and not stop_event.is_set():
            # 截取当前屏幕
            screenshot = pyautogui.screenshot(region=self.scroll_region)
            screenshot_np = np.array(screenshot)
            
            # OCR识别
            ocr_result, _ = ocr(screenshot_np)
            current_recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
            
            # 处理识别结果并记录出售按钮位置（不点击）
            if ocr_result:
                self.collect_sale_positions_from_ocr(ocr_result)
            
            # 判断是否到达底部：连续2次OCR结果相同
            if (len(last_recognized_texts) > 0 and 
                len(current_recognized_texts) > 0 and
                set(last_recognized_texts) == set(current_recognized_texts)):
                consecutive_same_count += 1
                if consecutive_same_count >= 2:
                    break
            else:
                consecutive_same_count = 0
                
            last_recognized_texts = current_recognized_texts.copy()
            
            # 向下滑动
            self.scroll_down()
            scroll_count += 1
        
        print(f"[ElderlyAnimalSeller] 找到 {len(self.sale_positions)} 个老年动物需要出售")
        return len(self.sale_positions)
    
    def collect_sale_positions_from_ocr(self, ocr_result):
        """从OCR结果中收集出售按钮位置（不点击）"""
        global hwnd
        
        # 提取所有文字和位置
        text_items = []
        for text_info in ocr_result:
            if text_info and len(text_info) > 1:
                box = text_info[0]
                text = text_info[1]
                
                # 计算文字中心位置
                y_coords = [point[1] for point in box]
                avg_y = sum(y_coords) / len(y_coords)
                x_coords = [point[0] for point in box]
                avg_x = sum(x_coords) / len(x_coords)
                
                text_items.append({
                    'text': text,
                    'x': avg_x,
                    'y': avg_y,
                    'box': box
                })
        
        # 按行分组
        rows = self.group_texts_by_row(text_items)
        
        # 处理每行，记录有"老年"文字的行的出售按钮位置
        for row in rows:
            row_texts = [item['text'] for item in row]
            
            # 检查是否为老年动物行（包含"老年"文字）
            has_elderly = any('老年' in text for text in row_texts)
            has_sale_button = any('出售' in text for text in row_texts)
            
            if has_elderly and has_sale_button:
                # 找到出售按钮位置
                for item in row:
                    if '出售' in item['text']:
                        # 计算屏幕坐标
                        screen_x = self.scroll_region[0] + int(item['x'])
                        screen_y = self.scroll_region[1] + int(item['y'])
                        
                        # 记录位置，不点击
                        self.sale_positions.append((screen_x, screen_y))
                        print(f"[ElderlyAnimalSeller] 记录出售按钮位置: ({screen_x}, {screen_y})")
                        break
    
    def click_all_sale_buttons(self):
        """点击所有记录的出售按钮"""
        global hwnd
        clicked_count = 0
        
        print(f"[ElderlyAnimalSeller] 开始点击 {len(self.sale_positions)} 个出售按钮...")
        
        for position in self.sale_positions:
            if stop_event.is_set():
                break
                
            screen_x, screen_y = position
            
            # 点击按钮
            click_at_window_coord(hwnd, screen_x, screen_y)
            time.sleep(0.5)
            clicked_count += 1
            print(f"[ElderlyAnimalSeller] 点击出售按钮，位置: ({screen_x}, {screen_y}) - {clicked_count}/{len(self.sale_positions)}")
            time.sleep(0.5)
            # 点击确认按钮
            find_and_click_image('./sale_image/salebtn.png', confidence=0.65)
            time.sleep(0.5)
            # 处理可能的确认对话框
            self.handle_confirmation_dialog()
        
        return clicked_count
    
    def handle_confirmation_dialog(self):
        """处理可能的确认对话框"""
        # 这里可以添加处理确认对话框的逻辑
        # 例如：识别并点击"确定"或"确认"按钮
        # 暂时留空，根据实际游戏界面添加相应逻辑
        pass
    
    def sell_elderly_animals(self, scroll_template_path):
        """
        出售所有老年动物（主函数）
        
        Args:
            scroll_template_path: 滑动区域模板图片路径
            
        Returns:
            int: 成功出售的老年动物数量
        """
        try:
            print(f"[ElderlyAnimalSeller] 开始出售老年动物，使用模板: {scroll_template_path}")
            
            # 重置计数器
            self.sold_count = 0
            self.sale_positions = []
            
            # 1. 找到滑动区域
            if not self.find_scroll_area(scroll_template_path):
                print("[ElderlyAnimalSeller] 未找到滑动区域，可能没有动物或出售界面未正确加载")
                return 0
            
            # 2. 滚动到顶部
            self.scroll_to_top()
            
            # 3. 第一阶段：找到所有老年动物并记录出售按钮位置
            elderly_count = self.find_all_elderly_animals()
            
            if elderly_count == 0:
                print("[ElderlyAnimalSeller] 未找到老年动物，无需出售")
                return 0
            
            # 4. 第二阶段：点击所有记录的出售按钮
            sold_count = self.click_all_sale_buttons()
            
            # 5. 滚动回顶部
            self.scroll_to_top()
            
            print(f"[ElderlyAnimalSeller] 老年动物出售完成，共出售 {sold_count} 只老年动物")
            return sold_count
            
        except Exception as e:
            print(f"[ElderlyAnimalSeller] 出售老年动物时发生错误: {str(e)}")
            traceback.print_exc()
            return 0

# 创建全局实例
elderly_animal_seller = ElderlyAnimalSeller()

def sell_elderly_animals(scroll_template_path="./sale_image/scroll3.png"):
    """
    出售老年动物（对外接口）
    
    Args:
        scroll_template_path: 滑动区域模板图片路径
        
    Returns:
        int: 成功出售的老年动物数量
    """
    try:
        print(f"[ElderlyAnimalSeller] 调用出售老年动物，模板路径: {scroll_template_path}")
        result = elderly_animal_seller.sell_elderly_animals(scroll_template_path)
        print(f"[ElderlyAnimalSeller] 出售老年动物完成，结果: {result}")
        return result
    except Exception as e:
        print(f"[ElderlyAnimalSeller] 出售老年动物时发生异常: {str(e)}")
        traceback.print_exc()
        return 0