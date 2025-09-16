from flask import Blueprint, jsonify, request
import threading
from main.service.shimen.shimen_service import ShimenService

shimen_bp = Blueprint('shimen', __name__, url_prefix='/shimen')
shimen_service = ShimenService()

@shimen_bp.route('/start', methods=['POST'])
def start_shimen():
    """
    启动师门任务
    """
    try:
        # 在新线程中启动师门任务，避免阻塞主线程
        if not shimen_service.running:
            thread = threading.Thread(target=shimen_service.start)
            thread.daemon = True
            thread.start()
            return jsonify({"status": "success", "message": "师门任务已启动"})
        else:
            return jsonify({"status": "warning", "message": "师门任务已在运行中"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@shimen_bp.route('/stop', methods=['POST'])
def stop_shimen():
    """
    停止师门任务
    """
    try:
        if shimen_service.running:
            shimen_service.stop()
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
        status = shimen_service.get_status()
        return jsonify({"status": "success", "data": status})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})