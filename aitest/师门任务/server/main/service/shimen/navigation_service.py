# 师门导航服务
import pyautogui
import time
from rapidocr_onnxruntime import RapidOCR
import cv2
import re
import numpy as np
from ..utils.window_utils import find_and_click_template
from ..utils.window_utils import find_window_by_title, find_and_click_template, ocr_text_in_region_with_rapidocr, ocr_text_in_template_area, click_top_center, get_window_position, match_and_click_template
from ..utils.config import window_title, animal_shop_list
class ShimenNavigationService:
    def __init__(self):
        # 初始化 OCR 引擎
        self.ocr = RapidOCR()
    
    def navigate_to_shimen_interface(self, sect_config=None):
        """
        导航到师门任务界面
        :param region: 窗口区域
        :param gohome: 回门派技能图片路径
        :param shifu: 师父NPC图片路径
        :param sect_config: 门派配置信息
        """
        print("导航到师门任务界面")
        hwnd = find_window_by_title(window_title)
        region = get_window_position(hwnd)

        
        # 先检查是否已经存在师傅按钮，如果存在直接点击
        if find_and_click_template(sect_config.get("shifuaim"), 0.4):
            print("[导航服务] 检测到师傅图片，已直接点击")
            time.sleep(1)
            # 检测到师傅图片并点击后，需要继续执行领取任务操作
            self.find_and_click_shimen_task(region)
            return
        
        # 点击底部法术
        find_and_click_template("public/shimen/task/notice.png", 0.5)
        time.sleep(0.2)
        # 点回门派技能
        find_and_click_template(sect_config.get("gohome"), 0.6)
        time.sleep(2)
        # 点击师门任务会自动寻路
        find_and_click_template("public/shimen/task/task.png", 0.3)
        time.sleep(1)
        # 监听界面左上角的文字循环监听直到出现对应文字后停止
        if find_and_click_template(sect_config.get("shifuaim"), 0.7):
            print("[导航服务] 检测到师父图片，已点击")
            time.sleep(1)
            # 检测到师父图片并点击后，需要继续执行领取任务操作
            self.find_and_click_shimen_task(region)
            return
        time.sleep(0.2)

        # # 点击左上角找显示地图
        # find_and_click_template(region, "public/shimen/task/showmap.png", 0.3)
        # time.sleep(1)
        # # 打开npc查找系统
        # find_and_click_template(region, "public/shimen/task/mappeople.png", 0.6)
        # time.sleep(1)
        # # 点击师门师傅名字信息
        # find_and_click_template(region, shifu, 0.7)
        # time.sleep(1)
        # 点击寻路按钮
        # find_and_click_template(region, "public/shimen/task/findbtn.png", 0.7)
            
        # 循环判断师傅图片在当前界面中是否存在，不存在就一直循环监听每间隔3秒监听一次
        max_wait_time = 30  # 最大等待时间30秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            if find_and_click_template(sect_config.get("shifuaim"), 0.4):
                print("[导航服务] 检测到师傅图片，已点击")
                break
            else:
                print("[导航服务] 未检测到师傅图片，3秒后继续监听...")
                time.sleep(3)
    
    def find_and_click_shimen_task(self, region):
        """
        查找并点击师门任务
        """
        print("查找并点击师门任务")
        # 判断是否出现可以点击的任务列表
        if find_and_click_template("public/shimen/task/tasklist.png", 0.1):
            print("[导航服务] 显示领取任务的列表")
            time.sleep(1)
            find_and_click_template("public/shimen/task/gettask.png", 0.7)
            print("[导航服务] 成功点击领取任务按钮")
            time.sleep(1)
            # 点击对话的关闭按钮
            find_and_click_template( "public/shimen/task/close.png", 0.7)
            time.sleep(1)
            return True
        return False
    
    def is_shimen_interface(self, screenshot):
        """
        判断当前是否为师门界面
        :param screenshot: 屏幕截图
        :return: 是否为师门界面
        """
        # 这里可以添加判断是否为师门界面的逻辑
        return False
    def go_to_item_location(self, item_name, sect_config=None):
        """
        导航到物品位置
        """
        print('导航到对应的商店%s' % item_name)
def extract_task_info(text):
    """
    从OCR识别的文本中提取师门任务信息
    
    Args:
        text (str): OCR识别出的完整文本
        
    Returns:
        dict: 包含已完成任务数和总任务数的字典
    """
    # 匹配"今日已完成X/Y"模式
    match = re.search(r'今日已完成(\d+)/(\d+)', text)
    if match:
        completed_count = int(match.group(1))
        total_count = int(match.group(2))
        return {
            'completed': completed_count,
            'total': total_count,
            'remaining': total_count - completed_count
        }
    else:
        return {
            'completed': -1,
            'total': -1,
            'remaining': -1
        }