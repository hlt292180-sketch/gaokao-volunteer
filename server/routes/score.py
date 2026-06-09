# 分数位次相关路由 —— 线性插值版
from flask import Blueprint, jsonify, request
from database.db import get_conn

score_bp = Blueprint('score', __name__)


def _interpolate_rank(cur, province_id, year, score, subject_type):
    """
    查询 score → rank，精确匹配失败时用上下边界线性插值。

    返回: (rank: int, None) 成功 或 (None, error_msg: str) 失败
    """
    # 1. 先查精确匹配
    cur.execute(
        "SELECT `rank` FROM score_segments"
        " WHERE province_id=%s AND year=%s AND score=%s AND subject_type=%s",
        (province_id, year, score, subject_type)
    )
    row = cur.fetchone()
    if row:
        return row['rank'], None

    # 2. 查上下边界
    cur.execute(
        "SELECT score, `rank` FROM score_segments"
        " WHERE province_id=%s AND year=%s AND subject_type=%s AND score < %s"
        " ORDER BY score DESC LIMIT 1",
        (province_id, year, subject_type, score)
    )
    lower = cur.fetchone()

    cur.execute(
        "SELECT score, `rank` FROM score_segments"
        " WHERE province_id=%s AND year=%s AND subject_type=%s AND score > %s"
        " ORDER BY score ASC LIMIT 1",
        (province_id, year, subject_type, score)
    )
    upper = cur.fetchone()

    # 3. 边界检查
    if not lower:
        return None, '分数低于当前一分一段表最低值，无法换算'
    if not upper:
        return None, '分数高于当前一分一段表最高值，无法换算'

    # 4. 线性插值: rank = lower_rank - (lower_rank - upper_rank) * ratio
    ratio = (score - lower['score']) / (upper['score'] - lower['score'])
    rank = lower['rank'] - (lower['rank'] - upper['rank']) * ratio
    return int(round(rank)), None


def _interpolate_score(cur, province_id, year, rank, subject_type):
    """
    查询 rank → score，精确匹配失败时用线性插值。
    返回: (score: int, None) 成功 或 (None, None) 找不到
    """
    # 1. 精确匹配
    cur.execute(
        "SELECT score FROM score_segments"
        " WHERE province_id=%s AND year=%s AND subject_type=%s AND `rank`=%s",
        (province_id, year, subject_type, rank)
    )
    row = cur.fetchone()
    if row:
        return row['score'], None

    # 2. 上下边界（rank 越小表示成绩越好，所以 lower_rank > upper_rank）
    cur.execute(
        "SELECT score, `rank` FROM score_segments"
        " WHERE province_id=%s AND year=%s AND subject_type=%s AND `rank` > %s"
        " ORDER BY `rank` ASC LIMIT 1",
        (province_id, year, subject_type, rank)
    )
    lower = cur.fetchone()  # rank 更大的记录 = 分数更低的边界

    cur.execute(
        "SELECT score, `rank` FROM score_segments"
        " WHERE province_id=%s AND year=%s AND subject_type=%s AND `rank` < %s"
        " ORDER BY `rank` DESC LIMIT 1",
        (province_id, year, subject_type, rank)
    )
    upper = cur.fetchone()  # rank 更小的记录 = 分数更高的边界

    if not lower or not upper:
        return None, None

    # 3. 线性插值: score = lower_score + (upper_score - lower_score) * ratio
    rank_range = lower['rank'] - upper['rank']
    if rank_range == 0:
        return lower['score'], None
    ratio = (rank - upper['rank']) / rank_range
    score = upper['score'] - (upper['score'] - lower['score']) * ratio
    return int(round(score)), None


# ==================== 分数 → 位次换算 ====================
@score_bp.route('/convert')
def convert_score():
    """
    GET /api/score-segments/convert?provinceId=1&year=2025&score=612&subjectType=物理类&targetYear=2024

    逻辑：
    1. 当前分数 → 位次（精确匹配或线性插值）
    2. 位次 → 目标年份等效分（精确匹配或线性插值）
    """
    province_id = request.args.get('provinceId', type=int)
    year        = request.args.get('year', type=int)
    score       = request.args.get('score', type=int)
    subject_type = request.args.get('subjectType', '物理类')
    target_year  = request.args.get('targetYear', type=int)

    if not all([province_id, year, score, target_year]):
        return jsonify({'success': False, 'message': '请提供 provinceId, year, score, targetYear'}), 400

    conn = get_conn()
    cur = conn.cursor()

    # ---- 第3步：分数 → 位次（含线性插值）----
    current_rank, err = _interpolate_rank(cur, province_id, year, score, subject_type)
    if err:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': err}), 400

    # ---- 第4步：位次 → 目标年份等效分（含线性插值）----
    equivalent_score, _ = _interpolate_score(cur, province_id, target_year, current_rank, subject_type)

    cur.close()
    conn.close()

    return jsonify({
        'success': True,
        'data': {
            'currentScore': score,
            'currentYear': year,
            'rank': current_rank,
            'targetYear': target_year,
            'equivalentScore': equivalent_score,
        }
    })
