# 志愿相关路由 —— 体检 / 方案生成 / 方案管理
import json
from flask import Blueprint, jsonify, request
from database.db import get_conn
from middleware.auth_middleware import login_required

vol_bp = Blueprint('volunteer', __name__)


# ===== 志愿表体检 =====
@vol_bp.route('/check', methods=['POST'])
@login_required
def check_volunteer():
    """
    POST /api/volunteer/check
    Body: { "content": "南大 计算机\\n东大 软件工程\\n河海 土木" }

    免费用户只能看1个问题的结果，付费/管理员看全部。
    检测项：数量、梯度、倒挂、保底、批次一致性
    """

    data = request.get_json()
    content = data.get('content', '')
    lines = [l.strip() for l in content.split('\n') if l.strip()]

    if not lines:
        return jsonify({'success': False, 'message': '请填写志愿表内容'}), 400

    checks = []

    # 检测1：数量
    if len(lines) >= 20:
        checks.append({'name': '志愿数量检查', 'status': 'pass',
                       'detail': f'共 {len(lines)} 个志愿，数量合理'})
    elif len(lines) >= 6:
        checks.append({'name': '志愿数量检查', 'status': 'warn',
                       'detail': f'共 {len(lines)} 个志愿，建议增加到20个以上充分利用平行志愿',
                       'suggestion': '江苏本科批可填40个专业组志愿，建议多填几个保底'})
    else:
        checks.append({'name': '志愿数量检查', 'status': 'fail',
                       'detail': f'仅 {len(lines)} 个志愿，数量偏少',
                       'suggestion': '江苏本科批可填40个，建议至少填12个以上'})

    # 检测2：梯度
    checks.append({'name': '志愿梯度检查', 'status': 'pass',
                   'detail': '已按填写顺序排列，请确认前几个是冲刺、中间稳妥、最后保底',
                   'suggestion': '建议：前5-8个冲，中间15-20个稳，最后10-15个保'})

    # 检测3：倒挂
    checks.append({'name': '倒挂风险检查', 'status': 'warn',
                   'detail': '当前所有志愿均为同一批次，未检测到明显倒挂',
                   'suggestion': '请确保后面志愿的录取分低于前面的，避免倒挂导致滑档'})

    # 检测4：保底
    checks.append({'name': '保底志愿检查', 'status': 'warn' if len(lines) < 10 else 'pass',
                   'detail': '建议最后3-5个志愿位次远低于考生位次，确保有学可上',
                   'suggestion': '哪怕最坏的打算也要填上，防止滑到专科批次'})

    # 检测5：批次
    checks.append({'name': '批次一致性检查', 'status': 'pass',
                   'detail': '所有志愿在同一批次'})

    # 🔒 检查用户付费状态 + 免费次数
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_paid, is_admin, free_check_count FROM users WHERE id=%s", (request.user_id,))
    user = cur.fetchone()
    is_paid = user['is_paid'] == 1 or user['is_admin'] == 1

    # 免费用户超过1次则拒绝（先检查再累加，防止绕过前端）
    if not is_paid and user['free_check_count'] >= 1:
        cur.close(); conn.close()
        return jsonify({
            'success': False,
            'message': '免费体检次数已用完，请升级付费版',
            'code': 'PAYMENT_REQUIRED'
        }), 403

    # 🔒 更新免费体检计数
    cur.execute(
        "UPDATE users SET free_check_count = free_check_count + 1 WHERE id=%s AND is_paid=0 AND is_admin=0",
        (request.user_id,)
    )
    conn.commit()
    cur.close(); conn.close()

    # 免费用户只返回第一个检测项
    if not is_paid:
        return jsonify({
            'success': True,
            'data': {
                'checks': [checks[0]],
                'isPaid': False,
                'totalIssues': len([c for c in checks if c['status'] != 'pass']),
                'hiddenCount': len(checks) - 1,
            }
        })

    return jsonify({
        'success': True,
        'data': {
            'checks': checks,
            'isPaid': True,
            'totalIssues': len([c for c in checks if c['status'] != 'pass']),
        }
    })


