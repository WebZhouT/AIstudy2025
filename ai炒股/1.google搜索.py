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

# 采集所有数据
all_data = []
def generate_page_urls(base_url, pages):
    """生成分页URL列表"""
    parsed = urlparse(base_url)
    query = parse_qs(parsed.query)
    
    # 保留核心参数，移除分页相关参数
    preserved_params = ['q', 'lr', 'cr', 'tbs', 'sca_esv']
    clean_query = {k: v for k, v in query.items() if k in preserved_params}
    
    urls = []
    for page in range(pages):
        # 每页10条结果，start参数递增
        new_query = clean_query.copy()
        new_query['start'] = [str(page * 10)]
        
        # 重建URL
        new_query_str = urlencode(new_query, doseq=True)
        urls.append(urlunparse(parsed._replace(query=new_query_str)))
    
    return urls
def save_webpage_content(url, page_num):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # 设置中文User-Agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        
        driver_path = r'F:\AIstudy2025\ai炒股\chromedriver-win64\chromedriver.exe'
        service = Service(executable_path=driver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(5)
        
        # 访问页面
        driver.get(url)
        time.sleep(2)  # 基础等待时间
        
        # 生成唯一文件名
        parsed_url = urlparse(url)
        domain = parsed_url.hostname or "unknown"
        domain_clean = re.sub(r'[\\/*?:"<>|]', '_', domain)
        
        # 包含页码和搜索词
        query_params = parse_qs(parsed_url.query)
        search_query = query_params.get('q', [''])[0]
        # 获取当前的年月日
        current_date = time.strftime("%Y%m%d", time.localtime())
        filename = f"{current_date}_p{page_num+1}.html"
        full_path = os.path.join("炒股搜索结果", filename)
        # 创建数据存储结构
        results_data={
            "page": page_num + 1,
            "results": [],
            "source_url": url
        }

        # 获取所有搜索结果容器
        results = driver.find_elements(By.CLASS_NAME, "MjjYud")
        # 遍历输出结果的文本内容
        for idx, result in enumerate(results):
            print(f"\n=== 结果 {idx+1} ===")
            # 安全提取元素
            title = result.find_elements(By.CSS_SELECTOR, "h3")[0].text if result.find_elements(By.CSS_SELECTOR, "h3") else ""
            link = result.find_elements(By.TAG_NAME, "a")[0].get_attribute("href") if result.find_elements(By.TAG_NAME, "a") else ""
            snippet = result.find_elements(By.CLASS_NAME, "VwiC3b")[0].text if result.find_elements(By.CLASS_NAME, "VwiC3b") else ""

            
            print(f"标题: {title}")
            print(f"链接: {link}")
            print(f"摘要: {snippet}...")  # 只显示前50字符
            item = {
                "title": title,
                "link": link,
                "snippet": snippet
            }
            # 如果item.title!=none，则跳过保存
            if item.get("title") == None:
                continue
            if item.get("link") == None:
                continue
            if item.get("snippet") == None:
                continue  

            results_data['results'].append(item)
        # 将循环输出的内容保存到json文件中#
        # 生成JSON文件名
        # filename2 = f"中国政治财经新闻_p{page_num+1}.json"
        # full_path2 = os.path.join("html_files", filename2)
        # # 保存JSON数据
        # with open(full_path2, 'w', encoding='utf-8') as f:
        #     json.dump(results_data, f, ensure_ascii=False, indent=2)

        # print(f"成功保存JSON文件：{filename2}")
        """ ==================================== """
        # 保存内容
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        all_data.append(results_data)
        print(f"成功保存第 {page_num+1} 页：{full_path}")

        return True

    except Exception as e:
        print(f"第 {page_num+1} 页抓取失败：{str(e)}")
        return False
    finally:
        if 'driver' in locals():
        
            driver.quit()

if __name__ == "__main__":
    # 原始URL（第一页）
    base_url = "https://www.google.com/search?q=中国政治财经新闻&lr=lang_zh-CN&cr=countryCN&tbs=lr:lang_1zh-CN,ctr:countryCN,qdr:d"
    
    # 生成10页URL
    page_urls = generate_page_urls(base_url, pages=10)
    
    # 创建存储目录
    os.makedirs("html_files", exist_ok=True)
    
    # 遍历抓取
    for idx, url in enumerate(page_urls):
        save_webpage_content(url, idx)
        time.sleep(5)  # 增加间隔防止被封
    # 全部遍历完成后，存储json文件
    # 获取当前的年月日
    current_date = time.strftime("%Y%m%d", time.localtime())
    filename3 = f"{current_date}.json"
    full_path3 = os.path.join("html_files", filename3)
    with open(full_path3, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"成功保存JSON文件：{filename3}")
