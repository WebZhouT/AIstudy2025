from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url = "https://www.iwencai.com/unifiedwap/result?w=..."

# 1. 正确配置 Chromedriver 路径
service = Service(executable_path="F:\AIstudy2025\ai炒股\chromedriver.exe")  # 修改为实际路径

# 2. 反爬和浏览器选项
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features=AutomationControlled")
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")

driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(url)
    
    # 3. 显式等待关键元素
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table"))  # 替换为实际元素
    )
    
    # 可选：处理弹窗（如有）
    try:
        close_btn = driver.find_element(By.CSS_SELECTOR, ".popup-close")
        close_btn.click()
    except Exception:
        pass
    
    time.sleep(2)
    
    # 保存页面
    with open("webpage.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("成功保存页面")
    
finally:
    driver.quit()