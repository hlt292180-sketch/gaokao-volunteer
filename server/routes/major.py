# 专业相关路由
from flask import Blueprint, jsonify, request
from database.db import get_conn

major_bp = Blueprint('major', __name__)

# ===== 专业列表 =====
@major_bp.route('/')
def list_majors():
    """
    GET /api/majors?keyword=计算机&category=工学&page=1&limit=12
    """

    keyword  = request.args.get('keyword', '')
    category = request.args.get('category', '')
    page     = request.args.get('page', 1, type=int)
    limit    = request.args.get('limit', 12, type=int)

    conn = get_conn()
    cur = conn.cursor()

    where_parts = ["1=1"]
    params = []

    if keyword:
        where_parts.append("(name LIKE %s OR subcategory LIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if category:
        where_parts.append("category=%s")
        params.append(category)

    where_clause = " AND ".join(where_parts)

    cur.execute(f"SELECT COUNT(*) AS total FROM majors WHERE {where_clause}", params)
    total = cur.fetchone()['total']

    offset = (page - 1) * limit
    cur.execute(
        f"SELECT * FROM majors WHERE {where_clause}"
        f" ORDER BY id ASC LIMIT %s OFFSET %s",
        params + [limit, offset]
    )
    rows = cur.fetchall()

    cur.close(); conn.close()

    return jsonify({
        'success': True,
        'data': rows,
        'pagination': {
            'page': page, 'limit': limit,
            'total': total,
            'totalPages': (total + limit - 1) // limit,
        }
    })


# ===== 专业详情 + 就业画像 =====
@major_bp.route('/<int:major_id>')
def get_major(major_id):
    """
    GET /api/majors/5

    功能：查专业基本信息 + 就业画像（薪资、就业率、去向）
    """

    conn = get_conn()
    cur = conn.cursor()

    # 查专业信息
    cur.execute("SELECT * FROM majors WHERE id=%s", (major_id,))
    major = cur.fetchone()
    if not major:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '专业不存在'}), 404

    # 查就业画像
    cur.execute("SELECT * FROM major_profiles WHERE major_id=%s", (major_id,))
    profile = cur.fetchone()

    cur.close(); conn.close()

    return jsonify({
        'success': True,
        'data': {**major, 'profile': profile}
    })


# ===== 专业趋势预测（付费接口）=====
@major_bp.route('/<int:major_id>/trend')
def get_major_trend(major_id):
    """
    GET /api/majors/5/trend

    返回该专业未来4年的趋势预测（需求走向、薪资预测、饱和度）。
    虽然是付费功能，但数据通过 API 返回，前端根据 isPaid 打码。
    """

    conn = get_conn()
    cur = conn.cursor()

    # 查专业是否存在
    cur.execute("SELECT id, name FROM majors WHERE id=%s", (major_id,))
    major = cur.fetchone()
    if not major:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '专业不存在'}), 404

    # 查最新趋势预测数据
    cur.execute(
        "SELECT * FROM major_trends WHERE major_id=%s ORDER BY year_forecast DESC LIMIT 1",
        (major_id,)
    )
    trend = cur.fetchone()
    cur.close(); conn.close()

    if not trend:
        return jsonify({'success': True, 'data': None})

    return jsonify({
        'success': True,
        'data': {
            'majorName': major['name'],
            'yearForecast': trend['year_forecast'],
            'demandTrend': trend['demand_trend'],
            'saturationLevel': trend['saturation_level'],
            'avgSalaryForecast': trend['avg_salary_forecast'],
            'confidence': trend['confidence'],
            'dataSource': trend['data_source'],
            'summary': trend['summary'],
        }
    })
