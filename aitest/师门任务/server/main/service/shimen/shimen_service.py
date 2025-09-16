# 师门任务
import os
import pyautogui
import time
import json
from rapidocr_onnxruntime import RapidOCR
import threading
import keyboard
import win32gui
import win32con
import cv2
import numpy as np
# 引入窗口工具函数
from ..utils.window_utils import find_window_by_title, get_window_position, click_top_center, find_and_click_template
# 师门导航服务（当前未实现，直接写到代码里面了）
from .navigation_service import ShimenNavigationService
# 寻物任务服务
from .find_item_service import FindItemService
# 捕捉任务服务
from .capture_service import CaptureService
# 巡逻任务服务 
from .patrol_service import PatrolService
class ShimenService:
    def __init__(self, sect="五庄观"):
        # 初始化 OCR 引擎
        self.ocr = RapidOCR()
        
        # 全局变量控制运行状态
        self.running = False
        self.stop_event = threading.Event()
        
        # 统一定义窗口标题
        self.window_title = "Phone-E6EDU20429087631"  # 设备1
        
        # 任务结果
        self.results = []
        
        # 键盘监听线程
        self.keyboard_thread = None
        self.main_loop_thread = None
        
        # 设置结果文件路径为public/shimen/result.json
        self.result_file_path = "public/shimen/result.json"
        
        # 调试图片保存路径
        self.debug_image_path = "public/shimen/debug"
        # 创建调试图片保存目录
        if not os.path.exists(self.debug_image_path):
            os.makedirs(self.debug_image_path)
        
        # 加载历史结果
        self.load_results()
        
        # 注册全局热键
        self.register_global_hotkeys()
        
        # 门派信息
        self.sect = sect
        # 加载门派配置
        self.load_sect_config()
        
        # 已完成任务计数
        self.completed_count = 0

    def load_sect_config(self):
        """加载门派配置信息"""
        try:
            config_path = "public/shimen/task/taskBtnlist.json"
            with open(config_path, "r", encoding="utf-8") as f:
                configs = json.load(f)
            
            # 根据门派查找对应配置
            for config in configs:
                if config.get("sect") == self.sect:
                    self.sect_config = config
                    print(f"加载门派配置成功: {self.sect}")
                    return
            
            # 如果没找到对应配置，使用默认配置
            self.sect_config = configs[0] if configs else {}
            print(f"未找到门派配置，使用默认配置: {self.sect}")
        except Exception as e:
            print(f"加载门派配置失败: {e}")
            self.sect_config = {}

    def register_global_hotkeys(self):
        """注册全局热键"""
        try:
            # 注册F1启动
            keyboard.add_hotkey('f1', self.start)
            # 注册F2停止
            keyboard.add_hotkey('f2', self.stop)
            print("热键注册成功: F1=启动, F2=停止")
        except Exception as e:
            print(f"热键注册失败: {e}")

    def load_results(self):
        """
        加载历史任务结果
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
        保存任务结果到文件
        """
        try:
            with open(self.result_file_path, "w", encoding="utf-8") as f:
                                json.dump(self.results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存结果出错: {str(e)}")

    def start(self):
        """启动师门任务"""
        if self.running:
            print("任务已在运行中")
            return
            
        print("正在启动师门任务...")
        self.running = True
        self.stop_event.clear()
        
        # 在新线程中运行主循环
        self.main_loop_thread = threading.Thread(target=self.main_loop, daemon=True)
        self.main_loop_thread.start()
        
        print("师门任务已启动！按 F2 停止")

    def stop(self):
        """停止师门任务"""
        if not self.running:
            print("任务未在运行")
            return
            
        print("正在停止师门任务...")
        self.running = False
        self.stop_event.set()
        
        # 等待主循环线程结束
        if self.main_loop_thread and self.main_loop_thread.is_alive():
            self.main_loop_thread.join(timeout=2.0)
        
        print("===== 脚本已停止 =====")

    def get_status(self):
        """获取运行状态"""
        return {
            "running": self.running,
            "completed_count": len(self.results)
        }

    def get_results(self):
        """获取任务结果"""
        self.load_results()
        return self.results

    def accept_and_identify_task(self):
        """
        接受任务并识别任务类型
        """
        print("接受任务并识别任务类型...")
        # 这里应该实现接受任务并识别任务类型的逻辑
        # 暂时返回默认值，实际应根据界面OCR识别结果确定
        return "未知", "未识别任务内容"

    def execute_task_by_type(self, task_type, full_text, region):
        """
        根据任务类型执行对应的任务
        
        Args:
            task_type: 任务类型 ("捕捉", "寻物", "巡逻")
            full_text: 任务完整文本描述
            region: 窗口区域
            
        Returns:
            bool: 任务执行是否成功
        """
        success = False
        if task_type == "捕捉":
            capture_service = CaptureService(region, self, self.ocr, ShimenNavigationService(), self.sect_config)
            success = capture_service.execute(full_text)
        elif task_type == "寻物":
            find_item_service = FindItemService(region, self, self.ocr, ShimenNavigationService(), self.sect_config)
            success = find_item_service.execute(full_text)
        elif task_type == "巡逻":
            patrol_service = PatrolService(self, region, self.ocr, ShimenNavigationService(), self.sect_config)
            success = patrol_service.execute(full_text)
        elif task_type == "完成":
            # 当任务类型为"完成"时，执行与回门派相同的逻辑
            print("[主循环] 检测到任务完成，执行回门派操作")
            navigation_service = ShimenNavigationService()
            navigation_service.navigate_to_shimen_interface(region, notice, gohome, shifu, self.sect_config)
            success = True
        else:
            print(f"未知任务类型: {task_type}")
            
        return success

    def main_loop(self):
        """主循环函数"""
        template_path = "public/shimen/task/task.png"  # 师门任务图标
        notice = "public/shimen/task/notice.png"  # 法术提示
        # 从配置中获取回门派和师傅图标路径
        gohome = self.sect_config.get("gohome", "public/shimen/task/gohomewz.png")
        shifu = self.sect_config.get("shifu", "public/shimen/task/zhenyuan.png")
        shifuaim = self.sect_config.get("shifuaim", "public/shimen/task/shifuaim.png")
        template_path2 = "public/shimen/task/accept.png"  # 接取任务按钮
        close_btn = "public/shimen/close.png"  # 关闭按钮
        index = 0
        
        print(f"[主循环] 开始执行师门任务，窗口: {self.window_title}")
        
        try:
            while self.running and not self.stop_event.is_set():
                hwnd = find_window_by_title(self.window_title)
                if not hwnd:
                    print("[主循环] 未找到游戏窗口")
                    time.sleep(2)
                    continue
                
                print(f"[主循环] 找到窗口句柄: {hwnd}")
                
                # 获取窗口区域
                region = get_window_position(hwnd)
                print(f"[主循环] 窗口区域: {region}")
                
                # 检查窗口是否最小化
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.1)
                
                # 激活窗口
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    pass
                
                if index == 0:
                    time.sleep(0.1)
                    # 点击窗口顶部激活窗口
                    click_top_center(hwnd)
                    index = 1
                # 步骤
                # 1.先判断指定模板区域的文字信息是否有师门字样，有的话解析文字，确定师门任务信息
                #   如果没有对应信息，就识别指定图片所在位置进行点击操作
                #   如果有对应信息，对信息进行解析，判断后续任务内容。输出解析的文字信息
                # 查找师门任务信息
                    
                print("[主循环] 查找师门任务信息...")
                
                # 获取当前句柄窗口指定图片所在区域位置
                template = cv2.imread(template_path)
                if template is None:
                    print(f"[主循环] 无法读取模板图片 {template_path}")
                    time.sleep(2)
                    continue
                
                # 截取整个窗口区域
                screenshot = pyautogui.screenshot(region=region)
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # 在窗口截图中匹配模板
                res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                
                threshold = 0.2
                if max_val >= threshold:
                    # 计算匹配区域的坐标（相对于整个屏幕）
                    h, w = template.shape[:2]
                    top_left = (region[0] + max_loc[0], region[1] + max_loc[1])
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    
                    # 定义一个稍微扩大一点的区域用于OCR识别
                    # 扩大50像素范围以确保包含完整任务信息
                    ocr_region = (
                        max(region[0], top_left[0]),
                        max(region[1], top_left[1]),
                        min(region[2], w),
                        min(region[3], h)
                    )
                    
                    # 截取匹配区域进行OCR识别
                    task_screenshot = pyautogui.screenshot(region=ocr_region)
                    screenshot_np = np.array(task_screenshot)
                    
                    # 保存调试图片
                    debug_filename = f"shimen_task_{int(time.time())}.png"
                    debug_filepath = os.path.join(self.debug_image_path, debug_filename)
                    task_screenshot.save(debug_filepath)
                    print(f"[主循环] 调试图片已保存: {debug_filepath}")
                    
                    # 使用RapidOCR识别文字
                    ocr_result, _ = self.ocr(screenshot_np)
                    
                    # 检查是否有识别结果
                    task_text = ""
                    if ocr_result:
                        # 提取所有识别到的文字
                        texts = [text_info[1] for text_info in ocr_result if len(text_info) > 1]
                        task_text = " ".join(texts)
                        print(f"[主循环] 识别到的文字: {task_text}")
                        
                        # 判断是否有"师门"字样
                        if "师门" in task_text:
                            print("[主循环] 检测到师门任务，开始解析任务信息")
                            if "回师门" in task_text or "前往师父" in task_text or "完成" in task_text:
                                # 使用导航服务导航到师门界面
                                navigation_service = ShimenNavigationService()
                                # 传递门派配置信息
                                navigation_service.navigate_to_shimen_interface(region, notice, gohome, shifu, self.sect_config)
                                
                                # 先检查是否存在shifuaim.png，如果不存在再执行原有逻辑
                                if not find_and_click_template(region, shifuaim, 0.4):
                                    # 使用导航服务查找并点击师门任务
                                    if navigation_service.find_and_click_shimen_task(region):
                                        # ========后续补充
                                        # 2. 接受任务并识别类型
                                        task_type, full_text = self.accept_and_identify_task()
                                        self.current_task = task_type
                                        
                                        # 3. 执行对应任务
                                        success = self.execute_task_by_type(task_type, full_text, region)
                                        
                                        # 任务执行完成后返回师门
                                        if success:
                                            self.return_to_master()
                                            self.completed_count += 1
                                    else:
                                        print("[主循环] 解析对应的文字信息分析任务")
                                else:
                                    print("[主循环] 检测到shifuaim.png，已点击")
                                    # 点击对话的关闭按钮
                                    find_and_click_template(region, "public/shimen/task/close.png", 0.4)
                                        
                                    # 重新识别任务类型并执行对应任务
                                    # 查找师门任务信息
                                    print("[主循环] 重新查找师门任务信息...")
                                    template = cv2.imread(template_path)
                                    if template is None:
                                        print(f"[主循环] 无法读取模板图片 {template_path}")
                                    else:
                                        # 截取整个窗口区域
                                        screenshot = pyautogui.screenshot(region=region)
                                        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                                            
                                        # 在窗口截图中匹配模板
                                        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                                            
                                        threshold = 0.2
                                        if max_val >= threshold:
                                            # 计算匹配区域的坐标（相对于整个屏幕）
                                            h, w = template.shape[:2]
                                            top_left = (region[0] + max_loc[0], region[1] + max_loc[1])
                                            bottom_right = (top_left[0] + w, top_left[1] + h)
                                                
                                            # 定义一个稍微扩大一点的区域用于OCR识别
                                            # 扩大50像素范围以确保包含完整任务信息
                                            ocr_region = (
                                                top_left[0],
                                                top_left[1],
                                                w,
                                                h
                                            )
                                                
                                            # 截取匹配区域进行OCR识别
                                            task_screenshot = pyautogui.screenshot(region=ocr_region)
                                            screenshot_np = np.array(task_screenshot)
                                                
                                            # 保存调试图片
                                            debug_filename = f"shimen_task_{int(time.time())}_after_return.png"
                                            debug_filepath = os.path.join(self.debug_image_path, debug_filename)
                                            task_screenshot.save(debug_filepath)
                                            print(f"[主循环] 调试图片已保存: {debug_filepath}")
                                                
                                            # 使用RapidOCR识别文字
                                            ocr_result, _ = self.ocr(screenshot_np)
                                                
                                            # 检查是否有识别结果
                                            task_text = ""
                                            if ocr_result:
                                                # 提取所有识别到的文字
                                                texts = [text_info[1] for text_info in ocr_result if len(text_info) > 1]
                                                task_text = " ".join(texts)
                                                print(f"[主循环] 识别到的文字: {task_text}")
                                                
                                                # 分析任务类型并执行对应任务
                                                if "抓" in task_text or "捕捉" in task_text:
                                                    task_type = "捕捉"
                                                    full_text = task_text
                                                elif "买到" in task_text or "送给" in task_text:
                                                    task_type = "寻物"
                                                    full_text = task_text
                                                elif "巡逻" in task_text or "附近" in task_text:
                                                    task_type = "巡逻"
                                                    full_text = task_text
                                                elif "任务完成" in task_text:
                                                    task_type = "完成"
                                                    full_text = task_text
                                                else:
                                                    task_type = "未知"
                                                    full_text = task_text
                                                    
                                                print(f"[主循环] 识别到任务类型: {task_type}")
                                                
                                                # 如果任务类型为未知，则点击找师傅领取任务
                                                if task_type == "未知":
                                                    print("[主循环] 任务类型未知，点击找师傅领取任务")
                                                    navigation_service = ShimenNavigationService()
                                                    navigation_service.find_and_click_shimen_task(region)
                                                    
                                                    # 重新识别任务类型
                                                    task_type, full_text = self.accept_and_identify_task()
                                                    print(f"[主循环] 重新识别到任务类型: {task_type}")
                                                    
                                                # 执行对应任务
                                                success = self.execute_task_by_type(task_type, full_text, region)
                                                    
                                                # 任务执行完成后返回师门
                                                if success:
                                                    self.return_to_master()
                                                    self.completed_count += 1
                            else:
                                # 解析师门任务信息的后续操作可以在这里添加
                                # 2. 接受任务并识别类型
                                task_type, full_text = self.parse_shimen_task(region)
                                self.current_task = task_type
                                
                                # 3. 执行对应任务
                                success = False
                                if "巡逻" in full_text or "附近" in full_text:
                                    patrol_service = PatrolService(self, region, self.ocr, ShimenNavigationService(), self.sect_config)
                                    success = patrol_service.execute(full_text)
                                    
                                    # 巡逻任务完成后，继续执行下一个任务
                                    if success:
                                        self.return_to_master()
                                        self.completed_count += 1
                                        # 保存结果并继续下一个任务
                                        self.record_task_result(f"完成巡逻任务: {full_text}")
                                        time.sleep(2)
                                        continue  # 继续主循环执行下一个任务
                                    else:
                                        print("巡逻任务执行失败")
                                        break
                                elif "买到" in full_text or "送给" in full_text:
                                    # 执行找物品的任务逻辑
                                    find_item_service = FindItemService(region, self, self.ocr, ShimenNavigationService(), self.sect_config)
                                    success = find_item_service.execute(full_text)
                                elif "捕捉" in full_text or "逻" in full_text:
                                    # 执行巡逻任务逻辑
                                    capture_service = CaptureService(region, self, self.ocr, ShimenNavigationService(), self.sect_config)
                                    success = capture_service.execute(full_text)
                                else:
                                    # 未知任务类型（比如继续回师门看看师父，就是说交任务也会走到这里）
                                    # 1.先点击关闭按钮
                                    # find_and_click_template(region, "", 0.4)
                                    print(f"未知任务类型: {task_type}")
                                    continue
                                
                                # 4. 返回交任务
                                if success:
                                    self.return_to_master()
                                    self.completed_count += 1
                                
                                time.sleep(2)
                        else:
                            print("[主循环] 未检测到师门字样，执行跳出循环操作")
                            break
                            # # 没有"师门"字样时的点击操作可以在这里添加
                            # pyautogui.click(top_left[0] + w//2, top_left[1] + h//2)
                            # 解析师门任务信息的后续操作可以在这里添加
                            # self.parse_shimen_task(region)
                    else:
                        print("[主循环] 未识别到任何文字")
                        # 没有识别到文字时的默认点击操作
                        pyautogui.click(top_left[0] + w//2, top_left[1] + h//2)
                else:
                    print(f"[主循环] 未能在窗口中找到任务图标模板，最高匹配度: {max_val:.2f}")
                    # 在找不到任务图标时，添加再次OCR识别逻辑
                    # 当任务类型为未知时，重新检查任务图标区域
                    template_path = "public/shimen/task/task.png"  # 师门任务图标
                    template = cv2.imread(template_path)
                    if template is not None:
                        # 再次尝试匹配模板
                        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                        
                        if max_val >= 0.2:  # 使用较低阈值
                            # 计算匹配区域的坐标（相对于整个屏幕）
                            h, w = template.shape[:2]
                            top_left = (region[0] + max_loc[0], region[1] + max_loc[1])
                            
                            # 定义OCR识别区域
                            ocr_region = (
                                max(region[0], top_left[0]),
                                max(region[1], top_left[1]),
                                min(region[2], w),
                                min(region[3], h)
                            )
                            
                            # 截取匹配区域进行OCR识别
                            task_screenshot = pyautogui.screenshot(region=ocr_region)
                            screenshot_np = np.array(task_screenshot)
                            
                            # 使用RapidOCR识别文字
                            ocr_result, _ = self.ocr(screenshot_np)
                            
                            # 检查是否有识别结果
                            task_text = ""
                            if ocr_result:
                                # 提取所有识别到的文字
                                texts = [text_info[1] for text_info in ocr_result if len(text_info) > 1]
                                task_text = " ".join(texts)
                                print(f"[主循环-重新识别] 识别到的文字: {task_text}")
                                
                                # 根据重新识别的文字判断任务类型
                                if "完成" in task_text or "回去" in task_text:
                                    task_type = "完成"
                                    full_text = task_text
                                    success = self.execute_task_by_type(task_type, full_text, region)
                                elif "巡逻" in task_text or "附近" in task_text:
                                    task_type = "巡逻"
                                    full_text = task_text
                                    patrol_service = PatrolService(self, region, self.ocr, ShimenNavigationService(), self.sect_config)
                                    success = patrol_service.execute(full_text)
                                elif "买到" in task_text or "送给" in task_text:
                                    task_type = "寻物"
                                    full_text = task_text
                                    find_item_service = FindItemService(region, self, self.ocr, ShimenNavigationService(), self.sect_config)
                                    success = find_item_service.execute(full_text)
                                elif "抓" in task_text or "捕捉" in task_text:
                                    task_type = "捕捉"
                                    full_text = task_text
                                    capture_service = CaptureService(region, self, self.ocr, ShimenNavigationService(), self.sect_config)
                                    success = capture_service.execute(full_text)
                break
                    
        except Exception as e:
            print(f"[主循环] 发生异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            print("[主循环] 线程退出")

    def parse_shimen_task(self, region):
        """
        解析师门任务信息
        """
        try:
            # 先查找师门任务图标的位置
            template_path = "public/shimen/task/task.png"
            template = cv2.imread(template_path)
            
            if template is None:
                print(f"[parse_shimen_task] 无法读取模板图片 {template_path}")
                return "无法读取模板图片", ""
            
            # 截取整个窗口区域
            screenshot = pyautogui.screenshot(region=region)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 在窗口截图中匹配模板
            res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            threshold = 0.3
            if max_val >= threshold:
                # 计算匹配区域的坐标（相对于整个屏幕）
                h, w = template.shape[:2]
                top_left = (region[0] + max_loc[0], region[1] + max_loc[1])
                bottom_right = (top_left[0] + w, top_left[1] + h)
                
                # 定义一个稍微扩大一点的区域用于OCR识别
                # 扩大50像素范围以确保包含完整任务信息
                ocr_region = (
                    max(region[0], top_left[0]),
                    max(region[1], top_left[1]),
                    min(region[0] + region[2], w),
                    min(region[1] + region[3], h)
                )
                
                # 截取匹配区域进行OCR识别
                task_screenshot = pyautogui.screenshot(region=ocr_region)
                screenshot_np = np.array(task_screenshot)
                
                # 保存调试图片
                debug_filename = f"shimen_parse_{int(time.time())}.png"
                debug_filepath = os.path.join(self.debug_image_path, debug_filename)
                task_screenshot.save(debug_filepath)
                print(f"[parse_shimen_task] 调试图片已保存: {debug_filepath}")
                
                # 使用RapidOCR识别文字
                ocr_result, _ = self.ocr(screenshot_np)
                
                # 检查是否有识别结果
                if ocr_result:
                    # 提取所有识别到的文字
                    texts = [text_info[1] for text_info in ocr_result if len(text_info) > 1]
                    full_text = " ".join(texts)
                    print(f"[parse_shimen_task] 识别到的文字: {full_text}")
                    if "抓到" in full_text or "抓" in full_text:
                        return "捕捉", full_text
                    elif "寻" in full_text or "物" in full_text:
                        # 执行找物品的任务逻辑
                        return "寻物", full_text
                    elif "附近" in full_text or "逻" in full_text:
                        # 执行巡逻任务逻辑
                        return "巡逻", full_text
                    else:
                        return "未知", full_text
                else:
                    print("[parse_shimen_task] 未识别到任何文字")
                    return "未识别到任务信息", ""
            else:
                print(f"[parse_shimen_task] 未能在窗口中找到任务图标模板，最高匹配度: {max_val:.2f}")
                return "未找到任务图标", ""
        except Exception as e:
            print(f"[parse_shimen_task] 解析任务信息出错: {str(e)}")
            return "解析任务信息失败", ""

    def record_task_result(self, result_text):
        """
        记录任务执行结果
        """
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            log_entry = {
                "name": "师门任务",
                "result": result_text,
                "timestamp": timestamp
            }
            
            self.results.append(log_entry)
            self.save_results()
            print(f"[记录] 已保存任务日志: {result_text}")
        except Exception as e:
            print(f"[记录] 记录任务结果出错: {str(e)}")
    
    def return_to_master(self):
        """
        返回师门交任务
        """
        print("开始返回师门交任务...")
        # 这里应该调用导航服务返回师门
        navigation_service = ShimenNavigationService()
        # 重新实现返回师门的逻辑
        print("已返回师门并完成任务提交")
