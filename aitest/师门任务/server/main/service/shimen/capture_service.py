
# 引入窗口工具函数
from ..utils.window_utils import find_window_by_title,  find_and_click_template, find_template_in_window
from ..utils.keyboard import click_sequence_numbers
# 获取窗口等信息
from ..utils.config import window_title, animal_shop_list
from ..utils.changePageKeyBoard import click_numbers_on_keyboardPage
# 师门导航服务（当前未实现，直接写到代码里面了）
from .navigation_service import ShimenNavigationService,extract_task_info
# 引入窗口工具函数
from ..utils.window_utils import find_window_by_title, get_window_position, click_top_center, find_and_click_template,ocr_text_in_template_area

from .ocr_service import ShimenOCRService
import time
import pyautogui
import os
# 捕捉任务服务
class CaptureService:
    def __init__(self,ocr_service, sect_config=None):
        hwnd = find_window_by_title(window_title)
        region = get_window_position(hwnd)
        self.ocr_service = ocr_service
        self.region = region
        self.sect_config = sect_config
    def execute(self, full_text):
        """执行捕捉任务"""
        print("开始执行捕捉任务...")
        print(f"任务描述: {full_text}")
        
        # 1. 识别需要捕捉的怪物
        monster_name = self.recognize_monster_name(full_text)
        print(f"需要捕捉: {monster_name}")
        
        # 2. 导航到商会进行购买
        self.navigate_to_monster_map(monster_name)
        
        # 3. 寻找并下单购买动物
        self.capture_monster(monster_name)
        print("购买召唤兽流程，完成，执行回门派操作")
        navigation_service = ShimenNavigationService()
        navigation_service.navigate_to_shimen_interface(self.sect_config)
    
    def navigate_to_monster_map(self, monster_name):
        """导航到商会根据配置买动物"""
        # 查找匹配的店铺
        matching_shops = self.find_shops_for_monster(monster_name)
        if not matching_shops:
            print(f"未找到售卖 {monster_name} 的店铺")
            return False
        print(f"找到 {len(matching_shops)} 个售卖 {monster_name} 的店铺")
        # # 根据怪物名称选择对应地图
        # monster_maps = {
        #     "大海龟": "东海湾",
        #     "巨蛙": "东海湾",
        #     "强盗": "大唐国境",
        #     # 更多映射关系...
        # }
        # # 获取要捕捉的动物名称
        # getAnimalName = self.recognize_monster_name(monster_name)
        # target_map = monster_maps.get(monster_name, "东海湾")
        # print(f"导航到: {target_map}")
        # 如果本来就在商会旁边有商人的，那么直接点击商人就行了，不需要再去商会
        exit_Shop = find_and_click_template("public/shimen/task/capture/shop.png", 0.4)
        if exit_Shop:
          # 如果找到并点击了商人
          pass
        else:
            # 如果没有找到商人，那么就返回False
            # 点击道具
            find_and_click_template("public/shimen/task/capture/goods.png", 0.4)
            time.sleep(0.5)
            # 点击导标旗符
            find_and_click_template("public/shimen/task/capture/guid.png", 0.4)
            time.sleep(0.5)
            # 点击使用
            find_and_click_template("public/shimen/task/capture/use.png", 0.4)
            time.sleep(0.5)
            # 点击当铺
            find_and_click_template("public/shimen/task/capture/mapaim.png", 0.4)
            time.sleep(0.5)
            # 点击地图上的坐标位置
            find_and_click_template("public/shimen/task/capture/mapaim.png", 0.4)
            time.sleep(1)
            # 点击关闭按钮
            find_and_click_template("public/shimen/task/closemap.png", 0.4)
            time.sleep(3)
            # 点击商会总管
            find_and_click_template("public/shimen/task/capture/shop.png", 0.4)
        time.sleep(1)
        # 遍历所有匹配的店铺，直到找到并购买成功
        for shop_info in matching_shops:
            print(f"尝试店铺 {shop_info['shopId']}, 第 {shop_info['page']} 页")
            
            if self.try_buy_from_shop(shop_info, monster_name):
                print(f"成功购买 {monster_name}")
                # 点击关闭店铺窗口
                find_and_click_template("public/shimen/task/capture/closemap.png", 0.4)
                return True
        
        time.sleep(1)
        # # 点击翻页
        # find_and_click_template("public/shimen/task/capture/page.png", 0.4)
        # # 点击翻页对应的数字
        # # 匹配对应的召唤兽名字出现的位置
        # # 点击购买
        # find_and_click_template("public/shimen/task/capture/buy.png", 0.4)
        # time.sleep(0.5)
        # # 点击关闭
        # find_and_click_template("public/shimen/task/capture/closemap.png", 0.4)
        # 执行回师门

        # 实际导航逻辑...
    def try_buy_from_shop(self, shop_info, monster_name):
        """尝试从指定店铺购买召唤兽"""
        # 点击快速跳转
        find_and_click_template("public/shimen/task/capture/find.png", 0.6)
        time.sleep(1)
        
        # 点击输入框获得焦点
        find_and_click_template("public/shimen/task/capture/input.png", 0.4)
        
        time.sleep(0.5)
        
        # 输入店铺ID
        hwnd = find_window_by_title(window_title)
        success = click_sequence_numbers(hwnd, "public/shimen/task/number_keyboard.png", shop_info["shopId"])

        if not success:
            print(f"输入店铺ID {shop_info['shopId']} 失败")
            return False
        
        time.sleep(1)
        # 输入店铺数字并点击确定按钮
        find_and_click_template("public/shimen/task/capture/findShop.png", 0.4)
        time.sleep(1)
        # 点击翻页显示出翻页菜单
        find_and_click_template("public/shimen/task/capture/page.png", 0.4)
        time.sleep(1)
        # 如果需要翻页，进行翻页操作
        if shop_info["page"] != "1":
            if not self.turn_to_page(shop_info["page"]):
                print(f"翻到第 {shop_info['page']} 页失败")
                return False
        
        # 查找并点击购买按钮
        return self.find_and_buy_monster(monster_name)
    def find_and_buy_monster(self, monster_name):
        """在当前页查找并购买指定召唤兽"""
        print(f"开始查找 {monster_name}")
        return False
    # 从数组中匹配对应的动物名字在full_text中
    def recognize_monster_name(self,full_text):
        """
        从数组中匹配对应的怪物文字在full_text中
        返回字符串类型的怪物名称
        
        Args:
            animal_list: 动物名称数组，用于匹配识别
        
        Returns:
            str: 匹配到的动物名称
        """
        # 从utils.config导入animal_list
        from ..utils.config import animal_list
        
        # 在任务文本中查找匹配的动物名称
        for animal in animal_list:
            if animal in full_text:
                return animal
        
        # 如果没有找到匹配项，返回第一个动物作为默认值
        return animal_list[0] if animal_list else "未知怪物"
    def find_shops_for_monster(self, monster_name):
        """根据召唤兽名称查找所有相关的店铺和页数"""
        matching_shops = []
        
        for shop in animal_shop_list:
            for animal in shop["animalList"]:
                if animal["name"] == monster_name:
                    matching_shops.append({
                        "shopId": shop["shopId"],
                        "page": animal["page"],
                        "name": animal["name"]
                    })
                    break  # 同一个店铺中找到一个匹配就跳出
        
        return matching_shops
    def turn_to_page(self, target_page):
        """翻到指定页数"""
        hwnd = find_window_by_title(window_title)
        # 将目标页数转换为字符串，因为click_numbers_on_keyboard可以处理字符串，比如"10"
        target_page_str = str(target_page)
        # 调用正确的函数
        result = click_numbers_on_keyboardPage(hwnd, "public/shimen/task/changePage.png", target_page_str)
        return result['success']
    def capture_monster(self, monster_name):
        """寻找并下单购买对应的召唤兽"""
        # 确保目录存在
        import os
        save_dir = "public/debug"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        
        # 获取当前屏幕或窗口的图像
        hwnd = find_window_by_title(window_title)
        
        # 获取模板图片在句柄窗口中的位置
        result = find_template_in_window(hwnd, "public/shimen/task/capture/capture.png", threshold=0.4)
        if result['found']:
            print(f"找到模板位置: {result['position']}")
            print(f"模板中心点: {result['center']}")
            
            # 获取截图区域的绝对坐标
            region_x, region_y, region_width, region_height = result['position']
            
            # 截图指定区域
            image = pyautogui.screenshot(region=result['position'])
            
            # 保存区域截图到本地
            save_path = os.path.join(save_dir, "capture.png")
            image.save(save_path)
            
            # 创建OCR服务实例
            ocr_service = ShimenOCRService()
            found, locations_info = ocr_service.find_text_in_image(image, monster_name)
            
            if found and locations_info:
                clicked_count = 0
                max_clicks = 1  # 只点击第一个匹配项
                
                print(f"[capture_monster] 找到 {len(locations_info)} 个位置")
                print("[capture_monster] 所有位置:")
                
                for i, location in enumerate(locations_info):
                    # 我故意从第3个开始
                    print(f"位置 {i+2}: {location}")
                    if clicked_count >= max_clicks:
                        break
                        
                    if location and len(location) >= 4:
                        # 计算OCR返回的坐标在截图区域内的中心点
                        x_coords = [point[0] for point in location]
                        y_coords = [point[1] for point in location]
                        x_relative = sum(x_coords) // len(x_coords)
                        y_relative = sum(y_coords) // len(y_coords)
                        
                        # 将相对坐标转换为绝对屏幕坐标
                        screen_x = region_x + x_relative
                        screen_y = region_y + y_relative
                        
                        print(f"[capture_monster] 相对坐标: ({x_relative}, {y_relative})")
                        print(f"[capture_monster] 绝对坐标: ({screen_x}, {screen_y})")
                        
                        # 点击绝对坐标位置
                        self.click_at_position(screen_x, screen_y)
                        print(f"[capture_monster] 点击第 {i+1} 个位置: 屏幕坐标({screen_x}, {screen_y})")
                        clicked_count += 1
                        time.sleep(0.5)  # 点击间隔
                
                # 点击购买按钮
                find_template_in_window(hwnd, "public/shimen/task/capture/buy.png", threshold=0.4)
                time.sleep(1)
                return True
            else:
                print(f"[capture_monster] 未找到文字: {monster_name}")
                return False

        else:
            print("[capture_monster] 未找到模板区域")
            return False
    def click_at_position(self, x, y):
        """在指定位置点击"""
        print(f"[click_at_position] 准备点击坐标: ({x}, {y})")
        
        # 获取当前鼠标位置
        current_x, current_y = pyautogui.position()
        print(f"[click_at_position] 当前鼠标位置: ({current_x}, {current_y})")
        
        # 计算移动距离
        distance = ((x - current_x)**2 + (y - current_y)**2)**0.5
        move_duration = min(0.3, max(0.1, distance / 1000))
        
        print(f"[click_at_position] 移动距离: {distance:.2f} 像素, 移动时间: {move_duration:.2f} 秒")
        
        # 平滑移动并点击
        pyautogui.moveTo(x, y, duration=move_duration, tween=pyautogui.easeOutQuad)
        time.sleep(0.1)
        pyautogui.click()
        
        print(f"[click_at_position] 点击完成")
        time.sleep(1)
        # 点击购买
        find_and_click_template("public/shimen/task/capture/buy.png",0.6)
        time.sleep(1)
        # 关闭全部窗口
        find_and_click_template("public/shimen/task/capture/closemap.png", 0.6)
        time.sleep(1)
        find_and_click_template("public/shimen/task/capture/closemap.png", 0.6)
        time.sleep(1)
