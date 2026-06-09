# 院校相关路由
from flask import Blueprint, jsonify, request
from database.db import get_conn

uni_bp = Blueprint('university', __name__)

# ===== 院校列表（支持筛选 + 分页）=====
@uni_bp.route('/')
def list_universities():
    """
    GET /api/universities?keyword=南京&level=本科&type=综合&page=1&limit=12

    功能：按条件筛院校，分页返回
    """

    # 拿参数
    keyword = request.args.get('keyword', '')
    level   = request.args.get('level', '')
    utype   = request.args.get('type', '')       # type 是 Python 保留字，用 utype
    page    = request.args.get('page', 1, type=int)
    limit   = request.args.get('limit', 12, type=int)

    conn = get_conn()
    cur = conn.cursor()

    # 动态拼接查询条件（用参数化查询，手动构造 WHERE 子句）
    where_parts = ["1=1"]  # 占位，方便后面 AND 拼接
    params = []

    if keyword:
        where_parts.append("name LIKE %s")
        params.append(f"%{keyword}%")
    if level:
        where_parts.append("`level`=%s")
        params.append(level)
    if utype:
        where_parts.append("`type`=%s")
        params.append(utype)

    where_clause = " AND ".join(where_parts)

    # 查总数（分页需要）
    cur.execute(f"SELECT COUNT(*) AS total FROM universities WHERE {where_clause}", params)
    total = cur.fetchone()['total']

    # 查数据
    offset = (page - 1) * limit
    cur.execute(
        f"SELECT * FROM universities WHERE {where_clause}"
        " ORDER BY is_985 DESC, is_211 DESC, id ASC"
        f" LIMIT %s OFFSET %s",
        params + [limit, offset]
    )
    rows = cur.fetchall()

    cur.close(); conn.close()

    return jsonify({
        'success': True,
        'data': rows,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'totalPages': (total + limit - 1) // limit,  # 向上取整
        }
    })


# ===== 院校详情 + 历年录取线 =====
@uni_bp.route('/<int:uni_id>')
def get_university(uni_id):
    """
    GET /api/universities/5

    功能：查院校基本信息 + 历年录取分数
    """

    conn = get_conn()
    cur = conn.cursor()

    # 查院校信息
    cur.execute("SELECT * FROM universities WHERE id=%s", (uni_id,))
    uni = cur.fetchone()
    if not uni:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '院校不存在'}), 404

    # 查历年录取分（取该校各专业最高/最低分，按年份聚合）
    cur.execute(
        "SELECT year, batch, subject_type,"
        " MIN(min_score) as min_score, MIN(min_rank) as min_rank,"
        " ROUND(AVG(avg_score)) as avg_score, SUM(plan_count) as plan_count"
        " FROM admission_scores"
        " WHERE university_id=%s"
        " GROUP BY year, batch, subject_type"
        " ORDER BY year DESC, batch",
        (uni_id,)
    )
    scores = cur.fetchall()

    cur.close(); conn.close()

    return jsonify({
        'success': True,
        'data': {**uni, 'admissionScores': scores}
    })
