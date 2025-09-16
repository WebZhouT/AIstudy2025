from flask import Blueprint, jsonify, request
import threading
from main.service.autologin.autologin_service import AutoLoginService

# 修复：添加唯一的端点名称前缀以避免冲突
autologin_bp = Blueprint('autologin', __name__, url_prefix='/autologin')
auto_login_service = AutoLoginService()

@autologin_bp.route('/start', methods=['POST'])
def start_autologin():
    """
    启动自动签到
    """
    try:
        # 在新线程中启动自动签到，避免阻塞主线程
        if not auto_login_service.running:  # 修复：使用正确的属性访问方式
            thread = threading.Thread(target=auto_login_service.start)
            thread.daemon = True
            thread.start()
            return jsonify({"status": "success", "message": "自动签到已启动"})
        else:
            return jsonify({"status": "warning", "message": "自动签到已在运行中"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@autologin_bp.route('/stop', methods=['POST'])
def stop_autologin():
    """
    停止自动签到
    """
    try:
        if auto_login_service.running:  # 修复：使用正确的属性访问方式
            auto_login_service.stop()
            return jsonify({"status": "success", "message": "自动签到已停止"})
        else:
            return jsonify({"status": "warning", "message": "自动签到未在运行"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@autologin_bp.route('/status', methods=['GET'])
def get_status():
    """
    获取自动签到运行状态
    """
    try:
        status = auto_login_service.get_status()
        return jsonify({"status": "success", "data": status})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@autologin_bp.route('/results', methods=['GET'])
def get_results():
    """
    获取签到结果
    """
    try:
        results = auto_login_service.get_results()
        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})