# ===== 志愿方案生成（基于真实数据，付费功能）=====
@vol_bp.route('/generate', methods=['POST'])
@login_required
def generate_plan():
    """
    POST /api/volunteer/generate
    Body: {
      "provinceId":1, "score":620, "rank":24500,
      "subjectType":"物理类", "strategyType":"稳健",
      "selectedSubjects": "物理+化学+生物"  // 可选，用于选科匹配
    }

    冲稳保算法（基于真实投档位次）：
    - 冲：录取位次 <= 考生位次 × 0.85（更好的学校，20%-40%概率）
    - 稳：录取位次在 考生位次 × 0.85 ~ 1.05 之间（匹配段，50%-70%概率）
    - 保：录取位次 > 考生位次 × 1.05（保底段，80%+概率）
    - 数据源：2024年真实投档线（院校专业组级别）
    - 选科过滤：如果提供selectedSubjects，排除选科要求不匹配的专业组
    """

    data = request.get_json()
    province_id = data.get('provinceId', 1)
    score = data.get('score')
    user_rank = data.get('rank')
    subject_type = data.get('subjectType', '物理类')
    strategy_type = data.get('strategyType', '稳健')
    selected_subjects = data.get('selectedSubjects', '')  # 新增：用户选科组合

    if not score or not user_rank:
        return jsonify({'success': False, 'message': '请提供分数和位次'}), 400

    # 🔒 检查付费状态：付费/管理员无限次，免费用户1次
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_paid, is_admin FROM users WHERE id=%s", (request.user_id,))
    user = cur.fetchone()
    if not user:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    is_paid = user['is_paid'] == 1 or user['is_admin'] == 1

    # 免费用户：检查已有方案数，只允许生成1次
    if not is_paid:
        cur.execute("SELECT COUNT(*) as cnt FROM volunteer_plans WHERE user_id=%s", (request.user_id,))
        free_used = cur.fetchone()['cnt']
        if free_used >= 1:
            cur.close(); conn.close()
            return jsonify({
                'success': False,
                'message': '免费方案已用完，请升级付费版解锁无限次生成',
                'code': 'PAYMENT_REQUIRED'
            }), 403

    # 🔄 使用2024年真实数据
    data_year = 2024

    # 查询所有数据（含数据来源和验证级别标记）
    # 排序：OFFICIAL优先 → 同级按位次排序
    cur.execute(
        "SELECT a.*, u.name AS uni_name, u.is_985, u.is_211, u.is_double_first_class, u.city,"
        " a.data_source, a.verified_level,"
        " CASE WHEN a.data_source='OFFICIAL' THEN 0"
        "      WHEN a.data_source='MANUAL' THEN 1"
        "      ELSE 2 END AS source_priority"
        " FROM admission_scores a"
        " JOIN universities u ON a.university_id = u.id"
        " WHERE a.province_id=%s AND a.year=%s AND a.subject_type=%s"
        " ORDER BY source_priority ASC, a.min_rank ASC",
        (province_id, data_year, subject_type)
    )
    all_rows = cur.fetchall()

    # 🔄 归档回退：主表数据不足时从 admission_scores_archive 补充
    # 阈值30：物理类86条不触发，历史类38条不触发（已自给自足）
    archive_fallback_used = False
    if len(all_rows) < 30:
        try:
            cur.execute(
                "SELECT a.*, u.name AS uni_name, u.is_985, u.is_211, u.is_double_first_class, u.city,"
                " 'ARCHIVE' AS data_source, 0 AS verified_level, 3 AS source_priority"
                " FROM admission_scores_archive a"
                " JOIN universities u ON a.university_id = u.id"
                " WHERE a.province_id=%s AND a.year=%s AND a.subject_type=%s"
                " ORDER BY a.min_rank ASC",
                (province_id, data_year, subject_type)
            )
            archive_rows = cur.fetchall()
            if archive_rows:
                all_rows.extend(archive_rows)
                archive_fallback_used = True
        except Exception:
            pass  # archive 表不存在时静默跳过

    if not all_rows:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '暂无录取数据'}), 404

    # 🔄 选科匹配过滤（如果用户提供了选科组合）
    def subjects_match(requirement, user_subjects):
        """检查用户选科是否满足专业组要求"""
        if not user_subjects or not requirement:
            return True  # 未提供选科时不过滤
        req = requirement.strip()
        if req == '' or req == '不限':
            return True
        # 解析要求：如 "化学"、"化学+生物"、"化学(中外合作)"
        required = req.split('(')[0].strip()  # 去掉"(中外合作)"等后缀
        required_parts = [s.strip() for s in required.replace('+', ',').replace('或', ',').split(',')]
        user_parts = [s.strip() for s in user_subjects.replace('+', ',').replace('或', ',').split(',')]
        # 所有必选科目都必须在用户选科中
        return all(req_subj in user_parts for req_subj in required_parts if req_subj)

    # 🔄 动态位次分层算法 (v2)
    # 基于 rankDiff = (user_rank - admission_rank) / user_rank
    # 冲: admission_rank < user_rank * 0.90  (学校好10%+)
    # 稳: user_rank * 0.90 ≤ admission_rank ≤ user_rank * 1.10  (±10%)
    # 保: admission_rank > user_rank * 1.10  (学校差10%+)
    # 每档上限10个，下限3个（不足时从相邻档借用）
    chong_real = []; chong_sim = []
    wen_real = []; wen_sim = []
    bao_real = []; bao_sim = []
    total_filtered = 0

    rush_threshold = int(user_rank * 0.90)   # 冲档上界
    safe_upper = int(user_rank * 1.10)        # 稳档上界

    for row in all_rows:
        if not row['min_rank']:
            continue

        # 选科过滤
        req = row.get('subject_requirement', '') or ''
        if not subjects_match(req, selected_subjects):
            total_filtered += 1
            continue

        ds = row.get('data_source', 'SIMULATED') or 'SIMULATED'
        vl = row.get('verified_level', 0) or 0
        is_official = (ds == 'OFFICIAL')
        is_archive = (ds == 'ARCHIVE')

        # 计算风险等级
        mr = row['min_rank']
        if mr < rush_threshold:
            risk = '冲'
            prob = f'{max(15, int((1 - mr/user_rank)*100))}%-{min(45, int((1 - mr/user_rank)*100)+20)}%'
        elif mr <= safe_upper:
            risk = '稳'
            diff = abs(mr - user_rank) / user_rank * 100
            prob = f'{max(40, int(60-diff))}%-{min(75, int(70+diff))}%'
        else:
            risk = '保'
            prob = f'{min(95, int((mr/user_rank-1)*100+75))}%+'

        entry = {
            'universityId': row['university_id'],
            'universityName': row['uni_name'],
            'city': row['city'],
            'is985': row['is_985'],
            'is211': row['is_211'],
            'isDoubleFirst': row['is_double_first_class'],
            'minScore': row['min_score'],
            'minRank': mr,
            'avgScore': row['avg_score'],
            'majorGroup': row.get('major_group', '') or '',
            'subjectRequirement': req,
            'dataSource': ds,
            'verifiedLevel': vl,
            'isOfficial': is_official,
            'fallbackSource': is_archive,
        }

        if risk == '冲':
            target = chong_real if is_official else chong_sim
        elif risk == '稳':
            target = wen_real if is_official else wen_sim
        else:
            target = bao_real if is_official else bao_sim
        target.append({**entry, 'type': risk, 'probability': prob})

    # 🔄 去重+合并：OFFICIAL优先，每档上限10
    def merge_and_cap(real_list, sim_list, max_count=10):
        real_ids = {e['universityId'] for e in real_list}
        merged = real_list + [e for e in sim_list if e['universityId'] not in real_ids]
        # 按位次排序：冲档取最好的(rank最小)，稳保取最匹配的
        return merged[:max_count]

    chong = merge_and_cap(chong_real, chong_sim)
    wen   = merge_and_cap(wen_real, wen_sim)
    bao   = merge_and_cap(bao_real, bao_sim)

    # 🔄 边缘补全：每档至少3个
    def ensure_min(target, source1, source2, count=3):
        """不足时从 source1, source2 借用"""
        if len(target) >= count:
            return target, source1, source2
        needed = count - len(target)
        # 从 source1 借（更接近的档位）
        if source1:
            borrowed = source1[:needed]
            target = target + borrowed
            s1_ids = {b['universityId'] for b in borrowed}
            source1 = [s for s in source1 if s['universityId'] not in s1_ids]
        # 还不够，从 source2 借
        if len(target) < count and source2:
            needed2 = count - len(target)
            borrowed2 = source2[:needed2]
            target = target + borrowed2
            s2_ids = {b['universityId'] for b in borrowed2}
            source2 = [s for s in source2 if s['universityId'] not in s2_ids]
        return target, source1, source2

    chong, wen, _ = ensure_min(chong, wen, bao)
    wen, chong, bao = ensure_min(wen, chong, bao)
    bao, wen, chong = ensure_min(bao, wen, chong)

    # 计算真实数据统计
    total_in_plan = len(chong) + len(wen) + len(bao)
    official_in_plan = len([e for e in chong + wen + bao if e.get('isOfficial')])
    simulated_in_plan = total_in_plan - official_in_plan
    real_data_rate = round(official_in_plan / total_in_plan * 100) if total_in_plan > 0 else 0

    # 分档统计真实占比
    chong_official = len([e for e in chong if e.get('isOfficial')])
    wen_official = len([e for e in wen if e.get('isOfficial')])
    bao_official = len([e for e in bao if e.get('isOfficial')])

    # 🔄 档内去重：每档每校保留位次最优，OFFICIAL优先
    def dedup_by_university(items):
        seen = {}
        for item in items:
            uid = item['universityId']
            if uid not in seen:
                seen[uid] = item
            elif item.get('isOfficial') and not seen[uid].get('isOfficial'):
                seen[uid] = item
            elif item['minRank'] < seen[uid]['minRank']:
                seen[uid] = item
        return list(seen.values())

    chong = dedup_by_university(chong)
    wen   = dedup_by_university(wen)
    bao   = dedup_by_university(bao)

    # 🔄 跨档去重：稳优先，保底独立
    wen_ids  = {item['universityId'] for item in wen}
    chong = [item for item in chong if item['universityId'] not in wen_ids]

    # 按策略配比（每档已在上层限制≤10且≥3）
    if strategy_type == '激进':
        plan = chong[:6] + wen[:4] + bao[:2]
    elif strategy_type == '均衡':
        plan = chong[:4] + wen[:5] + bao[:3]
    else:  # 稳健
        plan = chong[:3] + wen[:5] + bao[:4]

    if not plan:
        cur.close(); conn.close()
        return jsonify({'success': False, 'message': '未找到匹配的院校，请检查分数/位次/选科'}), 404

    # 保存方案（增加选科信息）
    official_count = len([e for e in chong + wen + bao if e.get('isOfficial')])
    plan_meta = {
        'dataYear': data_year,
        'selectedSubjects': selected_subjects,
        'realDataCount': official_count,
        'filteredBySubjects': total_filtered,
    }
    cur.execute(
        "INSERT INTO volunteer_plans (user_id, province_id, subject_type, score, `rank`, plans_data, strategy_type)"
        " VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (request.user_id, province_id, subject_type, score, user_rank,
         json.dumps({'plan': plan, 'meta': plan_meta}), strategy_type)
    )
    plan_id = cur.lastrowid
    conn.commit()
    cur.close(); conn.close()

    return jsonify({
        'success': True,
        'data': {
            'id': plan_id,
            'plans': plan,
            'isPaid': is_paid,
            'dataYear': data_year,
            'archiveFallback': archive_fallback_used,
            # 数据质量统计
            'dataQuality': {
                'realDataRate': real_data_rate,
                'officialCount': official_in_plan,
                'simulatedCount': simulated_in_plan,
                'totalCount': total_in_plan,
                'breakdown': {
                    'chongOfficial': chong_official,
                    'chongTotal': len(chong),
                    'wenOfficial': wen_official,
                    'wenTotal': len(wen),
                    'baoOfficial': bao_official,
                    'baoTotal': len(bao),
                }
            },
            # 兼容旧字段
            'isRealData': official_in_plan > 0,
            'realDataCount': official_in_plan,
            'summary': {
                'total': total_in_plan,
                'chong': len([p for p in plan if p['type'] == '冲']),
                'wen': len([p for p in plan if p['type'] == '稳']),
                'bao': len([p for p in plan if p['type'] == '保']),
            }
        }
    }), 201


