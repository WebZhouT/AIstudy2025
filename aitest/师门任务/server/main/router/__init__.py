# 路由
from flask import Blueprint, render_template
# 自动签到路由
from .autologin_router import autologin_bp
# 师门路由
from .shimen_router import shimen_bp

Routers = Blueprint('routes', __name__)
# # 注册自动签到蓝图
# Routers.register_blueprint(autologin_bp, url_prefix='/autologin')
# 注册师门蓝图
Routers.register_blueprint(shimen_bp, url_prefix='/shimen')

# # 自动签到
# @Routers.route('/autologin')
# def autologin_index():
#     return render_template('autologin.html')

# 师门
@Routers.route('/shimen')
def shimen_index():
    return render_template('shimen.html')