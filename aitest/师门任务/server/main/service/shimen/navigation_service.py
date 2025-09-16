# 师门导航服务
import pyautogui
import time
from rapidocr_onnxruntime import RapidOCR
import cv2
import numpy as np
from ..utils.window_utils import find_and_click_template

class ShimenNavigationService:
    def __init__(self):
        # 初始化 OCR 引擎
        self.ocr = RapidOCR()
    
    def navigate_to_shimen_interface(self, region, notice, gohome, shifu, sect_config=None):
        """
        导航到师门任务界面
        :param region: 窗口区域
        :param notice: 法术提示图片路径
        :param gohome: 回门派技能图片路径
        :param shifu: 师父NPC图片路径
        :param sect_config: 门派配置信息
        """
        print("导航到师门任务界面")
        
        # 从配置中获取师傅目标图片路径，如果没有则使用默认路径
        shifuaim = sect_config.get("shifuaim") if sect_config else None
        if not shifuaim:
            shifuaim = "public/shimen/task/shifuaim.png"
        
        # 先检查是否已经存在师傅按钮，如果存在直接点击
        if find_and_click_template(region, shifuaim, 0.4):
            print("[导航服务] 检测到师傅图片，已直接点击")
            time.sleep(1)
            # 检测到师傅图片并点击后，需要继续执行领取任务操作
            self.find_and_click_shimen_task(region)
            return
        
        # 点击底部法术
        find_and_click_template(region, notice, 0.6)
        time.sleep(0.2)
        # 点回门派技能
        find_and_click_template(region, gohome, 0.6)
        time.sleep(0.2)
        # 点击左上角找显示地图
        find_and_click_template(region, "public/shimen/task/showmap.png", 0.3)
        time.sleep(1)
        # 打开npc查找系统
        find_and_click_template(region, "public/shimen/task/mappeople.png", 0.6)
        time.sleep(1)
        # 点击师门师傅名字信息
        find_and_click_template(region, shifu, 0.7)
        time.sleep(1)
        # 点击寻路按钮
        find_and_click_template(region, "public/shimen/task/findbtn.png", 0.7)
            
        # 循环判断师傅图片在当前界面中是否存在，不存在就一直循环监听每间隔3秒监听一次
        max_wait_time = 30  # 最大等待时间30秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            if find_and_click_template(region, shifuaim, 0.4):
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
        if find_and_click_template(region, "public/shimen/task/tasklist.png", 0.1):
            print("[导航服务] 显示领取任务的列表")
            time.sleep(1)
            find_and_click_template(region, "public/shimen/task/gettask.png", 0.7)
            print("[导航服务] 成功点击领取任务按钮")
            time.sleep(1)
            # 点击对话的关闭按钮
            find_and_click_template(region, "public/shimen/task/close.png", 0.7)
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