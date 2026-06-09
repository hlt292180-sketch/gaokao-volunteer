# 用户行为统计路由 —— 埋点记录 + 后台统计查询
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from database.db import get_conn

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/track', methods=['POST'])
def track_event():
    """
    POST /api/analytics/track
    Body: {
      "event_type": "page_view",
      "score": 620,        // 可选
      "rank": 8680,        // 可选
      "device_type": "mobile"  // 可选
    }

    记录用户行为事件，无需登录（未登录时 user_id 为 NULL）。
    """
    data = request.get_json() or {}
    event_type = data.get('event_type')
    if not event_type:
        return jsonify({'success': False, 'message': '缺少 event_type'}), 400

    # 允许的事件类型白名单
    allowed = {'page_view', 'score_input', 'plan_generate', 'pay_click',
               'pay_confirm', 'register', 'login', 'favorite_add', 'upgrade_view'}
    if event_type not in allowed:
        return jsonify({'success': False, 'message': f'无效的事件类型：{event_type}'}), 400

    # 尝试从 JWT 解析 user_id（可选，未登录也能记录）
    user_id = None
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        try:
            import jwt
            from config import Config
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('userId')  # JWT payload 中存的是驼峰命名
        except Exception:
            pass  # token 无效也继续记录

    score = data.get('score')
    rank_val = data.get('rank')
    device_type = data.get('device_type', '')

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO analytics_events (user_id, event_type, score, `rank`, device_type)"
        " VALUES (%s, %s, %s, %s, %s)",
        (user_id, event_type, score, rank_val, device_type)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True, 'message': 'ok'}), 201


