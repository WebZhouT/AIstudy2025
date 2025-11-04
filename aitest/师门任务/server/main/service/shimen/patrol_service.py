# 巡逻任务服务  
import pyautogui
import time
from rapidocr_onnxruntime import RapidOCR
import cv2
import numpy as np
from ..utils.window_utils import find_window_by_title, find_and_click_template,ocr_text_in_template_area
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
    def __init__(self, game_control, region, ocr_service, navigation_service, sect_config=None):
        self.game_control = game_control
        self.region = region  # 直接接收 region 参数
        self.ocr_service = ocr_service
        self.navigation_service = navigation_service
        self.sect_config = sect_config
        # 初始化 OCR 引擎
        self.ocr = RapidOCR()
        # 新增: 添加running属性
        self.running = True
        # 新增：添加extracted_coordinate作为实例变量
        self.extracted_coordinate = None
        # 新增：添加所有巡逻坐标和已用坐标
        self.all_patrol_coordinates = []
        self.used_coordinates = []
        
    def execute(self, full_text):
        """
        执行巡逻任务
        """
        print("开始执行巡逻任务...")
        print(f"任务描述: {full_text}")
        
        # 初始化巡逻坐标
        self.initialize_patrol_coordinates()
        
        # 实际的巡逻任务逻辑
        self.start_patrol()
        return True
        
    def initialize_patrol_coordinates(self):
        """初始化巡逻坐标"""
        PatrolCoordinates = self.sect_config.get("PatrolCoordinates") if self.sect_config else None
        if PatrolCoordinates:
            self.all_patrol_coordinates = PatrolCoordinates.copy()
            self.used_coordinates = []
            print(f"初始化巡逻坐标: {self.all_patrol_coordinates}")
        
    def get_random_coordinate(self):
        """获取一个随机的未使用坐标"""
        available_coords = [coord for coord in self.all_patrol_coordinates if coord not in self.used_coordinates]
        
        if not available_coords:
            # 如果所有坐标都已使用，重置已用坐标列表
            print("所有坐标已使用过，重置坐标列表")
            self.used_coordinates = []
            available_coords = self.all_patrol_coordinates.copy()
        
        if available_coords:
            random_coordinate = random.choice(available_coords)
            self.used_coordinates.append(random_coordinate)
            return random_coordinate
        else:
            return None
        
    def start_patrol(self):
        """
        启动巡逻任务
        """
        if not self.running:
            return
            
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
        self.find_and_click_template(notice, 0.5)
        time.sleep(0.2)
        # 点回门派技能
        self.find_and_click_template(gohome, 0.5)
        time.sleep(0.2)
        # 门派寻路（随机位置）
        # 回门派后，判断人物在地图中的位置
        # 点击左上角找显示地图
        self.find_and_click_template("public/shimen/task/showmap.png", 0.3)
        time.sleep(1)
        
        # 获取随机坐标并输入
        random_coordinate = self.get_random_coordinate()
        if random_coordinate:
            print(f"选择的巡逻坐标: {random_coordinate}")
            # 调用坐标输入方法
            self.input_coordinates_via_keyboard(random_coordinate)
        else:
            print("未找到有效的巡逻坐标")
            self.stop_patrol()
    
    def stop_patrol(self):
        """
        停止巡逻任务
        """
        print("停止巡逻任务")
        # 设置running为False以停止所有循环监听
        self.running = False
    
    def input_coordinates_via_keyboard(self, coordinate):
        """
        根据坐标值点击数字键盘图片输入坐标
        
        参数:
        coordinate: 坐标数组 [x, y]
        """
        if not coordinate or len(coordinate) != 2:
            print("坐标数据不正确")
            return
        
        x, y = coordinate
        self.extracted_coordinate = [x, y]  # 使用实例变量 
        
        # 输入X坐标
        print(f"正在输入X坐标: {x}")
        for digit in str(x):
            # 查找对应的数字图片并点击
            for key_info in area:
                if key_info['name'] == digit:
                    self.find_and_click_template(key_info['png'], confidence=0.5)
                    time.sleep(0.3)  # 添加点击后的延迟
                    break
        #点击确认按钮
        self.find_and_click_template('public/shimen/task/keyboard/sure.png', confidence=0.5) 
        time.sleep(1)     
        
        # 输入Y坐标
        print(f"正在输入Y坐标: {y}")
        for digit in str(y):
            # 查找对应的数字图片并点击
            for key_info in area:
                if key_info['name'] == digit:
                    self.find_and_click_template(key_info['png'], confidence=0.98)
                    time.sleep(1)  # 添加点击后的延迟
                    break
        #点击确认按钮
        self.find_and_click_template('public/shimen/task/keyboard/sure.png', confidence=0.85) 
        time.sleep(3) 
        print("坐标输入完成")
        # 点击关闭地图按钮
        self.find_and_click_template('public/shimen/task/closemap.png', confidence=0.75)  # 降低置信度
        
        # 坐标输入完成后，启动自动寻路监听
        navigation_result = self.listen_for_navigation_coordinates()
        
        # 根据导航结果决定下一步操作
        if navigation_result == "battle":
            print("进入战斗状态，等待战斗结束")
            self.wait_for_battle_end()
            # 战斗结束后重新选择坐标巡逻
            print("战斗结束，重新选择坐标巡逻")
            time.sleep(2)
            self.start_patrol()
        elif navigation_result == "arrived":
            print("成功到达目标坐标")
            # 到达目标后检查任务状态
            time.sleep(3)
            self.check_and_continue_patrol()
        else:
            print("导航监听超时，重新尝试")
            time.sleep(2)
            self.start_patrol()
            
    def find_and_click_template(self, template_path, confidence=0.8, region=None):
        """
        查找并点击模板图片的包装方法
        支持region参数
        """
        if region is None:
            region = self.region
        return find_and_click_template(template_path, confidence, region)
    
    def wait_for_battle_end(self):
        """等待战斗结束"""
        print("等待战斗结束...")
        battle_check_count = 0
        max_battle_checks = 60  # 最多检查60次，约3分钟
        
        while battle_check_count < max_battle_checks and self.running:
            try:
                # 检查战斗状态图片是否存在
                autowar_location = pyautogui.locateOnScreen('public/shimen/task/autowar.png', confidence=0.6, region=self.region)
                war_location = pyautogui.locateOnScreen('public/shimen/task/war.png', confidence=0.6, region=self.region)
                
                if not autowar_location and not war_location:
                    battle_check_count += 1
                    print(f"未检测到战斗状态 ({battle_check_count}/{max_battle_checks})")
                    # 连续3次未检测到战斗状态，认为战斗已结束
                    if battle_check_count >= 3:
                        print("战斗状态已结束")
                        return True
                else:
                    battle_check_count = 0  # 重置计数器
                    print("战斗仍在进行中...")
                    
            except pyautogui.ImageNotFoundException:
                battle_check_count += 1
                print(f"未找到战斗状态图片 ({battle_check_count}/{max_battle_checks})")
                if battle_check_count >= 3:
                    print("战斗状态已结束")
                    return True
            except Exception as e:
                # 捕获其他异常，比如尺寸不匹配等
                battle_check_count += 1
                print(f"战斗状态检查时出现异常: {e} ({battle_check_count}/{max_battle_checks})")
                if battle_check_count >= 3:
                    print("战斗状态已结束")
                    return True
                    
            time.sleep(3)  # 每3秒检查一次
            
        print("战斗等待超时")
        return False
    
    def check_and_continue_patrol(self):
        """检查任务状态并决定是否继续巡逻"""
        time.sleep(5)  # 等待任务状态更新
        hwnd = find_window_by_title(self.window_title)
        # 检查任务是否完成
        txt = ocr_text_in_template_area(hwnd, "public/shimen/task/task.png", 0.2)
        task_text = txt['text']
        if "任务完成" in txt['text']: 
            print("巡逻任务已完成")
            time.sleep(1)
            # 点击对话框的关闭按钮
            find_and_click_template("public/shimen/task/close.png", 0.4)
            time.sleep(2)
            # 结束，从头执行
            self.stop_patrol()
        else:
            print("巡逻任务未完成，继续巡逻")
            time.sleep(2)
            self.start_patrol()
    
    def listen_for_navigation_coordinates(self):
        """
        坐标输入完成后，每隔3秒进行指定区域的图像识别，
        监听界面中指定区域进行文本识别，识别出来的文字需要包含对应坐标
        
        返回:
        "arrived" - 到达目标坐标
        "battle" - 进入战斗状态
        "timeout" - 监听超时
        """
        if not self.extracted_coordinate:
            return "timeout"
            
        target_x, target_y = self.extracted_coordinate
        print("开始监听导航坐标...")
        
        # 修改: 使用areabtn.png图片定位区域
        area_btn_location = None
        try:
            area_btn_location = pyautogui.locateOnScreen('public/shimen/task/showmap.png', confidence=0.3)
            print(f"areabtn.png位置: {area_btn_location}")
        except pyautogui.ImageNotFoundException:
            area_btn_location = None
            print("未找到areabtn.png")
        except Exception as e:
            area_btn_location = None
            print(f"查找areabtn.png时出现错误: {e}")
        
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
            # 如果找不到areabtn.png，使用默认区域
            print("没找到监听区域，使用默认区域")
            # 使用窗口的左上角区域作为默认监听区域
            target_region = (
                self.region[0] + 50,
                self.region[1] + 50,
                200,
                100
            )
            print(f"使用默认监听区域: {target_region}")
        
        # 保存上一次识别的结果
        previous_result = None
        same_count = 0  # 连续相同结果计数器
        
        for i in range(20):  # 最多监听20次，约1分钟
            if not self.running:
                break
                
            try:
                # 检查战斗状态
                try:
                    autowar_location = pyautogui.locateOnScreen('public/shimen/task/autowar.png', confidence=0.6, region=self.region)
                    war_location = pyautogui.locateOnScreen('public/shimen/task/war.png', confidence=0.6, region=self.region)
                    if autowar_location or war_location:
                        print("检测到进入战斗状态，停止坐标监听")
                        return "battle"
                except pyautogui.ImageNotFoundException:
                    pass
                except Exception as e:
                    print(f"战斗状态检查时出现错误: {e}")
                
                # 检查区域尺寸是否有效
                if target_region[2] <= 0 or target_region[3] <= 0:
                    print("监听区域尺寸无效，跳过本次监听")
                    time.sleep(3)
                    continue
                
                # 截取指定区域
                screenshot = pyautogui.screenshot(region=target_region)
                temp_image = "temp_navigation_screenshot.png"
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
                        
                        # 如果连续2次识别结果相同，则认为已到达目标
                        if same_count >= 2:
                            print("识别结果连续2次未变化，判定已到达目标位置")
                            return "arrived"
                    else:
                        # 重置计数器
                        same_count = 0
                    
                    # 更新上一次的结果
                    previous_result = recognized_text
                    
                    # 检查是否包含坐标信息
                    import re
                    expected_coordinate_pattern = r'(?:[\w\W]*?[（(](\d+)[,，](\d+)[)）])|(\d+)\s+(\d+)|(?:[$$$(]*(\d+)[.,](\d+)[$$)]*)'
                    matches = re.findall(expected_coordinate_pattern, recognized_text)
                    
                    if matches:
                        print(f"检测到坐标信息: {matches}")
                        # 检查是否与提取的坐标匹配
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
                            return "arrived"
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
                                    if x == target_x and y == target_y:
                                        print(f"已到达目标坐标: {target_x},{target_y}")
                                        return "arrived"
                            except ValueError:
                                pass  # 如果转换失败，继续执行原有逻辑
                        
                        print("未检测到坐标信息")
                else:
                    print("未识别到任何文字")
                    
            except Exception as e:
                print(f"监听过程中出现错误: {e}")
                # 继续下一次循环，不中断监听
                
            # 等待3秒后继续
            time.sleep(3)
        
        print("导航监听超时")
        return "timeout"

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