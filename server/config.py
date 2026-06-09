# 后端配置文件
# 生产环境部署前请设置以下环境变量（或创建 .env 文件）：
#   SECRET_KEY=随机字符串
#   DB_PASSWORD=强密码
#   JWT_SECRET=随机字符串
import os

# ---- 加载 .env 文件（如果存在）----
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(_env_path):
        load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv 未安装时跳过，直接用系统环境变量

class Config:
    # Flask 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gaokao-dev-secret-key')

    # MySQL 数据库连接
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '292180')
    DB_NAME = os.environ.get('DB_NAME', 'gaokao')
    DB_CHARSET = 'utf8mb4'

    # JWT 配置
    JWT_SECRET = os.environ.get('JWT_SECRET', 'gaokao-jwt-secret-dev')
    JWT_EXPIRES = 7 * 24 * 3600  # 7天过期

    # 收费自动开关：基于业务覆盖率评分自动判定
    # 优先级：环境变量 > coverage_service 自动检测 > 默认值(false)
    MIN_COMMERCIAL_SCORE = 85  # 商业化评分最低门槛(满分100)

    @classmethod
    def get_allow_payment(cls):
        """
        收费自动开关。
        基于 coverage_service 的业务覆盖率评分判定。
        环境变量 ALLOW_PAYMENT 可手动覆盖。
        """
        env_val = os.environ.get('ALLOW_PAYMENT', '').lower()
        if env_val == 'true':
            return True
        if env_val == 'false':
            return False
        # 自动检测：商业化评分 ≥ 85 才允许
        try:
            from services.coverage_service import should_allow_payment
            return should_allow_payment()
        except Exception:
            return False

    # 兼容旧代码
    @classmethod
    def check_production(cls):
        warnings = []
        if cls.SECRET_KEY == 'gaokao-dev-secret-key':
            warnings.append('SECRET_KEY 使用默认值，生产环境请设置环境变量')
        if cls.DB_PASSWORD == '292180':
            warnings.append('DB_PASSWORD 使用默认值，生产环境请设置环境变量')
        if cls.JWT_SECRET == 'gaokao-jwt-secret-dev':
            warnings.append('JWT_SECRET 使用默认值，生产环境请设置环境变量')
        return warnings

    # 启动时检查是否使用默认密钥（仅开发环境警告）
    @classmethod
    def check_production(cls):
        warnings = []
        if cls.SECRET_KEY == 'gaokao-dev-secret-key':
            warnings.append('SECRET_KEY 使用默认值，生产环境请设置环境变量')
        if cls.DB_PASSWORD == '292180':
            warnings.append('DB_PASSWORD 使用默认值，生产环境请设置环境变量')
        if cls.JWT_SECRET == 'gaokao-jwt-secret-dev':
            warnings.append('JWT_SECRET 使用默认值，生产环境请设置环境变量')
        return warnings
