# 收藏功能路由 —— 收藏/取消收藏院校和专业
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import login_required
from database.db import get_conn

fav_bp = Blueprint('favorite', __name__)


@fav_bp.route('/universities', methods=['GET'])
@login_required
def list_fav_universities():
    """GET /api/favorites/universities —— 我的收藏院校列表"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.id, f.created_at, u.id AS university_id, u.name, u.city, u.level, u.type
        FROM favorite_universities f
        JOIN universities u ON f.university_id = u.id
        WHERE f.user_id = %s ORDER BY f.created_at DESC
    """, (request.user_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({'success': True, 'data': rows})


@fav_bp.route('/universities/<int:university_id>', methods=['POST'])
@login_required
def fav_university(university_id):
    """POST /api/favorites/universities/1 —— 收藏院校"""
    conn = get_conn()
    cur = conn.cursor()
    # 检查院校存在
    cur.execute("SELECT id FROM universities WHERE id=%s", (university_id,))
    if not cur.fetchone():
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '院校不存在'}), 404
    try:
        cur.execute(
            "INSERT INTO favorite_universities (user_id, university_id) VALUES (%s, %s)",
            (request.user_id, university_id)
        )
        conn.commit()
        cur.close(); conn.close()
        return jsonify({'success': True, 'message': '已收藏'}), 201
    except Exception:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '已收藏过该院校'}), 400


@fav_bp.route('/universities/<int:university_id>', methods=['DELETE'])
@login_required
def unfav_university(university_id):
    """DELETE /api/favorites/universities/1 —— 取消收藏"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM favorite_universities WHERE user_id=%s AND university_id=%s",
        (request.user_id, university_id)
    )
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'success': True, 'message': '已取消收藏'})


@fav_bp.route('/majors', methods=['GET'])
@login_required
def list_fav_majors():
    """GET /api/favorites/majors —— 我的收藏专业列表"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.id, f.created_at, m.id AS major_id, m.name, m.category, m.degree
        FROM favorite_majors f
        JOIN majors m ON f.major_id = m.id
        WHERE f.user_id = %s ORDER BY f.created_at DESC
    """, (request.user_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({'success': True, 'data': rows})


@fav_bp.route('/majors/<int:major_id>', methods=['POST'])
@login_required
def fav_major(major_id):
    """POST /api/favorites/majors/1 —— 收藏专业"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM majors WHERE id=%s", (major_id,))
    if not cur.fetchone():
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '专业不存在'}), 404
    try:
        cur.execute(
            "INSERT INTO favorite_majors (user_id, major_id) VALUES (%s, %s)",
            (request.user_id, major_id)
        )
        conn.commit()
        cur.close(); conn.close()
        return jsonify({'success': True, 'message': '已收藏'}), 201
    except Exception:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '已收藏过该专业'}), 400


@fav_bp.route('/majors/<int:major_id>', methods=['DELETE'])
@login_required
def unfav_major(major_id):
    """DELETE /api/favorites/majors/1 —— 取消收藏"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM favorite_majors WHERE user_id=%s AND major_id=%s",
        (request.user_id, major_id)
    )
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'success': True, 'message': '已取消收藏'})


@fav_bp.route('/check', methods=['GET'])
@login_required
def check_fav():
    """GET /api/favorites/check?type=university&ids=1,2,3 —— 批量查询收藏状态"""
    fav_type = request.args.get('type', 'university')
    ids_str = request.args.get('ids', '')
    if not ids_str:
        return jsonify({'success': True, 'data': []})

    ids = [int(x) for x in ids_str.split(',') if x.strip().isdigit()]
    if not ids:
        return jsonify({'success': True, 'data': []})

    conn = get_conn()
    cur = conn.cursor()
    if fav_type == 'university':
        table = 'favorite_universities'
        col = 'university_id'
    else:
        table = 'favorite_majors'
        col = 'major_id'

    placeholders = ','.join(['%s'] * len(ids))
    cur.execute(
        f"SELECT {col} FROM {table} WHERE user_id=%s AND {col} IN ({placeholders})",
        [request.user_id] + ids
    )
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({'success': True, 'data': [r[col] for r in rows]})
