import os
import pyautogui
import time
import json
from rapidocr_onnxruntime import RapidOCR
import threading
import keyboard

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
        
        # 键盘监听线程
        self.keyboard_thread = None
        
        # 设置结果文件路径为public/autologin/result.json
        self.result_file_path = "public/autologin/result.json"
        
        # 加载历史结果
        self.load_results()

    def load_results(self):
        """
        加载历史签到结果
        """
        try:
            # 使用新的结果文件路径
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
            # 使用新的结果文件路径
            with open(self.result_file_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存结果出错: {str(e)}")

    def find_drag_area_and_scroll(self, region, drag_area_template, character_names, threshold=0.7):
        """
        匹配拖拽区域并实现上下滚动功能
        """
        global aimData, current_character_index
        
        # 1. 匹配拖拽区域
        print("[find_drag_area_and_scroll] 开始匹配拖拽区域...")
        drag_area_matched = self.find_and_click_template(region, drag_area_template, threshold)
        
        if drag_area_matched:
            print("[find_drag_area_and_scroll] 成功匹配拖拽区域")
            
            # 2. 循环查找角色名
            max_scroll_attempts = 40  # 最大拖拽次数
            scroll_count = 0
            
            while scroll_count < max_scroll_attempts and not self.stop_event.is_set() and self.running:
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
                    time.sleep(0.5)
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
                    self.drag_from_to(start_x, start_y, end_x, end_y)
                    time.sleep(0.5)
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
        time.sleep(0.1)

    def start(self):
        """启动自动签到"""
        if not self.running:  # 防止重复启动
            self.running = True
            self.stop_event.clear()  # 重置停止事件
            print("提示: 按 F1 启动脚本，按 F2 停止脚本")
            # 启动键盘监听线程
            self.keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
            self.keyboard_thread.start()
            self.main_loop()

    def stop(self):
        """停止自动签到"""
        self.running = False
        self.stop_event.set()
        print("\n===== 脚本已停止 =====")


    def get_status(self):
        """获取运行状态"""
        return {
            "running": self.running,
            "current_character_index": self.current_character_index,
            "aim_data": self.aimData
        }

    def get_results(self):
        """获取签到结果"""
        self.load_results()  # 重新加载文件中的结果
        return self.results

    def keyboard_listener(self):
        """键盘监听器"""
        print("键盘监听已启动: F1=开始, F2=停止")
        while True:
            # 监听F1键启动
            keyboard.wait('f1')
            if not self.running:
                print("\n[F1] 按键被按下，启动脚本...")
                self.start()
            
            # 监听F2键停止
            keyboard.wait('f2')
            if self.running:
                print("\n[F2] 按键被按下，停止脚本...")
                self.stop()

    def main_loop(self):
        """主循环函数"""
        template_path = "public/autologin/1.png"  # 今日礼包
        template_path2 = "public/autologin/2.png"  # 去签到
        close1 = "public/autologin/3.png"  # 今日礼包关闭
        more = "public/autologin/more.png"  # 更多按钮
        rolebtn = "public/autologin/4.png"  # 领奖角色按钮
        index = 0
        print(f"[主循环] 正在监听窗口: {self.window_title}")
        
        while not self.stop_event.is_set():
            if self.running:
                hwnd = self.find_window_by_title(self.window_title)
                if hwnd:
                    print(f"[主循环] 找到窗口句柄: {hwnd}")
                    
                    # 获取窗口区域
                    region = self.get_window_position(hwnd)  # 返回 (x, y, width, height)
                    print(f"[主循环] 窗口区域: {region}")
                    
                    # 检查窗口是否最小化
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        time.sleep(0.05)
                    
                    # 激活窗口
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                    except:
                        pass
                    if index == 0:
                        time.sleep(0.1)
                        # 点击窗口顶部激活窗口
                        self.click_top_center(hwnd)
                        index = 1
                    else:
                        pass

                    
                    # 在窗口区域内查找并点击模板
                    print("[主循环] 开始查找模板...")
                    found_today_gift = False
                    
                    # 循环查找第一个模板直到找到为止
                    while not self.stop_event.is_set() and self.running:
                        success = self.find_and_click_template(region, template_path, 0.8)
                        if success:
                            print("[主循环] 成功点击今日礼包")
                            time.sleep(2)
                            found_today_gift = True
                            break
                        else:
                            print("[主循环] 未找到今日礼包，1秒后继续查找...")
                            time.sleep(1)
                    
                    # 只有在找到今日礼包的情况下才继续执行后续操作
                    if not found_today_gift:
                        continue
                    
                    # 如果脚本仍在运行，继续查找第二个对话模板去签到按钮点击
                    if not self.stop_event.is_set() and self.running:
                        # 添加一个标志来控制是否需要重新开始主循环
                        restart_main_loop = False
                        while not self.stop_event.is_set() and self.running and not restart_main_loop:
                            success2 = self.find_and_click_template(region, template_path2, 0.7)
                            if success2:
                                print("[主循环] 点击去签到按钮")
                                time.sleep(5)
                                break
                            else:
                                print("[主循环] 未找到去签到按钮，1秒后继续查找...")
                                # 增加角色索引以匹配下一个角色
                                self.current_character_index += 1
                                
                                # 检查是否已经遍历完所有角色
                                if self.current_character_index >= len(self.userlist):
                                    print("[主循环] 已遍历完所有角色，程序结束")
                                    # 停止脚本运行
                                    self.running = False
                                    return  # 退出主循环函数
                                
                                # 未找到去签到按钮，就关闭今日礼包
                                self.find_and_click_template(region, close1, 0.8)
                                time.sleep(1)
                                # 点击更多按钮
                                self.find_and_click_template(region, more, 0.8)
                                time.sleep(1)
                                # 点击领奖角色按钮
                                self.find_and_click_template(region, rolebtn, 0.3)
                                time.sleep(1)
                                # 处理拖拽区域（新添加的功能）
                                drag_area_template = "public/autologin/drag_area.png"
                                self.find_drag_area_and_scroll(region, drag_area_template, self.userlist, 0.3)
                                time.sleep(1)
                                # 点击领取奖励按钮
                                self.find_and_click_template(region, "public/autologin/5.png", 0.3)
                                time.sleep(1)
                                # 处理完拖拽区域后，设置标志以重新开始主循环而不是继续向下执行
                                restart_main_loop = True
                                break
                        
                        # 如果设置了重新开始主循环的标志，则跳过后续代码，使用continue重新开始主循环
                        if restart_main_loop:
                            continue
                            
                    # 点击出现的弹框奖励领取成功，开心收下
                    while not self.stop_event.is_set() and self.running:
                        success = self.find_and_click_template(region, 'public/autologin/7.png', 0.8)
                        if success:
                            print("[主循环] 点击出现的弹框奖励领取成功，开心收下")
                            time.sleep(5)
                            break
                        else:
                            print("[主循环] 未找到点击出现的弹框奖励领取成功，开心收下，1秒后继续查找...")
                            time.sleep(3)
                            break
                            
                    # 点击去抽奖的按钮
                    while not self.stop_event.is_set() and self.running:
                        success = self.find_and_click_template(region, 'public/autologin/6.png', 0.8)
                        if success:
                            print("[主循环] 点击去抽奖的按钮")
                            time.sleep(3)
                            break
                        else:
                            print("[主循环] 未找到点击出现的弹框奖励领取成功，开心收下的按钮，1秒后继续查找...")
                            time.sleep(3)
                            break
                            
                    # 点击出现的奖励领取成功开心收下弹框
                    while not self.stop_event.is_set() and self.running:
                        success = self.find_and_click_template(region, 'public/autologin/7.png', 0.8)
                        if success:
                            print("[主循环] 点击开心收下的按钮")
                            
                            # 识别goods.png所在区域的文字并保存到日志文件
                            try:
                                # 获取指定窗口区域
                                hwnd = self.find_window_by_title(self.window_title)
                                
                                if hwnd:
                                    # 获取窗口区域
                                    window_region = self.get_window_position(hwnd)
                                    print(f"[识别奖励] 窗口区域: {window_region}")
                                    
                                    # 先截取整个窗口用于匹配goods.png
                                    window_screenshot = pyautogui.screenshot(region=window_region)
                                    
                                    # 查找goods.png模板在窗口中的位置
                                    goods_template_path = "public/autologin/goods.png"
                                    template = cv2.imread(goods_template_path)
                                    if template is not None:
                                        # 将PIL图像转换为OpenCV格式
                                        open_cv_image = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
                                        
                                        # 在窗口截图中匹配goods.png模板
                                        res = cv2.matchTemplate(open_cv_image, template, cv2.TM_CCOEFF_NORMED)
                                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                                        
                                        threshold = 0.8
                                        if max_val >= threshold:
                                            # 计算匹配区域的坐标（相对于整个屏幕）
                                            h, w = template.shape[:2]
                                            top_left = (window_region[0] + max_loc[0], window_region[1] + max_loc[1])
                                            bottom_right = (top_left[0] + w, top_left[1] + h)
                                            
                                            # 截取匹配区域（基于屏幕绝对坐标）
                                            goods_region = (top_left[0], top_left[1], w, h)
                                            goods_screenshot = pyautogui.screenshot(region=goods_region)
                                            
                                            # 对截取的区域进行OCR识别
                                            img = cv2.cvtColor(np.array(goods_screenshot), cv2.COLOR_RGB2BGR)
                                            ocr_result, elapse = self.ocr(img)
                                            
                                            print("[主循环] goods.png区域OCR识别结果:")
                                            full_text = ""
                                            if ocr_result:
                                                recognized_texts = [text_info[1] for text_info in ocr_result if text_info and len(text_info) > 1]
                                                full_text = "\n".join(recognized_texts)
                                                for line in recognized_texts:
                                                    print(line)  # 输出识别的文字
                                            else:
                                                print("[主循环] 未识别到文字")
                                                full_text = "未识别到文本"
                                            
                                            # 获取当前时间戳
                                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                            
                                            # 创建日志条目
                                            log_entry = {
                                                "name": self.aimData,
                                                "result": full_text,
                                                "timestamp": timestamp
                                            }
                                            
                                            # 添加新条目
                                            self.results.append(log_entry)
                                            
                                            # 保存到日志文件
                                            self.save_results()
                                            print(f"[主循环] 已保存奖励日志: {self.aimData}")
                                        else:
                                            print(f"[主循环] 未能在窗口中找到goods.png模板，最高匹配度: {max_val:.2f}")
                                            # 记录未匹配到模板的情况
                                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                            log_entry = {
                                                "name": self.aimData,
                                                "result": "未匹配到对应区域",
                                                "timestamp": timestamp
                                            }
                                            
                                            self.results.append(log_entry)
                                            self.save_results()
                                            print(f"[主循环] 已保存奖励日志: {self.aimData}")
                                    else:
                                        print(f"[主循环] 无法读取模板图片 {goods_template_path}")
                                else:
                                    print(f"[主循环] 未找到窗口: {self.window_title}")
                            except Exception as e:
                                print(f"[主循环] goods.png区域文字识别出错: {str(e)}")
                                import traceback
                                traceback.print_exc()
                            
                            # 在OCR识别之后再点击开心收下按钮
                            time.sleep(0.5)
                            break
                        else:
                            print("[主循环] 未找到点击出现的奖励领取成功开心收下弹框，1秒后继续查找...")
                            time.sleep(2)
                    
                    print("[主循环] 等待下一次扫描...")
                else:
                    print("[主循环] 未找到窗口")
                
                # 等待1秒再进行下一次扫描
                for i in range(20, 0, -1):
                    if not self.running or self.stop_event.is_set():
                        break
                    print(f"\r[主循环] 下次扫描倒计时: {i/10:.1f}秒", end="", flush=True)
                    time.sleep(0.1)
                print("\r" + " " * 30, end="\r")
            else:
                # 脚本停止状态，每秒检查一次
                time.sleep(0.1)
