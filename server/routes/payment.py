# 支付相关路由 —— 创建订单 / 查询状态
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import login_required
from database.db import get_conn

pay_bp = Blueprint('payment', __name__)


@pay_bp.route('/create', methods=['POST'])
@login_required
def create_payment():
    """
    POST /api/payment/create
    Body: { "amount": 39, "plan": "standard" }

    创建待审核支付记录。用户扫码付款后点"我已付款"，
    系统生成订单，管理员后台审核后手动开通。
    """
    data = request.get_json() or {}
    amount = data.get('amount', 39)
    plan = data.get('plan', 'standard')

    conn = get_conn()
    cur = conn.cursor()

    # 🔒 收费保护：自动检测真实数据覆盖率
    from config import Config
    if not Config.get_allow_payment():
        cur.close(); conn.close()
        return jsonify({
            'success': False,
            'message': f'收费功能暂未开放。系统商业化评分未达到 {Config.MIN_COMMERCIAL_SCORE} 分门槛。',
            'code': 'PAYMENT_DISABLED',
            'requiredScore': Config.MIN_COMMERCIAL_SCORE,
        }), 403

    # 🔒 去重：同一用户已有 pending 订单时直接返回已有订单
    cur.execute(
        "SELECT order_no, amount, created_at FROM payments"
        " WHERE user_id=%s AND status='pending'"
        " ORDER BY created_at DESC LIMIT 1",
        (request.user_id,)
    )
    existing = cur.fetchone()
    if existing:
        cur.close(); conn.close()
        return jsonify({
            'success': True,
            'data': {
                'orderNo': existing['order_no'],
                'amount': existing['amount'],
                'status': 'pending',
                'message': '您已有待审核的付款记录，请勿重复提交，等待管理员审核开通即可',
            }
        })

    # 生成唯一订单号：时间戳 + UUID 前6位
    order_no = datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid.uuid4())[:6]

    cur.execute(
        "INSERT INTO payments (user_id, amount, status, order_no, plan)"
        " VALUES (%s, %s, %s, %s, %s)",
        (request.user_id, amount, 'pending', order_no, plan)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        'success': True,
        'data': {
            'orderNo': order_no,
            'amount': amount,
            'status': 'pending',
            'message': '支付记录已创建，请等待管理员审核开通',
        }
    }), 201


@pay_bp.route('/status/<order_no>', methods=['GET'])
@login_required
def check_status(order_no):
    """GET /api/payment/status/:orderNo —— 查询支付状态"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT status, amount, plan, paid_at FROM payments"
        " WHERE order_no=%s AND user_id=%s",
        (order_no, request.user_id)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({'success': False, 'message': '订单不存在'}), 404

    return jsonify({'success': True, 'data': row})


# ========== 管理员接口 ==========

@pay_bp.route('/pending', methods=['GET'])
@login_required
def list_pending():
    """
    GET /api/payment/pending —— 管理员查看待审核支付列表

    返回所有 status='pending' 的订单，JOIN users 表获取手机号。
    仅管理员可调用。
    """
    conn = get_conn()
    cur = conn.cursor()

    # 校验管理员身份
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (request.user_id,))
    admin = cur.fetchone()
    if not admin or admin['is_admin'] != 1:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '仅管理员可操作'}), 403

    cur.execute(
        "SELECT p.id, p.order_no, p.amount, p.plan, p.status, p.created_at,"
        " u.id AS user_id, u.phone, u.nickname"
        " FROM payments p JOIN users u ON p.user_id = u.id"
        " WHERE p.status = 'pending'"
        " ORDER BY p.created_at DESC"
    )
    rows = cur.fetchall()
    cur.close(); conn.close()

    return jsonify({'success': True, 'data': rows, 'total': len(rows)})


@pay_bp.route('/approve/<order_no>', methods=['POST'])
@login_required
def approve_payment(order_no):
    """
    POST /api/payment/approve/:orderNo —— 管理员审核通过一笔支付

    操作：
    1. 更新 payments 表：status='paid', paid_at=now
    2. 更新 users 表：is_paid=1
    """
    conn = get_conn()
    cur = conn.cursor()

    # 校验管理员
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (request.user_id,))
    admin = cur.fetchone()
    if not admin or admin['is_admin'] != 1:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '仅管理员可操作'}), 403

    # 查找订单
    cur.execute(
        "SELECT id, user_id, status FROM payments WHERE order_no=%s",
        (order_no,)
    )
    payment = cur.fetchone()
    if not payment:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '订单不存在'}), 404

    if payment['status'] != 'pending':
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': f'订单状态为 {payment["status"]}，无法重复审核'}), 400

    # 更新支付记录
    cur.execute(
        "UPDATE payments SET status='paid', paid_at=NOW() WHERE order_no=%s",
        (order_no,)
    )

    # 开通用户付费权限
    cur.execute(
        "UPDATE users SET is_paid=1 WHERE id=%s",
        (payment['user_id'],)
    )

    conn.commit()
    cur.close(); conn.close()

    return jsonify({
        'success': True,
        'data': {
            'orderNo': order_no,
            'status': 'paid',
            'message': '审核通过，用户已开通付费权限',
        }
    })
