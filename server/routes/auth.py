# 认证路由 —— 注册 / 登录 / 查个人信息
# 安全要点：
#   ✅ bcrypt 加密密码（不存明文）
#   ✅ JWT 无状态鉴权
#   ✅ API 绝不返回 password_hash

import bcrypt
import jwt
from flask import Blueprint, jsonify, request
from config import Config
from database.db import get_conn
from middleware.auth_middleware import login_required

auth_bp = Blueprint('auth', __name__)

# ===== 注册 =====
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    Body: { "phone": "138xxx", "password": "123456", "nickname": "小明" }

    流程：
    1. 校验手机号格式 + 密码长度
    2. 检查手机号是否已被注册
    3. bcrypt 加密密码（🔒 安全：不存明文）
    4. 插入用户
    5. 返回 JWT
    """

    data = request.get_json()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()

    # ---- 校验 ----
    if not phone or not password:
        return jsonify({'success': False, 'message': '手机号和密码不能为空'}), 400
    if not phone.isdigit() or len(phone) != 11:
        return jsonify({'success': False, 'message': '请输入正确的手机号'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6位'}), 400

    conn = get_conn()
    cur = conn.cursor()

    # 检查重复
    cur.execute("SELECT id FROM users WHERE phone=%s", (phone,))
    if cur.fetchone():
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '该手机号已注册'}), 400

    # 🔒 bcrypt 加密 —— 同样的密码两次加密结果不同，破解难度极高
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 插入
    cur.execute(
        "INSERT INTO users (phone, password_hash, nickname) VALUES (%s, %s, %s)",
        (phone, password_hash, nickname or ('用户' + phone[-4:]))
    )
    user_id = cur.lastrowid
    conn.commit()

    # 生成 JWT
    token = jwt.encode(
        {'userId': user_id, 'phone': phone},
        Config.JWT_SECRET,
        algorithm='HS256'
    )

    cur.close(); conn.close()

    return jsonify({
        'success': True,
        'message': '注册成功',
        'data': {'token': token, 'userId': user_id}
    }), 201


# ===== 登录 =====
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Body: { "phone": "138xxx", "password": "123456" }

    流程：
    1. 查手机号是否存在
    2. bcrypt 比对密码（不是直接比较字符串！）
    3. 生成 JWT 返回
    """

    data = request.get_json()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')

    if not phone or not password:
        return jsonify({'success': False, 'message': '手机号和密码不能为空'}), 400

    conn = get_conn()
    cur = conn.cursor()

    # 查用户
    cur.execute(
        "SELECT id, phone, nickname, password_hash, is_paid, is_admin, paid_expire_at"
        " FROM users WHERE phone=%s",
        (phone,)
    )
    user = cur.fetchone()

    if not user:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '手机号未注册'}), 400

    # 🔒 bcrypt 验密 —— 不是字符串比较，是专门的验密函数
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '密码错误'}), 400

    # 生成 JWT
    token = jwt.encode(
        {'userId': user['id'], 'phone': user['phone']},
        Config.JWT_SECRET,
        algorithm='HS256'
    )

    cur.close(); conn.close()

    # ⚠️ 不返回 password_hash
    return jsonify({
        'success': True,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': {
                'id': user['id'],
                'phone': user['phone'],
                'nickname': user['nickname'],
                'isPaid': user['is_paid'] == 1 or user['is_admin'] == 1,  # 管理员自动视为付费
                'isAdmin': user['is_admin'] == 1,
                'paidExpireAt': user['paid_expire_at'],
            }
        }
    })


# ===== 获取当前用户信息 =====
@auth_bp.route('/me', methods=['GET'])
@login_required  # 🔒 需要登录才能调用
def get_me():
    """
    GET /api/auth/me
    返回当前登录用户的完整信息（含免费额度计数）
    """

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, phone, nickname, is_paid, is_admin, paid_expire_at,"
        " free_check_count, free_assessment_count, created_at"
        " FROM users WHERE id=%s",
        (request.user_id,)  # ← 中间件注入的
    )
    user = cur.fetchone()

    cur.close(); conn.close()

    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    # ⚠️ 不返回 password_hash
    return jsonify({
        'success': True,
        'data': {
            **user,
            'isPaid': user['is_paid'] == 1 or user['is_admin'] == 1,
            'isAdmin': user['is_admin'] == 1,
        }
    })
