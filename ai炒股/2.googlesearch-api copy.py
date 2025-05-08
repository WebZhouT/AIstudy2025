# api网址：https://serpapi.com/search-api
from serpapi import GoogleSearch
import requests
import json
import time
import os
SAVE_DIR = "search_results"  # 保存目录
# params = {
#   # "engine": "google_light",
#   "engine": "google_finance",
#   "q": "财经新闻热度排行",
#   "gl": "countryCN",#此参数定义了 Google 搜索所使用的国家/地区
#   "cr": "countryCN",#该参数用于定义一个或多个国家/地区，以限制搜索范围
#   "hl": "zh-cn",
#   "num": "100",#返回的最大结果值
#   "window": "5D",
#   "device": "mobile",
#   "api_key": "373c486154696f277d65af08d933deac5c4b00b6a6e1f229834d537707e57237"
# }
# 搜索的类型google_light和google_finance财经
SEARCH_ENGINE = "google"
query = "财经新闻热度排行"
API_KEY = "373c486154696f277d65af08d933deac5c4b00b6a6e1f229834d537707e57237"  # 替换为你的API密钥




def google_search(query, pages=1):
    """执行Google搜索并保存结果"""
    try:
        # 创建保存目录
        os.makedirs(SAVE_DIR, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = int(time.time())
        filename = os.path.join(SAVE_DIR, f"{query}_{timestamp}.txt")
        
        # 打开文件准备写入
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"搜索关键词: {query}\n")
            f.write(f"搜索时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 分页获取结果
            for page in range(pages):
                params = {
                    "engine": "google_finance",
                    "q":query,
                    "gl": "countryCN",#此参数定义了 Google 搜索所使用的国家/地区
                    "cr": "countryCN",#该参数用于定义一个或多个国家/地区，以限制搜索范围
                    "hl": "zh-cn",# 语言
                    "num": "100",#返回的最大结果值
                    "window": "5D",
                    "device": "mobile",
                    "api_key": API_KEY,
                }
                
                # 发送API请求
                response = requests.get(
                    "https://serpapi.com/search",
                    params=params,
                    timeout=30
                )
                
                # 处理响应
                if response.status_code == 200:
                    data = response.json()
                    process_results(f, data, page+1)
                else:
                    print(f"请求失败 (页面 {page+1}): HTTP {response.status_code}")
                
                # API频率限制保护
                time.sleep(1)
                
        print(f"结果已保存到: {os.path.abspath(filename)}")
        return True

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

def process_results(file, data, page_num):
    """处理并写入搜索结果"""
    # 写入页眉
    file.write(f"========== 第 {page_num} 页 ==========\n")
    
    # 解析搜索结果
    if "organic_results" in data:
        for idx, result in enumerate(data["organic_results"], 1):
            title = result.get("title", "无标题")
            link = result.get("link", "#")
            snippet = result.get("snippet", "无摘要")
            
            # 写入格式化结果
            file.write(f"{idx}. {title}\n")
            file.write(f"链接: {link}\n")
            file.write(f"摘要: {snippet}\n\n")
    
    # 解析知识图谱（如果有）
    if "knowledge_graph" in data:
        kg = data["knowledge_graph"]
        file.write("\n[知识图谱信息]\n")
        file.write(f"标题: {kg.get('title', '')}\n")
        file.write(f"类型: {kg.get('type', '')}\n")
        file.write(f"描述: {kg.get('description', '')}\n\n")
    
    # 解析相关搜索（如果有）
    if "related_searches" in data:
        file.write("[相关搜索建议]\n")
        for search in data["related_searches"]:
            file.write(f"- {search.get('query', '')}\n")
        file.write("\n")

if __name__ == "__main__":
    # 使用示例
    search_query = "人工智能发展趋势"
    google_search(search_query, pages=2)  # 获取前2页结果