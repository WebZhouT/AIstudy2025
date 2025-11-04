from flask import Blueprint, jsonify, request
import threading
import json
import os
from main.service.shimen.shimen_service import ShimenService

shimen_bp = Blueprint('shimen', __name__, url_prefix='/shimen')

shimen_service = None

def load_sect_config(sect):
    """根据门派名称加载配置"""
    try:
        # 读取taskBtnlist.json文件
        config_path = "public/shimen/task/taskBtnlist.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        
        # 查找对应门派的配置
        for config in configs:
            if config.get('sect') == sect:
                return config
        
        return None
    except Exception as e:
        print(f"加载配置失败: {e}")
        return None

@shimen_bp.route('/start', methods=['POST'])
def start_shimen():
    """
    启动师门任务
    """
    global shimen_service
    
    try:
        # 获取请求数据
        data = request.get_json()
        sect = data.get('sect')
        level = data.get('level', 69)
        
        if not sect:
            return jsonify({"status": "error", "message": "缺少门派参数"})
        
        # 获取门派配置
        sect_config = load_sect_config(sect)
        if not sect_config:
            return jsonify({"status": "error", "message": f"未找到门派 {sect} 的配置"})
        
        # 创建ShimenService实例
        shimen_service = ShimenService(sect_config=sect_config)
        
        # 在新线程中启动师门任务，避免阻塞主线程
        if not shimen_service.running:
            thread = threading.Thread(target=shimen_service.start)
            thread.daemon = True
            thread.start()
            return jsonify({"status": "success", "message": f"师门任务已启动 - {sect}"})
        else:
            return jsonify({"status": "warning", "message": "师门任务已在运行中"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@shimen_bp.route('/stop', methods=['POST'])
def stop_shimen():
    """
    停止师门任务
    """
    global shimen_service
    
    try:
        if shimen_service and shimen_service.running:
            shimen_service.stop()
            shimen_service = None  # 重置为None
            return jsonify({"status": "success", "message": "师门任务已停止"})
        else:
            return jsonify({"status": "warning", "message": "师门任务未在运行"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@shimen_bp.route('/status', methods=['GET'])
def get_status():
    """
    获取师门任务运行状态
    """
    try:
        if shimen_service:
            status = shimen_service.get_status()
            return jsonify({"status": "success", "data": status})
        else:
            return jsonify({"status": "success", "data": {"running": False, "message": "任务未启动"}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})