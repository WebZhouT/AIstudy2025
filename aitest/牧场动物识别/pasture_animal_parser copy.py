# pasture_animal_parser.py 操作鼠标点击
import pyautogui
import numpy as np
import time
import traceback
import threading
import os
from collections import defaultdict
# 图像识别
from rapidocr_onnxruntime import RapidOCR
# 导入自定义的图像工具模块
from image_utils import find_and_click_image
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, window_title
# 初始化OCR引擎
ocr = RapidOCR()
stop_event = threading.Event()

class PastureAnimalParser:
    def __init__(self):
        self.scroll_region = None  # 滑动区域坐标
        self.precious_animals = set()  # 使用集合存储珍惜动物名称，自动去重
        self.reproductive_count = 0  # 进入生育期的珍惜动物数量
        
    def find_scroll_area(self, template_path, confidence=0.65):
        """找到滑动区域"""
        try:
            print(f"[PastureAnimalParser] 正在查找滑动区域模板: {template_path}")
            hwnd = find_window_by_title(window_title)
            if not hwnd:
                print("[PastureAnimalParser] 未找到游戏窗口")
                return False
                
            x, y, width, height = get_window_position(hwnd)
            
            # 查找滑动区域模板
            scroll_location = pyautogui.locateOnScreen(template_path, confidence=confidence, region=(x, y, width, height))
            if not scroll_location:
                print(f"[PastureAnimalParser] 未找到滑动区域模板: {template_path}，可能没有动物或界面未正确加载")
                return False
                
            # 设置滑动区域
            self.scroll_region = (
                int(scroll_location.left),
                int(scroll_location.top),
                int(scroll_location.width),
                int(scroll_location.height)
            )
            print(f"[PastureAnimalParser] 成功找到滑动区域: {self.scroll_region}")
            return True
        except Exception as e:
            print(f"[PastureAnimalParser] 查找滑动区域时出错: {str(e)}")
            return False
    
    def scroll_to_top(self):
        """滚动到顶部"""
        if not self.scroll_region:
            print("[PastureAnimalParser] 没有滑动区域，无法滚动")
            return False
            
        print("[PastureAnimalParser] 开始滚动到顶部...")
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
                print("[PastureAnimalParser] 已滚动到顶部")
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
            print("[PastureAnimalParser] 没有滑动区域，无法滚动")
            return False
            
        print("[PastureAnimalParser] 开始滚动到底部...")
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
                print("[PastureAnimalParser] 已滚动到底部")
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
            print("[PastureAnimalParser] 没有滑动区域，无法滚动")
            return
            
        x, y, w, h = self.scroll_region
        start_x = x + w // 2
        start_y = y + int(h * 0.8)
        end_x = x + w // 2
        end_y = y + int(h * 0.5)
        
        self.drag_from_to(start_x, start_y, end_x, end_y)
        time.sleep(0.5)
    
    def first_round_scroll(self):
        """第一轮滑动：点击收集和繁殖按钮，统计珍惜动物"""
        print("[PastureAnimalParser] 开始第一轮滑动...")
        
        # 重置计数器
        self.precious_animals = set()
        self.reproductive_count = 0
        
        max_scroll_attempts = 50
        scroll_count = 0
        last_recognized_texts = []
        consecutive_same_count = 0
        
        while scroll_count < max_scroll_attempts and not stop_event.is_set():
            # 截取当前屏幕
            screenshot = pyautogui.screenshot(region=self.scroll_region)
            screenshot_np = np.array(screenshot)
            
            # OCR识别
            ocr_result, _ = ocr(screenshot_np)
            current_recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
            
            # 处理识别结果
            if ocr_result:
                self.process_first_round_ocr(ocr_result)
            
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
        
        print(f"[PastureAnimalParser] 第一轮滑动完成，找到 {len(self.precious_animals)} 个珍惜动物，其中 {self.reproductive_count} 个处于进入生育期")
        return self.reproductive_count
    
    def process_first_round_ocr(self, ocr_result):
        """第一轮OCR处理：点击收集和繁殖按钮，统计珍惜动物"""
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
        
        # 点击收集和繁殖按钮
        self.click_collect_and_breed(text_items)
        
        # 按行分组
        rows = self.group_texts_by_row(text_items)
        
        # 处理每行，统计珍惜动物
        for row in rows:
            self.process_precious_animal_row(row)
    
    def click_collect_and_breed(self, text_items):
        """点击所有收集和繁殖按钮"""
        for item in text_items:
            text = item['text']
            if text in ['收集', '繁殖']:
                # 计算屏幕坐标
                screen_x = self.scroll_region[0] + int(item['x'])
                screen_y = self.scroll_region[1] + int(item['y'])
                
                # 点击按钮
                pyautogui.click(screen_x, screen_y)
                time.sleep(0.5)
                print(f"[PastureAnimalParser] 点击{text}按钮，位置: ({screen_x}, {screen_y})")
    
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
    
    def process_precious_animal_row(self, row):
        """处理单行文本，统计珍惜动物"""
        row_texts = [item['text'] for item in row]
        
        # 检查是否为珍惜动物行（包含白犀牛）
        animal_name = None
        has_reproductive = False
        
        for item in row:
            text = item['text']
            
            # 检查是否为珍惜动物
            if '白犀牛' in text:
                animal_name = text
            # 检查是否为珍惜动物
            if '熊猫' in text:
                animal_name = text            
            # 检查是否有"进入生育期"
            if text == '进入生育期':
                has_reproductive = True
        
        # 如果是珍惜动物且有生育期状态，记录信息
        if animal_name and has_reproductive:
            # 使用集合自动去重
            if animal_name not in self.precious_animals:
                self.precious_animals.add(animal_name)
                self.reproductive_count += 1
                print(f"[PastureAnimalParser] 发现珍惜动物 {animal_name} 处于进入生育期")
    
    def second_round_scroll(self):
        """第二轮滑动：点击进入生育期按钮"""
        print("[PastureAnimalParser] 开始第二轮滑动，点击进入生育期按钮...")
        
        clicked_count = 0
        max_scroll_attempts = 50
        scroll_count = 0
        last_recognized_texts = []
        consecutive_same_count = 0
        
        while scroll_count < max_scroll_attempts and not stop_event.is_set():
            # 截取当前屏幕
            screenshot = pyautogui.screenshot(region=self.scroll_region)
            screenshot_np = np.array(screenshot)
            
            # OCR识别
            ocr_result, _ = ocr(screenshot_np)
            current_recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
            
            # 处理识别结果并点击按钮
            if ocr_result:
                clicked_this_screen = self.click_reproductive_from_ocr(ocr_result)
                clicked_count += clicked_this_screen
            
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
        
        # 滚动回顶部
        self.scroll_to_top()
        
        print(f"[PastureAnimalParser] 第二轮点击完成，共点击 {clicked_count} 个进入生育期按钮")
        return clicked_count
    
    def click_reproductive_from_ocr(self, ocr_result):
        """从OCR结果中点击进入生育期按钮"""
        clicked_count = 0
        
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
        
        # 处理每行，点击进入生育期按钮
        for row in rows:
            row_texts = [item['text'] for item in row]
            
            # 检查是否为珍惜动物行且有进入生育期按钮
            has_precious_animal = any('白犀牛' in text or '熊猫' in text for text in row_texts)
            has_reproductive = any(text == '进入生育期' for text in row_texts)
            
            if has_precious_animal and has_reproductive:
                # 找到进入生育期按钮位置
                for item in row:
                    if item['text'] == '进入生育期':
                        # 计算屏幕坐标
                        screen_x = self.scroll_region[0] + int(item['x'])
                        screen_y = self.scroll_region[1] + int(item['y'])
                        
                        # 点击按钮
                        pyautogui.click(screen_x, screen_y)
                        time.sleep(0.5)
                        clicked_count += 1
                        print(f"[PastureAnimalParser] 点击进入生育期按钮，位置: ({screen_x}, {screen_y})")
                        break
        
        return clicked_count
    
    def third_round_scroll(self):
        """第三轮滑动：点击右箭头并执行喂食和清洁操作"""
        print("[PastureAnimalParser] 开始第三轮滑动...")
        
        # 点击右箭头按钮
        if find_and_click_image('./pasture/rightArrow.png', 0.8):
            print("[PastureAnimalParser] 成功点击右箭头按钮")
            time.sleep(1)  # 等待页面加载
            
            # 滚动到顶部
            self.scroll_to_top()
            
            # 开始向下滚动并识别文本
            max_scroll_attempts = 50
            scroll_count = 0
            last_recognized_texts = []
            consecutive_same_count = 0
            
            while scroll_count < max_scroll_attempts and not stop_event.is_set():
                # 截取当前屏幕
                screenshot = pyautogui.screenshot(region=self.scroll_region)
                screenshot_np = np.array(screenshot)
                
                # OCR识别
                ocr_result, _ = ocr(screenshot_np)
                current_recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
                
                # 处理识别结果并执行点击操作
                if current_recognized_texts:
                    self.process_third_round_ocr(ocr_result)
                
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
            
            print("[PastureAnimalParser] 第三轮滑动完成")
            # 关闭牧场界面
            find_and_click_image('./pasture/closearea.png', confidence=0.65)
        else:
            print("[PastureAnimalParser] 未找到右箭头按钮")
    
    def process_third_round_ocr(self, ocr_result):
        """处理第三轮OCR结果，执行喂食和清洁操作"""
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
        
        # 查找所有清洁按钮和喂食按钮
        cleaning_buttons = []
        feeding_buttons = []
        
        # 查找所有清洁度和剩余寿命信息
        cleanliness_values = []
        remaining_life_values = []
        
        for i, item in enumerate(text_items):
            text = item['text']
            
            # 查找清洁按钮
            if text == '清洁':
                cleaning_buttons.append(item)
            
            # 查找喂食按钮
            if text == '喂食':
                feeding_buttons.append(item)
            
            # 查找清洁度值（数字）
            if text.isdigit() and len(text) <= 3:  # 清洁度是0-100之间的数字
                # 检查这个数字是否在饱食度后面
                if i > 0 and text_items[i-1]['text'].isdigit() and len(text_items[i-1]['text']) <= 3:
                    cleanliness_values.append((int(text), item))
            
            # 查找剩余寿命值（纯数字）
            if text.isdigit() and len(text) <= 2:  # 剩余寿命通常是1-2位数字
                # 检查这个数字是否在产出/繁殖列后面
                if i > 0 and ('剩余' in text_items[i-1]['text'] or text_items[i-1]['text'] in ['产出/繁殖', '繁殖']):
                    remaining_life_values.append((int(text), item))
        
        # 执行清洁操作
        for cleanliness, item in cleanliness_values:
            print(f"[PastureAnimalParser] 检测到清洁度: {cleanliness}")
            if cleanliness < 100:
                # 找到对应的清洁按钮
                for cleaning_button in cleaning_buttons:
                    # 检查按钮是否在同一行（Y坐标相近）
                    if abs(cleaning_button['y'] - item['y']) <= 20:
                        # 计算屏幕坐标
                        screen_x = self.scroll_region[0] + int(cleaning_button['x'])
                        screen_y = self.scroll_region[1] + int(cleaning_button['y'])
                        
                        # 点击按钮
                        pyautogui.click(screen_x, screen_y)
                        time.sleep(0.5)
                        print(f"[PastureAnimalParser] 点击清洁按钮，位置: ({screen_x}, {screen_y})")
                        break
        
        # 执行喂食操作
        for remaining_life, item in remaining_life_values:
            if remaining_life >= 8:
                # 找到对应的饱食度
                satiety = None
                for i, satiety_item in enumerate(text_items):
                    if satiety_item['text'].isdigit() and len(satiety_item['text']) <= 3:
                        # 检查这个数字是否在同一行（Y坐标相近）且是第一个数字
                        if abs(satiety_item['y'] - item['y']) <= 20:
                            # 假设第一个数字是饱食度
                            satiety = int(satiety_item['text'])
                            break
                
                # 如果找到了饱食度且小于100，计算需要点击的次数
                if satiety is not None and satiety < 100:
                    # 计算需要点击的次数（每次点击增加10点饱食度）
                    clicks_needed = (100 - satiety + 9) // 10  # 向上取整
                    
                    # 找到对应的喂食按钮
                    for feeding_button in feeding_buttons:
                        # 检查按钮是否在同一行（Y坐标相近）
                        if abs(feeding_button['y'] - item['y']) <= 20:
                            # 计算屏幕坐标
                            screen_x = self.scroll_region[0] + int(feeding_button['x'])
                            screen_y = self.scroll_region[1] + int(feeding_button['y'])
                            
                            # 点击按钮多次
                            for click in range(clicks_needed):
                                pyautogui.click(screen_x, screen_y)
                                time.sleep(0.5)
                                print(f"[PastureAnimalParser] 点击喂食按钮 ({click+1}/{clicks_needed})，位置: ({screen_x}, {screen_y})")
                            break
    
    def collect_all_animals(self, scroll_template_path):
        """
        收集所有动物信息（主函数）
        
        Args:
            scroll_template_path: 滑动区域模板图片路径
            
        Returns:
            int: 进入生育期的珍惜动物数量
        """
        try:
            print(f"[PastureAnimalParser] 开始收集牧场动物信息，使用模板: {scroll_template_path}")
            
            # 1. 找到滑动区域
            if not self.find_scroll_area(scroll_template_path):
                print("[PastureAnimalParser] 未找到滑动区域，可能没有动物或牧场界面未正确加载")
                return 0
            
            # 2. 不需要滚动到顶部，因为一开始就在顶部
            # 直接开始第一轮滑动
            
            # 3. 第一轮滑动：点击收集和繁殖按钮，统计珍惜动物
            reproductive_count = self.first_round_scroll()
            
            # 4. 滚动回顶部（只有在需要第二轮滑动时才执行）
            if reproductive_count >= 3:
                self.scroll_to_top()
            
            # 5. 第二轮滑动：如果条件满足，点击进入生育期按钮
            if reproductive_count >= 3:
                self.second_round_scroll()
            else:
                print(f"[PastureAnimalParser] 进入生育期的珍惜动物数量不足3个({reproductive_count})，不执行第二轮点击操作")
                self.scroll_to_top()
            
            # 6. 第三轮滑动：预留接口
            self.third_round_scroll()
            
            print(f"[PastureAnimalParser] 动物信息收集完成，共找到 {reproductive_count} 个进入生育期的珍惜动物")
            return reproductive_count
            
        except Exception as e:
            print(f"[PastureAnimalParser] 收集动物信息时发生错误: {str(e)}")
            traceback.print_exc()
            return 0

# 创建全局实例
animal_parser = PastureAnimalParser()

def get_all_pasture_animals(scroll_template_path="./pasture/scroll2.png"):
    """
    获取牧场所有动物信息（对外接口）
    
    Args:
        scroll_template_path: 滑动区域模板图片路径
        
    Returns:
        int: 进入生育期的珍惜动物数量
    """
    try:
        print(f"[PastureAnimalParser] 调用获取牧场动物信息，模板路径: {scroll_template_path}")
        result = animal_parser.collect_all_animals(scroll_template_path)
        print(f"[PastureAnimalParser] 获取牧场动物信息完成，结果: {result}")
        return result
    except Exception as e:
        print(f"[PastureAnimalParser] 获取牧场动物信息时发生异常: {str(e)}")
        traceback.print_exc()
        return 0