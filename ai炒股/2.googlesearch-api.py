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
engine = "google_light"
API_KEY = "373c486154696f277d65af08d933deac5c4b00b6a6e1f229834d537707e57237"  # 替换为你的API密钥




def google_search(query):
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
        params = {
            "engine": engine,
            "q":query,
            # "gl": "countryCN",#此参数定义了 Google 搜索所使用的国家/地区
            "cr": "countryCN",#该参数用于定义一个或多个国家/地区，以限制搜索范围
            "hl": "zh-cn",
            "num": "100",#返回的最大结果值
            "window": "5D",
            "device": "mobile",
            "api_key": "373c486154696f277d65af08d933deac5c4b00b6a6e1f229834d537707e57237"
        }
        
        # 发送API请求
        search = GoogleSearch(params)
        response = search.get_dict()
        print(response)
        # 将返回数据全部写到txt文本中
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(response, ensure_ascii=False, indent=2))
            f.write("\n")

                
        print(f"结果已保存到: {os.path.abspath(filename)}")
        return True

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

def process_results(file, data):
    """将原始结果数据直接写入文件"""
    try:
        # 写入完整JSON结构
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")  # 添加换行分隔
        
        # 可选：附加元数据（时间戳、来源等）
        file.write(f"\n<!-- Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')} -->")
        
    except Exception as e:
        print(f"写入原始数据失败: {str(e)}")
        raise

if __name__ == "__main__":
    # 使用示例
    # search_query = "2025年5月6日 中国财经政治行业热点新闻"
    search_query = "中国2025年5月4日财经热点"
    google_search(search_query)  # 获取前2页结果