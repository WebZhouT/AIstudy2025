# 巡逻任务服务  
import pyautogui
import time
from rapidocr_onnxruntime import RapidOCR
import cv2
import numpy as np
from ..utils.window_utils import find_and_click_template
import random  # 新增: 导入random模块
# 键盘虚拟按键
area = [
    {
      'name':"1",
      'png':"public/shimen/task/keyboard/1.png"
    },    
    
    {
      'name':"2",
      'png':"public/shimen/task/keyboard/2.png"
    },{
      'name':"3",
      'png':"public/shimen/task/keyboard/3.png"
    },
    {
      'name':"4",
      'png':"public/shimen/task/keyboard/4.png"
    },
    {
      'name':"5",
      'png':"public/shimen/task/keyboard/5.png"
    },
    {
      'name':"6",
      'png':"public/shimen/task/keyboard/6.png"
    },
    {
      'name':"7",
      'png':"public/shimen/task/keyboard/7.png"
    },
    {
      'name':"8",
      'png':"public/shimen/task/keyboard/8.png"
    },
    {
      'name':"9",
      'png':"public/shimen/task/keyboard/9.png"
    },
    {
      'name':"0",
      'png':"public/shimen/task/keyboard/0.png"
    }
]

class PatrolService:
    # 初始化 OCR 引擎
    def __init__(self, game_control, ocr_service, navigation_service, sect_config=None):
        self.game_control = game_control
        self.ocr_service = ocr_service
        self.navigation_service = navigation_service
        self.sect_config = sect_config
        # 初始化 OCR 引擎
        self.ocr = RapidOCR()
        # 新增: 添加running属性
        self.running = True
        # 新增: 添加region属性占位符，实际使用时应该从game_control获取
        self.region = None
    
    def execute(self, full_text):
        """
        执行巡逻任务
        """
        print("开始执行巡逻任务...")
        print(f"任务描述: {full_text}")
        
        # 实际的巡逻任务逻辑
        self.start_patrol()
        return True
        
    def start_patrol(self):
        """
        启动巡逻任务
        """
        print("启动巡逻任务")
        # 这里可以添加实际的巡逻逻辑
        # 例如：点击自动寻路、等待一段时间等
        # 从配置中获取师傅目标图片路径，如果没有则使用默认路径
        gohome = self.sect_config.get("gohome") if self.sect_config else None
        if not gohome:
            gohome = "public/shimen/task/shifuaim.png"
        # 先回到门派地图
        notice = "public/shimen/task/notice.png"  # 法术提示    
        # 点击底部法术
        find_and_click_template(self.region, notice, 0.6)
        time.sleep(0.2)
        # 点回门派技能
        find_and_click_template(self.region, gohome, 0.6)
        time.sleep(0.2)
        # 门派寻路（随机位置）
        # 回门派后，判断人物在地图中的位置(获取当前的巡逻坐标，"PatrolCoordinates": [
        #   [
        #     "97",
        #     "64"
        #   ],
        #   [
        #     "22",
        #     "48"
        #   ]
        # ])
        PatrolCoordinates = self.sect_config.get("PatrolCoordinates") if self.sect_config else None
        # 解析巡逻坐标，比如第一个坐标x是97，y是64
        # 点击左上角找显示地图
        find_and_click_template(self.region, "public/shimen/task/showmap.png", 0.3)
        time.sleep(1)
        # 传入获得的PatrolCoordinates中的随机一个坐标
        # input_coordinates_via_keyboard()
        # 修改: 从PatrolCoordinates中获取一个随机坐标并调用input_coordinates_via_keyboard
        if PatrolCoordinates and len(PatrolCoordinates) > 0:
            # 随机选择一个坐标
            random_coordinate = random.choice(PatrolCoordinates)
            print(f"选择的巡逻坐标: {random_coordinate}")
            # 调用坐标输入方法
            self.input_coordinates_via_keyboard(random_coordinate)
        else:
            print("未找到有效的巡逻坐标")
        pass
        
        # 添加: 检查任务是否完成，如果未完成则重新启动巡逻
        if not self.check_task_completion("public/shimen/task/task.png", 0.4):
            print("任务未完成，重新启动巡逻任务")
            self.start_patrol()
        else:
            print("任务已完成")
            self.stop_patrol()
    
    def stop_patrol(self):
        """
        停止巡逻任务
        """
        print("停止巡逻任务")
        # 设置running为False以停止所有循环监听
        self.running = False
        # 这里可以添加停止巡逻的其他逻辑
        pass
    
    def input_coordinates_via_keyboard(self, coordinate):
        """
        根据坐标值点击数字键盘图片输入坐标
        
        参数:
        coordinate: 坐标数组 [x, y]
        """
        # 新增: 声明全局变量
        global extracted_coordinate  
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
                    self.find_and_click_image(key_info['png'], confidence=0.5)
                    time.sleep(0.3)  # 添加点击后的延迟
                    break
        #点击确认按钮
        self.find_and_click_image('public/shimen/task/keyboard/sure.png', confidence=0.5) 
        time.sleep(1)     
        # # 点击Y坐标输入框（假设存在ybtn.png图片）
        # self.find_and_click_image('ybtn.png', confidence=0.8)
        # time.sleep(2)
        
        # 输入Y坐标
        print(f"正在输入Y坐标: {y}")
        for digit in str(y):
            # 查找对应的数字图片并点击
            for key_info in area:
                if key_info['name'] == digit:
                    self.find_and_click_image(key_info['png'], confidence=0.98)
                    time.sleep(1)  # 添加点击后的延迟
                    break
        #点击确认按钮
        self.find_and_click_image('public/shimen/task/keyboard/sure.png', confidence=0.85) 
        time.sleep(3) 
        print("坐标输入完成")
        # 点击关闭地图按钮
        self.find_and_click_image('public/shimen/task/closemap.png', confidence=0.95)
        # 坐标输入完成后，启动自动寻路监听
        self.listen_for_navigation_coordinates()
        time.sleep(1) 
        # 如果当前界面有关闭按钮（比如战斗结束后会出现对话框，需要点击关闭）# 如果存在关闭按钮
        self.find_and_click_image('public/shimen/task/keyboard/close.png', confidence=0.8, region=self.region)
        time.sleep(0.2)  # 等待关闭按钮点击完成
        
        # 判断当前任务是否完成，如果没有完成重新调起巡逻任务
        # if not self.is_task_completed():  # 假设is_task_completed()方法判断任务是否完成
        #     print("任务未完成，重新启动巡逻任务")
        #     self.start_patrol()
        # else:
        #     print("任务已完成")

    def listen_for_navigation_coordinates(self):
        """
        坐标输入完成后，每隔3秒进行指定区域的图像识别，
        监听界面中指定区域进行文本识别，识别出来的文字需要包含对应坐标
        """
        # 新增: 声明全局变量
        global extracted_coordinate  
        print("开始监听导航坐标...")
        
        # 定义要识别的区域 (需要根据实际界面调整)
        # 这里假设在屏幕左上角区域
        # target_region = (50, 50, 300, 100)  # left, top, width, height
        
        # 修改: 使用areabtn.png图片定位区域
        area_btn_location = None
        try:
            area_btn_location = pyautogui.locateOnScreen('public/shimen/task/showmap.png', confidence=0.3)
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
            if not self.running:
                break
                
            try:
                # 截取指定区域
                screenshot = pyautogui.screenshot(region=target_region)
                temp_image = "temp_navigation_screenshot.png"  # 修改: 使用固定文件名
                screenshot.save(temp_image)
                
                # OCR识别（识别当前人物所在坐标）
                result, _ = self.ocr(temp_image)
                
                if result:
                    recognized_text = '\n'.join([item[1] for item in result])
                    print(f"第{i+1}次监听结果: {recognized_text}")
                    
                    # 检查本次识别结果与上次是否相同
                    if previous_result is not None and previous_result == recognized_text:
                        same_count += 1
                        print(f"识别结果连续 {same_count} 次相同")
                        # 判断当前是否存在战斗状态图片，如果存在，就跳出循环监听。
                        try:
                            area_btn_location = pyautogui.locateOnScreen('public/shimen/task/autowar.png', confidence=0.6, region=self.region)  # 修改: 补全路径
                            area_btn_location2 = pyautogui.locateOnScreen('public/shimen/task/war.png', confidence=0.6, region=self.region)  # 修改: 补全路径
                            print(f"areabtn.png位置: {area_btn_location}")
                            # 如果area_btn_location存在或者area_btn_location2存在，则判定进入战斗状态跳出循环。不再监听
                            if area_btn_location or area_btn_location2:  
                                print("进入战斗状态，跳出坐标监听")  # 添加输出
                                return True
                        except pyautogui.ImageNotFoundException:
                            area_btn_location = None
                            print("未找到areabtn.png")
                        # 如果连续2次识别结果相同，则认为已到达目标
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

    def find_and_click_image(self, image_path, confidence=0.8):
        """
        查找并点击图片
        """
        return find_and_click_template(self.region, image_path, confidence)

    def check_task_completion(self, image_path, confidence):
        """
        检查任务是否完成
        :param image_path: 用于判断任务完成的图片路径
        :param confidence: 图像识别相似度
        :return: True表示任务完成，False表示未完成
        """
        print("检查任务完成状态...")
        
        # 查找指定图片在当前窗口区域的位置
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=self.region)
            if location:
                print(f"找到任务完成指示图片，位置: {location}")
                
                # 截取该区域进行OCR识别
                screenshot = pyautogui.screenshot(region=(
                    int(location.left),
                    int(location.top),
                    int(location.width),
                    int(location.height)
                ))
                temp_image = "temp_task_completion_screenshot.png"
                screenshot.save(temp_image)
                
                # 使用RapidOCR识别文字
                result, _ = self.ocr(temp_image)
                
                if result:
                    task_text = '\n'.join([item[1] for item in result])
                    print(f"[主循环] 识别到的文字: {task_text}")
                    # 根据识别到的文字判断任务是否完成
                    # 这里可以根据实际需求添加具体的判断逻辑
                    if "完成" in task_text or "回去" in task_text:
                        return True
                return False
            else:
                print("未找到任务完成指示图片")
                return False
        except Exception as e:
            print(f"检查任务完成状态时出现错误: {e}")
            return False
