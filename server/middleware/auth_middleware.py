# JWT 认证中间件 —— 验证请求是否携带有效 token
import jwt
from flask import request, jsonify
from config import Config

def login_required(f):
    """
    装饰器：放在路由函数上，自动验证 JWT
    用法：@login_required
          def my_route():
              user_id = request.user_id  # 中间件注入的

    验证逻辑：
    1. 从请求头取 Authorization: Bearer <token>
    2. 用密钥解密 token
    3. 把 userId 注入 request，后续函数直接用
    """
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '请先登录'}), 401

        token = auth_header[7:]  # 跳过 "Bearer " 7个字符

        try:
            # 解密 token，拿到 payload（里面存了 userId 和 phone）
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            request.user_id = payload['userId']
            request.user_phone = payload['phone']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': '登录已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': '无效的登录凭证'}), 401

        return f(*args, **kwargs)

    return decorated
