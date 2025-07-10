# 获取数据存储到json中
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import os
import re
import time
import json
import urllib.parse
import pyautogui
# 采集所有数据
all_data = []


def save_webpage_content(url, numbers,title,price,payTime):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # 设置中文User-Agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        
        # driver_path = r'F:\AIstudy2025\ai炒股\chromedriver-win64\chromedriver.exe'
        driver_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        service = Service(executable_path=driver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(5000)
        
        # 访问页面
        driver.get(url+numbers)
        time.sleep(2)  # 基础等待时间
        # 获取当前的年月日
        current_date = time.strftime("%Y%m%d", time.localtime())
        filename = f"{current_date}_p{numbers}.html"
        full_path = os.path.join("订单搜索结果", filename)
        # 创建数据存储结构
        results_data={
            "page": numbers,
            "results": [],
            "source_url": url
        }

        # 获取所有搜索结果容器
        results = driver.find_elements(By.CLASS_NAME, "MjjYud")
        # 打开浏览器后，手动定位按钮的屏幕坐标
        x, y = 100, 200  # 替换为实际坐标
        pyautogui.click(x, y)
        # # 遍历输出结果的文本内容
        # for idx, result in enumerate(results):
        #     print(f"\n=== 结果 {idx+1} ===")
        #     # 安全提取元素
        #     title = result.find_elements(By.CSS_SELECTOR, "h3")[0].text if result.find_elements(By.CSS_SELECTOR, "h3") else ""
        #     link = result.find_elements(By.TAG_NAME, "a")[0].get_attribute("href") if result.find_elements(By.TAG_NAME, "a") else ""
        #     snippet = result.find_elements(By.CLASS_NAME, "VwiC3b")[0].text if result.find_elements(By.CLASS_NAME, "VwiC3b") else ""

            
        #     print(f"标题: {title}")
        #     print(f"链接: {link}")
        #     print(f"摘要: {snippet}...")  # 只显示前50字符
        #     item = {
        #         "title": title,
        #         "link": link,
        #         "snippet": snippet
        #     }
        #     # 如果item.title!=none，则跳过保存
        #     if item.get("title") == None:
        #         continue
        #     if item.get("link") == None:
        #         continue
        #     if item.get("snippet") == None:
        #         continue  

        #     results_data['results'].append(item)
        """ ==================================== """
        # 保存内容
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        all_data.append(results_data)
        print(f"成功保存第 {numbers} 页：{full_path}")

        return True

    except Exception as e:
        print(f"第 {numbers} 页抓取失败：{str(e)}")
        return False
    finally:
        if 'driver' in locals():
        
            driver.quit()

if __name__ == "__main__":
    # 原始URL（第一页）
    # 后面拼接订单id是要查询的订单id
    base_url = "https://qn.taobao.com/home.htm/trade-platform/tp/detail?spm=a21dvs.23742411.0.0.60fb7d4dlgdW3y&bizOrderId="
    # 读取json文件，并循环打印
    with open("orders.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            number = item["number"]  # 去掉逗号
            title = item["title"]    # 去掉逗号
            price = item["price"]    # 去掉逗号
            payTime = item["payTime"]# 去掉逗号
            save_webpage_content(base_url, number,title,price,payTime)
            break;
    # 循环遍历json文件打印出每一个里面的json内容
  