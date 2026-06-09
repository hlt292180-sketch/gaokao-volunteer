# 高考志愿填报系统 —— Flask 后端入口
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ========== 健康检查 ==========
@app.route('/')
def index():
    return {'status': 'ok', 'message': '志愿导航后端运行中'}

# ========== 公开路由 ==========
from routes.province import province_bp
app.register_blueprint(province_bp, url_prefix='/api/provinces')

from routes.score import score_bp
from routes.university import uni_bp
from routes.major import major_bp
from routes.auth import auth_bp
from routes.assessment import assess_bp
from routes.volunteer import vol_bp

app.register_blueprint(score_bp, url_prefix='/api/score-segments')
app.register_blueprint(uni_bp, url_prefix='/api/universities')
app.register_blueprint(major_bp, url_prefix='/api/majors')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(assess_bp, url_prefix='/api/assessments')
app.register_blueprint(vol_bp, url_prefix='/api/volunteer')

# ========== 需登录路由 ==========
from routes.payment import pay_bp
app.register_blueprint(pay_bp, url_prefix='/api/payment')

# ========== 埋点路由（公开，无需登录）==========
from routes.analytics import analytics_bp
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

# ========== 收藏路由（需登录）==========
from routes.favorite import fav_bp
app.register_blueprint(fav_bp, url_prefix='/api/favorites')

# ========== 启动 ==========
if __name__ == '__main__':
    print('🎓 志愿导航后端启动中...')
    app.run(port=3000, debug=True)
