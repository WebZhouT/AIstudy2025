# 网易大神签到
import os
import pyautogui
import time
import json
from rapidocr_onnxruntime import RapidOCR
import threading
import keyboard
import numpy as np
import cv2
import win32gui
import win32con
# 引入窗口工具函数
from ..utils.window_utils import find_window_by_title, get_window_position, click_top_center, find_and_click_template

class AutoLoginService:
    def __init__(self):
        # 初始化 OCR 引擎
        self.ocr = RapidOCR()
        
        # 全局变量控制运行状态
        self.running = False
        self.stop_event = threading.Event()
        
        # 定义角色名列表，按照优先级排序
        self.userlist = ["heart","傻傻","残","妲己","兄弟情义无情","依然爱你"]
        
        # 已经完成的角色名字
        self.exitname = []
        
        # 当前操作的目标角色名字
        self.aimData = ''
        
        # 当前匹配的角色索引
        self.current_character_index = -1
        
        # 统一定义窗口标题
        self.window_title = "Phone-E6EDU20429087631"  # 设备2
        
        # 签到结果
        self.results = []
        
        # 主循环线程
        self.main_loop_thread = None
        
        # 设置结果文件路径为public/autologin/result.json
        self.result_file_path = "public/autologin/result.json"
        
        # 加载历史结果
        self.load_results()
        
        # 注册全局热键
        self.register_global_hotkeys()

    def register_global_hotkeys(self):
        """注册全局热键"""
        try:
            # 注册F1启动
            keyboard.add_hotkey('f1', self.start)
            # 注册F2停止
            keyboard.add_hotkey('f2', self.stop)
            print("热键注册成功: F1=启动自动签到, F2=停止自动签到")
        except Exception as e:
            print(f"热键注册失败: {e}")

    def load_results(self):
        """
        加载历史签到结果
        """
        try:
            if os.path.exists(self.result_file_path):
                with open(self.result_file_path, "r", encoding="utf-8") as f:
                    self.results = json.load(f)
        except Exception as e:
            print(f"加载历史结果出错: {str(e)}")
            self.results = []

    def save_results(self):
        """
        保存签到结果到文件
        """
        try:
            with open(self.result_file_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存结果出错: {str(e)}")

    def find_drag_area_and_scroll(self, region, drag_area_template, character_names, threshold=0.7):
        """
        匹配拖拽区域并实现上下滚动功能
        """
        # 1. 匹配拖拽区域
        print("[find_drag_area_and_scroll] 开始匹配拖拽区域...")
        drag_area_matched = find_and_click_template(region, drag_area_template, threshold)
        
        if drag_area_matched:
            print("[find_drag_area_and_scroll] 成功匹配拖拽区域")
            
            # 2. 循环查找角色名
            max_scroll_attempts = 40  # 最大拖拽次数
            scroll_count = 0
            
            while scroll_count < max_scroll_attempts and not self.stop_event.is_set() and self.running:
                if self.stop_event.is_set():
                    break
                    
                # 截取当前区域进行OCR识别
                try:
                    # 截取整个窗口区域进行OCR
                    screenshot = pyautogui.screenshot(region=region)
                    screenshot_np = np.array(screenshot)
                    
                    # 使用RapidOCR识别文字
                    ocr_result, _ = self.ocr(screenshot_np)
                    
                    # 检查是否有识别结果
                    if ocr_result:
                        # 检查当前索引对应的角色名是否在识别结果中
                        if self.current_character_index < len(character_names):
                            current_character = character_names[self.current_character_index]
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
                                    self.aimData = current_character
                                    # 点击角色名字
                                    pyautogui.moveTo(screen_x, screen_y, duration=0.1)
                                    pyautogui.click(screen_x, screen_y)
                                    # 找到目标角色并点击后，不再执行拖拽，直接返回
                                    return True
                    
                    # 如果没有找到当前角色名，执行拖拽操作
                    print(f"[find_drag_area_and_scroll] 未找到目标角色 {character_names[self.current_character_index] if self.current_character_index < len(character_names) else 'N/A'}，执行拖拽操作...")
                    
                    # 根据窗口区域计算拖拽起始和结束点
                    x, y, w, h = region
                    # 设置拖拽起始点（区域中部偏下）
                    start_x = x + w // 2
                    start_y = y + int(h * 0.7)
                    # 设置拖拽结束点（区域中部偏上）
                    end_x = x + w // 2
                    end_y = y + int(h * 0.5)
                    
                    # 执行拖拽操作
                    self.drag_from_to(start_x, start_y, end_x, end_y)
                    self.stop_event.wait(0.5)  # 可中断的等待
                    scroll_count += 1
                    
                except Exception as e:
                    print(f"[find_drag_area_and_scroll] OCR识别出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                    # 即使OCR出错，也执行拖拽操作
                    x, y, w, h = region
                    start_x = x + w // 2
                    start_y = y + int(h * 0.7)
                    end_x = x + w // 2
                    end_y = y + int(h * 0.5)
                    
                    # 执行拖拽操作
                    self.drag_from_to(start_x, start_y, end_x, end_y)
                    self.stop_event.wait(0.5)
                    scroll_count += 1
            
            if scroll_count >= max_scroll_attempts:
                print("[find_drag_area_and_scroll] 已达到最大拖拽次数，未找到目标角色")
            
            return True
        else:
            print("[find_drag_area_and_scroll] 未匹配到拖拽区域")
            return False

    def drag_from_to(self, start_x, start_y, end_x, end_y):
        """
        从起始坐标拖拽到终止坐标
        """
        print(f"[drag_from_to] 执行拖拽操作: 从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
        
        pyautogui.moveTo(start_x, start_y, duration=0.1)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=0.3)
        pyautogui.mouseUp()
        self.stop_event.wait(0.1)  # 可中断的等待

    def start(self):
        """启动自动签到"""
        if self.running:
            print("自动签到已在运行中")
            return
            
        print("正在启动自动签到...")
        self.running = True
        self.stop_event.clear()
        
        # 在新线程中运行主循环
        self.main_loop_thread = threading.Thread(target=self.main_loop, daemon=True)
        self.main_loop_thread.start()
        
        print("自动签到已启动！按 F2 停止")

    def stop(self):
        """停止自动签到"""
        if not self.running:
            print("自动签到未在运行")
            return
            
        print("正在停止自动签到...")
        self.running = False
        self.stop_event.set()
        
        # 等待主循环线程结束
        if self.main_loop_thread and self.main_loop_thread.is_alive():
            self.main_loop_thread.join(timeout=2.0)
        
        print("===== 自动签到已停止 =====")

    def get_status(self):
        """获取运行状态"""
        return {
            "running": self.running,
            "current_character_index": self.current_character_index,
            "aim_data": self.aimData,
            "completed_count": len(self.results)
        }

    def get_results(self):
        """获取签到结果"""
        self.load_results()
        return self.results

    def main_loop(self):
        """主循环函数"""
        template_path = "public/autologin/1.png"  # 今日礼包
        template_path2 = "public/autologin/2.png"  # 去签到
        close1 = "public/autologin/3.png"  # 今日礼包关闭
        more = "public/autologin/more.png"  # 更多按钮
        rolebtn = "public/autologin/4.png"  # 领奖角色按钮
        index = 0
        
        print(f"[主循环] 开始执行自动签到，窗口: {self.window_title}")
        
        try:
            while self.running and not self.stop_event.is_set():
                hwnd = find_window_by_title(self.window_title)
                if not hwnd:
                    print("[主循环] 未找到游戏窗口")
                    self.stop_event.wait(2)  # 可中断的等待
                    continue
                
                print(f"[主循环] 找到窗口句柄: {hwnd}")
                
                # 获取窗口区域
                region = get_window_position(hwnd)
                print(f"[主循环] 窗口区域: {region}")
                
                # 检查窗口是否最小化
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    self.stop_event.wait(0.1)
                
                # 激活窗口
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    pass
                
                if index == 0:
                    self.stop_event.wait(0.1)
                    # 点击窗口顶部激活窗口
                    click_top_center(hwnd)
                    index = 1

                # 查找今日礼包图标
                print("[主循环] 查找今日礼包图标...")
                found_today_gift = False
                
                for attempt in range(5):  # 最多尝试5次
                    if self.stop_event.is_set():
                        break
                        
                    success = find_and_click_template(region, template_path, 0.8)
                    if success:
                        print("[主循环] 成功点击今日礼包")
                        found_today_gift = True
                        self.stop_event.wait(2)
                        break
                    else:
                        print(f"[主循环] 未找到今日礼包，尝试 {attempt + 1}/5")
                        self.stop_event.wait(1)
                
                if not found_today_gift:
                    print("[主循环] 未找到今日礼包，继续下一次循环")
                    self.stop_event.wait(2)
                    continue

                # 查找去签到按钮
                print("[主循环] 查找去签到按钮...")
                found_sign_button = False
                restart_needed = False
                
                for attempt in range(5):
                    if self.stop_event.is_set():
                        break
                        
                    success = find_and_click_template(region, template_path2, 0.7)
                    if success:
                        print("[主循环] 点击去签到按钮")
                        found_sign_button = True
                        self.stop_event.wait(5)
                        break
                    else:
                        print(f"[主循环] 未找到去签到按钮，尝试 {attempt + 1}/5")
                        
                        # 增加角色索引
                        self.current_character_index += 1
                        
                        # 检查是否已经遍历完所有角色
                        if self.current_character_index >= len(self.userlist):
                            print("[主循环] 已遍历完所有角色，程序结束")
                            self.running = False
                            break
                        
                        # 执行切换角色流程
                        find_and_click_template(region, close1, 0.8)
                        self.stop_event.wait(1)
                        find_and_click_template(region, more, 0.8)
                        self.stop_event.wait(1)
                        find_and_click_template(region, rolebtn, 0.3)
                        self.stop_event.wait(1)
                        
                        # 处理拖拽区域
                        drag_area_template = "public/autologin/drag_area.png"
                        self.find_drag_area_and_scroll(region, drag_area_template, self.userlist, 0.3)
                        self.stop_event.wait(1)
                        
                        # 点击领取奖励按钮
                        find_and_click_template(region, "public/autologin/5.png", 0.3)
                        self.stop_event.wait(1)
                        
                        restart_needed = True
                        break
                
                if restart_needed:
                    continue
                if not found_sign_button:
                    continue

                # 后续的点击操作都使用可中断的等待
                self.process_reward_actions(region)
                
                print("[主循环] 本次循环完成，等待3秒后继续...")
                self.stop_event.wait(3)
                
        except Exception as e:
            print(f"[主循环] 发生异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            print("[主循环] 自动签到线程退出")

    def process_reward_actions(self, region):
        """处理奖励相关的点击操作"""
        # 点击奖励弹框
        self.click_with_retry(region, 'public/autologin/7.png', "奖励领取成功", 3)
        
        # 点击抽奖按钮
        self.click_with_retry(region, 'public/autologin/6.png', "去抽奖", 3)
        
        # 再次点击奖励弹框
        self.click_with_retry(region, 'public/autologin/7.png', "开心收下", 3)
        
        # 识别并保存奖励信息
        self.identify_and_save_reward()

    def click_with_retry(self, region, template_path, action_name, max_attempts=3):
        """带重试的点击操作"""
        for attempt in range(max_attempts):
            if self.stop_event.is_set():
                break
                
            success = find_and_click_template(region, template_path, 0.8)
            if success:
                print(f"[主循环] 点击{action_name}")
                self.stop_event.wait(3)
                return True
            else:
                print(f"[主循环] 未找到{action_name}按钮，尝试 {attempt + 1}/{max_attempts}")
                self.stop_event.wait(2)
        return False

    def identify_and_save_reward(self):
        """识别并保存奖励信息"""
        try:
            hwnd = find_window_by_title(self.window_title)
            if not hwnd:
                print("[奖励识别] 未找到游戏窗口")
                return
                
            window_region = get_window_position(hwnd)
            
            # 查找goods.png模板
            goods_template_path = "public/autologin/goods.png"
            template = cv2.imread(goods_template_path)
            if template is None:
                print(f"[奖励识别] 无法读取模板图片: {goods_template_path}")
                return
                
            # 截屏并匹配
            window_screenshot = pyautogui.screenshot(region=window_region)
            open_cv_image = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
            
            res = cv2.matchTemplate(open_cv_image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            if max_val >= 0.8:
                h, w = template.shape[:2]
                top_left = (window_region[0] + max_loc[0], window_region[1] + max_loc[1])
                
                # 截取奖励区域进行OCR
                goods_region = (top_left[0], top_left[1], w, h)
                goods_screenshot = pyautogui.screenshot(region=goods_region)
                img = cv2.cvtColor(np.array(goods_screenshot), cv2.COLOR_RGB2BGR)
                ocr_result, elapse = self.ocr(img)
                
                full_text = ""
                if ocr_result:
                    recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
                    full_text = "\n".join(recognized_texts)
                    print("[奖励识别] OCR识别结果:")
                    for line in recognized_texts:
                        print(f"  - {line}")
                else:
                    full_text = "未识别到文本"
                    print("[奖励识别] 未识别到文字")
                
                # 保存奖励信息
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                log_entry = {
                    "name": self.aimData,
                    "result": full_text,
                    "timestamp": timestamp
                }
                
                self.results.append(log_entry)
                self.save_results()
                print(f"[奖励识别] 已保存奖励日志: {self.aimData} - {full_text}")

            else:
                # 未匹配到goods模板的情况
                print(f"[奖励识别] 未匹配到奖励区域，最高匹配度: {max_val:.2f}")
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                log_entry = {
                    "name": self.aimData,
                    "result": f"未匹配到奖励区域 (匹配度: {max_val:.2f})",
                    "timestamp": timestamp
                }
                
                self.results.append(log_entry)
                self.save_results()
                print(f"[奖励识别] 已记录未匹配日志")

        except Exception as e:
            print(f"[奖励识别] 奖励识别出错: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 即使出错也记录日志
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            log_entry = {
                "name": self.aimData,
                "result": f"识别出错: {str(e)}",
                "timestamp": timestamp
            }
            
            self.results.append(log_entry)
            self.save_results()
            print(f"[奖励识别] 已记录错误日志")