@analytics_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    GET /api/analytics/stats?days=7

    返回指定天数内的统计指标。仅管理员可调用。
    """
    # 🔒 管理员鉴权
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': '请先登录'}), 401
    try:
        import jwt
        from config import Config
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        admin_id = payload.get('userId')
    except Exception:
        return jsonify({'success': False, 'message': '无效的登录凭证'}), 401

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (admin_id,))
    admin_row = cur.fetchone()
    if not admin_row or admin_row['is_admin'] != 1:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '仅管理员可查看统计'}), 403

    days = request.args.get('days', 7, type=int)
    since = datetime.now() - timedelta(days=days)

    conn = get_conn()
    cur = conn.cursor()

    # 总访问人数（page_view 去重 IP 或用 user_id）
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) as cnt FROM analytics_events"
        " WHERE event_type='page_view' AND event_time >= %s AND user_id IS NOT NULL",
        (since,)
    )
    visitors = cur.fetchone()['cnt']

    # 输入分数人数
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) as cnt FROM analytics_events"
        " WHERE event_type='score_input' AND event_time >= %s AND user_id IS NOT NULL",
        (since,)
    )
    score_input_users = cur.fetchone()['cnt']

    # 生成方案人数
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) as cnt FROM analytics_events"
        " WHERE event_type='plan_generate' AND event_time >= %s AND user_id IS NOT NULL",
        (since,)
    )
    plan_users = cur.fetchone()['cnt']

    # 点击付款人数
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) as cnt FROM analytics_events"
        " WHERE event_type='pay_click' AND event_time >= %s AND user_id IS NOT NULL",
        (since,)
    )
    pay_click_users = cur.fetchone()['cnt']

    # 确认付款人数
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) as cnt FROM analytics_events"
        " WHERE event_type='pay_confirm' AND event_time >= %s AND user_id IS NOT NULL",
        (since,)
    )
    pay_confirm_users = cur.fetchone()['cnt']

    # 收藏人数
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) as cnt FROM analytics_events"
        " WHERE event_type='favorite_add' AND event_time >= %s AND user_id IS NOT NULL",
        (since,)
    )
    favorite_users = cur.fetchone()['cnt']

    # 查看升级页人数
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) as cnt FROM analytics_events"
        " WHERE event_type='upgrade_view' AND event_time >= %s AND user_id IS NOT NULL",
        (since,)
    )
    upgrade_view_users = cur.fetchone()['cnt']

    # 注册人数（直接从 users 表取更准确，但这里用埋点数据保持一致性）
    cur.execute(
        "SELECT COUNT(*) as cnt FROM users WHERE created_at >= %s",
        (since,)
    )
    register_total = cur.fetchone()['cnt']

    # 每日趋势（最近 N 天，每天的事件数）
    cur.execute(
        "SELECT DATE(event_time) as dt, event_type, COUNT(*) as cnt"
        " FROM analytics_events"
        " WHERE event_time >= %s"
        " GROUP BY DATE(event_time), event_type"
        " ORDER BY dt ASC",
        (since,)
    )
    daily_rows = cur.fetchall()

    cur.close()
    conn.close()

    # 组装每日趋势数据
    daily = {}
    for row in daily_rows:
        dt_str = row['dt'].strftime('%m-%d') if hasattr(row['dt'], 'strftime') else str(row['dt'])[-5:]
        if dt_str not in daily:
            daily[dt_str] = {}
        daily[dt_str][row['event_type']] = row['cnt']

    # 计算转化率
    def rate(part, total):
        if not total:
            return '0%'
        return f'{round(part / total * 100, 1)}%'

    return jsonify({
        'success': True,
        'data': {
            'period': f'最近 {days} 天',
            'metrics': {
                'visitors': visitors,
                'scoreInputUsers': score_input_users,
                'planUsers': plan_users,
                'favoriteUsers': favorite_users,
                'upgradeViewUsers': upgrade_view_users,
                'payClickUsers': pay_click_users,
                'payConfirmUsers': pay_confirm_users,
                'registerTotal': register_total,
            },
            'conversion': {
                'visitToScore': rate(score_input_users, visitors),
                'scoreToPlan': rate(plan_users, score_input_users),
                'planToFavorite': rate(favorite_users, plan_users),
                'favoriteToUpgrade': rate(upgrade_view_users, favorite_users),
                'upgradeToPayClick': rate(pay_click_users, upgrade_view_users),
                'payClickToConfirm': rate(pay_confirm_users, pay_click_users),
                'visitToPay': rate(pay_confirm_users, visitors),
            },
            'daily': daily,  # 每日事件数
        }
    })


@analytics_bp.route('/funnel', methods=['GET'])
def get_funnel():
    """
    GET /api/analytics/funnel?days=30 —— 转化漏斗数据

    返回从首页访问到付费成功的完整转化链路。
    仅管理员可调用。
    """
    # 管理员鉴权
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': '请先登录'}), 401
    try:
        import jwt
        from config import Config
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        admin_id = payload.get('userId')
    except Exception:
        return jsonify({'success': False, 'message': '无效的登录凭证'}), 401

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (admin_id,))
    admin_row = cur.fetchone()
    if not admin_row or admin_row['is_admin'] != 1:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '仅管理员可查看'}), 403

    days = request.args.get('days', 30, type=int)
    since = datetime.now() - timedelta(days=days)

    # 漏斗各步骤人数（DISTINCT user_id）
    steps = [
        ('page_view', '首页访问'),
        ('register', '注册'),
        ('score_input', '完成测评/换算'),
        ('plan_generate', '生成方案'),
        ('favorite_add', '收藏院校/专业'),
        ('upgrade_view', '查看升级页'),
        ('pay_click', '点击升级'),
        ('pay_confirm', '确认付款'),
    ]

    funnel = []
    prev = None
    for event_type, label in steps:
        cur.execute(
            "SELECT COUNT(DISTINCT user_id) as cnt FROM analytics_events"
            " WHERE event_type=%s AND event_time >= %s AND user_id IS NOT NULL",
            (event_type, since)
        )
        cnt = cur.fetchone()['cnt']
        rate_str = ''
        if prev and prev > 0:
            rate_str = f'{round(cnt / prev * 100, 1)}%'
        funnel.append({
            'step': label,
            'eventType': event_type,
            'count': cnt,
            'rate': rate_str if rate_str else '-',
        })
        prev = cnt

    # 付费成功（从 users 表直接取）
    cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_paid=1 AND created_at >= %s", (since,))
    paid_cnt = cur.fetchone()['cnt']
    rate_str = ''
    if prev and prev > 0:
        rate_str = f'{round(paid_cnt / prev * 100, 1)}%'
    funnel.append({
        'step': '付费成功',
        'eventType': 'paid',
        'count': paid_cnt,
        'rate': rate_str if rate_str else '-',
    })

    cur.close(); conn.close()

    return jsonify({'success': True, 'data': {'period': f'最近 {days} 天', 'funnel': funnel}})


# ========== 数据质量仪表盘（管理员）==========
@analytics_bp.route('/data-quality', methods=['GET'])
def data_quality_dashboard():
    """
    GET /api/analytics/data-quality

    返回 admissions_scores 表的数据来源分布统计。
    管理员后台数据质量仪表盘使用。
    """
    conn = get_conn()
    cur = conn.cursor()

    # 1. admission_scores 数据来源分布
    cur.execute(
        "SELECT data_source, verified_level, COUNT(*) as cnt"
        " FROM admission_scores GROUP BY data_source, verified_level"
        " ORDER BY data_source, verified_level"
    )
    source_rows = cur.fetchall()

    # 2. 按科类+年份统计真实数据覆盖率
    cur.execute(
        "SELECT year, subject_type,"
        " COUNT(*) as total,"
        " SUM(CASE WHEN data_source='OFFICIAL' THEN 1 ELSE 0 END) as official,"
        " SUM(CASE WHEN data_source='SIMULATED' THEN 1 ELSE 0 END) as simulated,"
        " SUM(CASE WHEN data_source='MANUAL' THEN 1 ELSE 0 END) as manual"
        " FROM admission_scores GROUP BY year, subject_type ORDER BY year, subject_type"
    )
    yearly_rows = cur.fetchall()

    # 3. 一分一段表统计
    cur.execute(
        "SELECT COUNT(*) as total, COUNT(DISTINCT year) as years,"
        " COUNT(DISTINCT subject_type) as subjects"
        " FROM score_segments"
    )
    seg_stats = cur.fetchone()

    # 4. 专业数据覆盖
    cur.execute("SELECT COUNT(*) FROM major_profiles")
    profiles_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM major_trends")
    trends_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM majors")
    majors_total = cur.fetchone()[0]

    # 5. 总体真实数据率
    cur.execute(
        "SELECT COUNT(*) as total, SUM(CASE WHEN data_source='OFFICIAL' THEN 1 ELSE 0 END) as official"
        " FROM admission_scores"
    )
    overall = cur.fetchone()
    total_all = overall['total'] or 1
    official_all = overall['official'] or 0
    overall_rate = round(official_all / total_all * 100, 1)

    cur.close()
    conn.close()

    return jsonify({
        'success': True,
        'data': {
            'overall': {
                'totalRecords': total_all,
                'officialRecords': official_all,
                'simulatedRecords': total_all - official_all,
                'realDataRate': overall_rate,
                'allowPayment': overall_rate >= 95,
            },
            'sourceDistribution': [
                {'source': r['data_source'], 'verifiedLevel': r['verified_level'], 'count': r['cnt']}
                for r in source_rows
            ],
            'yearlyBreakdown': [
                {
                    'year': r['year'], 'subjectType': r['subject_type'],
                    'total': r['total'], 'official': r['official'],
                    'simulated': r['simulated'], 'manual': r['manual'],
                    'rate': round(r['official'] / r['total'] * 100, 1) if r['total'] > 0 else 0,
                }
                for r in yearly_rows
            ],
            'segments': {
                'totalRecords': seg_stats['total'],
                'yearsCovered': seg_stats['years'],
                'subjectsCovered': seg_stats['subjects'],
                'isReal': True,  # 一分一段已全部替换为真实数据
            },
            'profilesCoverage': {
                'majorProfiles': profiles_cnt,
                'majorTrends': trends_cnt,
                'majorsTotal': majors_total,
                'coverageRate': round(profiles_cnt / majors_total * 100, 1) if majors_total > 0 else 0,
            },
        }
    })


# ========== 业务覆盖率仪表盘（替代旧 data-quality）==========
@analytics_bp.route('/coverage', methods=['GET'])
def coverage_dashboard():
    """
    GET /api/analytics/coverage

    返回业务覆盖率评分（非记录级覆盖率）。
    这是收费开关的核心依据。
    """
    try:
        from services.coverage_service import calculate_coverage
        data = calculate_coverage()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