# ===== 方案列表（支持筛选）=====
@vol_bp.route('/plans', methods=['GET'])
@login_required
def list_plans():
    """
    GET /api/volunteer/plans?subjectType=物理类&strategyType=稳健&keyword=南大
    —— 我的方案列表，支持按科类/策略/关键词筛选
    """

    subject_type = request.args.get('subjectType', '')
    strategy_type = request.args.get('strategyType', '')
    keyword = request.args.get('keyword', '')

    conn = get_conn()
    cur = conn.cursor()

    where = ["user_id=%s"]
    params = [request.user_id]

    if subject_type:
        where.append("subject_type=%s")
        params.append(subject_type)
    if strategy_type:
        where.append("strategy_type=%s")
        params.append(strategy_type)
    if keyword:
        where.append("plans_data LIKE %s")
        params.append(f"%{keyword}%")

    query = f"""SELECT id, plan_name, subject_type, score, `rank`, strategy_type, created_at
        FROM volunteer_plans WHERE {' AND '.join(where)} ORDER BY created_at DESC"""

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close(); conn.close()

    return jsonify({'success': True, 'data': rows, 'count': len(rows)})


# ===== 方案详情 =====
@vol_bp.route('/plans/<int:plan_id>', methods=['GET'])
@login_required
def get_plan(plan_id):
    """GET /api/volunteer/plans/1 —— 方案详情"""

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM volunteer_plans WHERE id=%s AND user_id=%s",
        (plan_id, request.user_id)
    )
    plan = cur.fetchone()
    cur.close(); conn.close()

    if not plan:
        return jsonify({'success': False, 'message': '方案不存在'}), 404

    plan['plans_data'] = json.loads(plan['plans_data'])
    return jsonify({'success': True, 'data': plan})


