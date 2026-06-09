# 测评路由 —— 霍兰德职业兴趣测评
from flask import Blueprint, jsonify, request
from database.db import get_conn
from middleware.auth_middleware import login_required

assess_bp = Blueprint('assessment', __name__)

# ===== 获取测评题目 =====
@assess_bp.route('/questions', methods=['GET'])
@login_required      # 🔒 需登录
def get_questions():
    """GET /api/assessments/questions —— 返回30道测评题"""

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, question_text, options, dimension FROM assessment_questions ORDER BY id")
    rows = cur.fetchall()
    cur.close(); conn.close()

    return jsonify({'success': True, 'data': rows})


# ===== 提交测评答案 =====
@assess_bp.route('/submit', methods=['POST'])
@login_required
def submit_assessment():
    """
    POST /api/assessments/submit
    Body: { "scores": {"R":85,"I":72,"A":45,"S":60,"E":38,"C":55} }

    流程：
    1. 接收六维得分
    2. 计算主导类型（最高分那个维度）
    3. 存到数据库
    4. 更新免费测评计数
    """

    data = request.get_json()
    scores = data.get('scores')  # dict: {"R":85,...}

    if not scores or len(scores) != 6:
        return jsonify({'success': False, 'message': '请提供完整的6维得分'}), 400

    # 找出主导类型（得分最高的维度）
    primary = max(scores, key=scores.get)

    conn = get_conn()
    cur = conn.cursor()

    # 🔒 检查免费测评次数：免费用户超过1次则拒绝
    cur.execute("SELECT is_paid, is_admin, free_assessment_count FROM users WHERE id=%s", (request.user_id,))
    user = cur.fetchone()
    is_paid = user['is_paid'] == 1 or user['is_admin'] == 1
    if not is_paid and user['free_assessment_count'] >= 1:
        cur.close(); conn.close()
        return jsonify({
            'success': False,
            'message': '免费测评次数已用完，请升级付费版',
            'code': 'PAYMENT_REQUIRED'
        }), 403

    # 保存结果
    import json
    cur.execute(
        "INSERT INTO assessment_results (user_id, result_scores, primary_type) VALUES (%s, %s, %s)",
        (request.user_id, json.dumps(scores), primary)
    )
    result_id = cur.lastrowid

    # 免费用户更新计数
    cur.execute(
        "UPDATE users SET free_assessment_count = free_assessment_count + 1"
        " WHERE id=%s AND is_paid=0 AND is_admin=0",
        (request.user_id,)
    )
    conn.commit()
    cur.close(); conn.close()

    return jsonify({
        'success': True,
        'data': {'id': result_id, 'primaryType': primary}
    }), 201


# ===== 获取最新测评结果 =====
@assess_bp.route('/latest', methods=['GET'])
@login_required
def get_latest():
    """GET /api/assessments/latest —— 返回当前用户最新的测评结果"""

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM assessment_results WHERE user_id=%s ORDER BY created_at DESC LIMIT 1",
        (request.user_id,)
    )
    row = cur.fetchone()
    cur.close(); conn.close()

    if not row:
        return jsonify({'success': False, 'message': '暂无测评记录'}), 404

    return jsonify({'success': True, 'data': row})


# ===== 查看指定测评结果 =====
@assess_bp.route('/result/<int:result_id>', methods=['GET'])
@login_required
def get_result(result_id):
    """
    GET /api/assessments/result/1
    只能查看自己的结果
    """

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM assessment_results WHERE id=%s AND user_id=%s",
        (result_id, request.user_id)
    )
    row = cur.fetchone()
    cur.close(); conn.close()

    if not row:
        return jsonify({'success': False, 'message': '结果不存在'}), 404

    return jsonify({'success': True, 'data': row})
