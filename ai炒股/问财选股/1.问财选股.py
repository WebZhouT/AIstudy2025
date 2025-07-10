from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
txt = '筛选出流通市值在10亿到80亿之间的所有个股；剔除所有利空消息个股；列出所属概念；列出行业；剔除科创板和北交所；剔除新股和次新股&querytype=stock'
# 生成防缓存标识addSign=1750473318854
addSign = str(int(time.time() * 1000))
strtxt = txt + '&addSign=' + addSign 
url = "https://www.iwencai.com/unifiedwap/result?w="+strtxt

# 1. 正确配置 Chromedriver 路径
driver_path = r'F:\AIstudy2025\ai炒股\chromedriver-win64\chromedriver.exe'
service = Service(executable_path=driver_path)

# 2. 反爬和浏览器选项
options = webdriver.ChromeOptions()
options.binary_location = r"F:\AIstudy2025\ai炒股\chrome-win64\chrome.exe"  # 例如: r"C:\Program Files\Google\Chrome\Application\chrome.exe"
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features=AutomationControlled")
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")

driver = webdriver.Chrome(service=service, options=options)
""" ============================================================================ """
# 采集所有数据
all_data = []
# 切换每页条数(点击显示100页)
def showTag():
    # 首先点击打开下拉菜单
    dropdown = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".pcwencai-pagination-wrap .drop-down-box")))
    dropdown.click()
    
    # 然后点击下拉菜单中的选项
    option = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".pcwencai-pagination-wrap .drop-down-box ul li:nth-child(3)")))
    option.click()
# 切换页码点击下一页
def switch_page():
    try:
        # 正确的下一页按钮定位
        next_btn = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".pcwencai-pagination li:last-child a"))
        )
        next_btn.click()
        time.sleep(2)  # 等待新页面加载
      
        save_data()  # 保存新页面的数据
        return True
    except Exception as e:
        print(f"翻页失败或已是最后一页: {e}")
        return False



# 保存页面显示的数据到全局，最后存本地
def save_data():
    # 获取表头信息
    header_columns = []
    header_ul = driver.find_element(By.CLASS_NAME, "iwc-table-header-ul")
    header_items = header_ul.find_elements(By.CLASS_NAME, "jsc-list-item")
  # 获取所有匹配的更多按钮
    more_btns = WebDriverWait(driver, 4).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody .hideMore .i-beyond-width"))
    )
    # 遍历点击所有更多按钮
    for btn in more_btns:
        try:
            # 滚动到元素
            # driver.execute_script("arguments[0].scrollIntoView();", btn)
            # 尝试普通点击
            btn.click()
            # time.sleep(1)  # 每次点击后等待1秒
        except:
            # 如果普通点击失败，尝试JavaScript点击
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
    """ ================================ """
    for item in header_items:
        # 提取表头文本
        spans = item.find_elements(By.CSS_SELECTOR, ".thead-span")
        if spans:
            # 合并多行表头文本
            header_text = " ".join([span.text.strip() for span in spans if span.text.strip()])
            header_columns.append(header_text)
    

    # 获取表格主体
    table_body = driver.find_element(By.CLASS_NAME, "iwc-table-body")
    table_rows = table_body.find_elements(By.CSS_SELECTOR, "tr")
    
    # 遍历每一行
    for row in table_rows:
        row_data = {}
        cells = row.find_elements(By.TAG_NAME, "td")
        
        # 跳过空行
        if not cells:
            continue
            
        # 提取固定列数据
        row_data["序号"] = cells[0].text.strip()
        row_data["股票代码"] = cells[2].text.strip()
        row_data["股票简称"] = cells[3].text.strip()
        row_data["现价（元）"] = cells[4].text.strip()
        row_data["涨跌幅(%)"] = cells[5].text.strip()
        row_data["流通市值"] = cells[6].text.strip()
        # 提取所属概念 (第7个td)
        if len(cells) > 7:
            concept_td = cells[7]
            concept_links = concept_td.find_elements(By.CSS_SELECTOR, "p a.splitLink")
            if concept_links:
                concepts = [link.text.strip() for link in concept_links]
                row_data["所属概念"] = ";".join(concepts)
            else:
                row_data["所属概念"] = concept_td.text.strip()
        
        # 提取行业信息 (第8个td)
        if len(cells) > 8:
            industry_td = cells[8]
            industry_links = industry_td.find_elements(By.CSS_SELECTOR, "a.splitLink")
            if industry_links:
                industries = [link.text.strip() for link in industry_links]
                row_data["所属行业"] = "-".join(industries)
            else:
                row_data["所属行业"] = industry_td.text.strip()
        
        # 提取上市板块 (第9个td)
        if len(cells) > 9:
            row_data["上市板块"] = cells[9].text.strip()
            
        # 提取股票市场类型 (第10个td)
        if len(cells) > 10:
            market_td = cells[10]
            market_links = market_td.find_elements(By.CSS_SELECTOR, "a.splitLink")
            if market_links:
                markets = [link.text.strip() for link in market_links]
                row_data["股票市场类型"] = ";".join(markets)
            else:
                row_data["股票市场类型"] = market_td.text.strip()
                
        # 提取总市值 (第11个td)
        if len(cells) > 11:
            row_data["总市值"] = cells[11].text.strip()
            
        # 提取概念数量 (第12个td)
        if len(cells) > 12:
            row_data["所属概念数量"] = cells[12].text.strip()
            
        # 提取成交量 (第13个td)
        if len(cells) > 13:
            row_data["成交量"] = cells[13].text.strip()
            
        # 提取成交额 (第14个td)
        if len(cells) > 14:
            row_data["成交额"] = cells[14].text.strip()
            
        # 提取市盈率 (第15个td)
        if len(cells) > 15:
            row_data["市盈率"] = cells[15].text.strip()
            
        # 提取地址信息 (第16个td)
        if len(cells) > 16:
            row_data["公司地址"] = cells[16].text.strip()
            
        # 提取经营范围 (第17个td)
        if len(cells) > 17:
            row_data["经营范围"] = cells[17].text.strip()
        
        # 添加到数据列表
        all_data.append(row_data)
try:
    driver.get(url)
    
    # 3. 显式等待关键元素
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "iwc-table-body"))  # 替换为实际元素page-item
    )
    showTag()
    # switch_page(driver)
    # 获取所有分页项
    time.sleep(4)
    # 获取所有分页项
    pagination_items = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".pcwencai-pagination li.page-item"))
    )
    
    if pagination_items:
        last_item = pagination_items[-1]  # 直接取最后一个元素
        print("最后一页文本:", last_item.text)
        save_data()
        # 循环最后一页的文本-1次
        for i in range(int(last_item.text)-1):
            print(f"正在处理第 {i+2} 页...")
            switch_page()
    else:
        print("未找到分页元素")

    
    # 输出JSON格式数据
    json_output = json.dumps(all_data, ensure_ascii=False, indent=2)
    # print(json_output)
    
    # 保存到文件
    with open("股票池.json", "w", encoding="utf-8") as f:
        f.write(json_output)
    print("成功保存JSON数据")

finally:
    # 关闭浏览器
    time.sleep(2)
    driver.quit()



# def changePage(pageNum):
    