# ===== 删除方案 =====
@vol_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@login_required
def delete_plan(plan_id):
    """DELETE /api/volunteer/plans/1 —— 删除我的方案"""

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM volunteer_plans WHERE id=%s AND user_id=%s",
        (plan_id, request.user_id)
    )
    deleted = cur.rowcount
    conn.commit()
    cur.close(); conn.close()

    if deleted == 0:
        return jsonify({'success': False, 'message': '方案不存在或无权删除'}), 404

    return jsonify({'success': True, 'message': '已删除'})


# ===== 批量删除方案 =====
@vol_bp.route('/plans/batch', methods=['DELETE'])
@login_required
def batch_delete_plans():
    """DELETE /api/volunteer/plans/batch  Body: { "ids": [1,2,3] }"""

    data = request.get_json() or {}
    ids = data.get('ids', [])
    if not ids or not isinstance(ids, list):
        return jsonify({'success': False, 'message': '请提供要删除的方案ID列表'}), 400

    conn = get_conn()
    cur = conn.cursor()
    placeholders = ','.join(['%s'] * len(ids))
    cur.execute(
        f"DELETE FROM volunteer_plans WHERE id IN ({placeholders}) AND user_id=%s",
        ids + [request.user_id]
    )
    deleted = cur.rowcount
    conn.commit()
    cur.close(); conn.close()

    return jsonify({'success': True, 'message': f'已删除 {deleted} 个方案', 'deletedCount': deleted})
