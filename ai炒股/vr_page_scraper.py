from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
from urllib.parse import urljoin, urlparse
import re

# 正确配置 Chromedriver 路径
driver_path = r'F:\AIstudy2025\ai炒股\chromedriver-win64\chromedriver.exe'
service = Service(executable_path=driver_path)

# 浏览器选项
options = webdriver.ChromeOptions()
options.binary_location = r"F:\AIstudy2025\ai炒股\chrome-win64\chrome.exe"
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features=AutomationControlled")
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")

driver = webdriver.Chrome(service=service, options=options)

# 目标网址
url = "https://vr.xgj.vasen.com/webapp/hotspot/index.html#/preview?wOH8lZfNZdlTK6aiEN8cEzj2a"

# 创建保存目录
save_dir = "vr_page_content"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 创建资源目录
css_dir = os.path.join(save_dir, "css")
js_dir = os.path.join(save_dir, "js")
img_dir = os.path.join(save_dir, "images")
if not os.path.exists(css_dir):
    os.makedirs(css_dir)
if not os.path.exists(js_dir):
    os.makedirs(js_dir)
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

def download_resource(url, folder, filename=None):
    """
    下载资源文件
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        if filename is None:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = str(hash(url)) + ".tmp"
        
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filepath
    except Exception as e:
        print(f"下载资源失败 {url}: {e}")
        return None

def fix_resource_paths(html_content, base_url):
    """
    修改资源路径为相对路径
    """
    # 处理CSS链接
    def replace_css(match):
        full_url = match.group(1)
        if full_url.startswith('data:'):
            return match.group(0)  # 保持data URI不变
            
        filename = os.path.basename(urlparse(full_url).path)
        if not filename:
            filename = str(hash(full_url)) + ".css"
            
        # 下载CSS文件
        downloaded = download_resource(full_url, css_dir, filename)
        if downloaded:
            return f'<link rel="stylesheet" href="css/{filename}">'
        return match.group(0)
    
    # 处理JS链接
    def replace_js(match):
        full_url = match.group(1)
        if full_url.startswith('data:'):
            return match.group(0)  # 保持data URI不变
            
        filename = os.path.basename(urlparse(full_url).path)
        if not filename:
            filename = str(hash(full_url)) + ".js"
            
        # 下载JS文件
        downloaded = download_resource(full_url, js_dir, filename)
        if downloaded:
            return f'<script src="js/{filename}">'
        return match.group(0)
    
    # 处理图片链接
    def replace_img(match):
        full_url = match.group(1)
        if full_url.startswith('data:'):
            return match.group(0)  # 保持data URI不变
            
        filename = os.path.basename(urlparse(full_url).path)
        if not filename:
            filename = str(hash(full_url)) + ".png"
            
        # 下载图片文件
        downloaded = download_resource(full_url, img_dir, filename)
        if downloaded:
            return f'src="images/{filename}"'
        return match.group(0)
    
    # 替换CSS链接
    html_content = re.sub(r'<link[^>]*href=["\']([^"\']*)["\'][^>]*stylesheet[^>]*>', replace_css, html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<link[^>]*stylesheet[^>]*href=["\']([^"\']*)["\'][^>]*>', replace_css, html_content, flags=re.IGNORECASE)
    
    # 替换JS链接
    html_content = re.sub(r'<script[^>]*src=["\']([^"\']*)["\'][^>]*>', replace_js, html_content, flags=re.IGNORECASE)
    
    # 替换图片链接
    html_content = re.sub(r'src=["\']([^"\']*)["\']', replace_img, html_content, flags=re.IGNORECASE)
    
    return html_content

try:
    # 访问网页
    driver.get(url)
    
    # 等待页面加载完成
    time.sleep(10)
    
    # 滚动页面以触发所有内容加载
    total_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(0, total_height, 100):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(0.1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(5)
    
    # 等待关键元素出现
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    # 获取页面标题和完整HTML
    page_title = driver.title
    page_html = driver.page_source
    
    # 修复资源路径
    page_html = fix_resource_paths(page_html, url)
    
    # 保存完整HTML
    html_file_path = os.path.join(save_dir, "index.html")
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(page_html)
    
    print(f"页面保存成功，标题: {page_title}")
    print(f"HTML文件保存至: {html_file_path}")
    
    # 尝试保存页面截图
    screenshot_path = os.path.join(save_dir, "screenshot.png")
    driver.save_screenshot(screenshot_path)
    print(f"页面截图保存至: {screenshot_path}")
    
    print("所有资源已保存，可以在本地浏览器中打开index.html进行预览")

except Exception as e:
    print(f"抓取过程中出现错误: {e}")

finally:
    # 关闭浏览器
    time.sleep(2)
    driver.quit()