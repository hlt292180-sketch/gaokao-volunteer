# -*- coding: utf-8 -*-
"""
业务覆盖率服务（替代旧的记录级 realDataRate）
==========================================
衡量的是"业务覆盖率"而非"记录覆盖率"。

指标：
  universityCoverage  — 已覆盖院校 / 目标院校
  groupCoverage       — 已覆盖专业组数 / 目标专业组数
  yearCoverage        — 已覆盖年份 / 目标年份
  highScoreCoverage   — 650+顶尖院校覆盖率
  scoreSegmentCoverage— 一分一段表真实度

商业化评分规则：
  数据真实性: 40分（一分一段 + 专业组来源）
  院校覆盖:   20分
  专业组覆盖: 15分
  年份覆盖:   10分
  高分段覆盖: 15分
  总分: 100分

等级: A(≥90) B(≥80) C(≥70) D(≥60) F(<60)
收费门槛: commercialScore ≥ 85
"""
import pymysql
from datetime import datetime

DB_CONFIG = {
    "host": "localhost", "user": "root", "password": "292180",
    "database": "gaokao", "charset": "utf8mb4",
}

# ---- 目标常量 ----
TARGET_UNIVERSITIES = 55        # 当前系统内 55 所江苏院校
TARGET_GROUPS = 55 * 3          # 每校平均 3 个专业组 = 165
TARGET_YEARS = {2023, 2024, 2025}
TARGET_HIGH_SCORE_SCHOOLS = {   # 650+ 必须覆盖的顶尖院校
    "清华大学", "北京大学", "复旦大学", "上海交通大学",
    "浙江大学", "中国科学技术大学", "南京大学", "东南大学",
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def calculate_coverage(conn=None):
    """
    计算业务覆盖率评分。返回完整字典。
    """
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    cur = conn.cursor()

    # ==========================================
    # 1. 院校覆盖率
    # ==========================================
    cur.execute(
        "SELECT COUNT(DISTINCT university_id) FROM admission_scores"
        " WHERE data_source='OFFICIAL'"
    )
    covered_unis = int(cur.fetchone()[0] or 0)
    uni_coverage = round(covered_unis / TARGET_UNIVERSITIES * 100, 1)

    # 按层级细分
    cur.execute("""SELECT u.level, COUNT(DISTINCT u.id) as total,
        COUNT(DISTINCT CASE WHEN a.data_source='OFFICIAL' THEN u.id END) as covered
        FROM universities u LEFT JOIN admission_scores a ON u.id=a.university_id
        GROUP BY u.level ORDER BY u.level""")
    tier_detail = {}
    for r in cur.fetchall():
        tier_detail[r[0]] = {
            "total": int(r[1]), "covered": int(r[2]),
            "rate": round(r[2] / r[1] * 100, 1) if r[1] > 0 else 0,
        }

    # ==========================================
    # 2. 专业组覆盖率
    # ==========================================
    cur.execute(
        "SELECT COUNT(DISTINCT CONCAT(university_id, '-', major_group))"
        " FROM admission_scores WHERE data_source='OFFICIAL' AND major_group != ''"
    )
    covered_groups = int(cur.fetchone()[0] or 0)
    group_coverage = round(covered_groups / TARGET_GROUPS * 100, 1)

    # 按科目
    cur.execute("""SELECT subject_type,
        COUNT(DISTINCT CONCAT(university_id, '-', major_group)) as cnt
        FROM admission_scores WHERE data_source='OFFICIAL' AND major_group != ''
        GROUP BY subject_type""")
    group_by_subject = {r[0]: int(r[1]) for r in cur.fetchall()}

    # ==========================================
    # 3. 年份覆盖率
    # ==========================================
    cur.execute(
        "SELECT DISTINCT year FROM admission_scores WHERE data_source='OFFICIAL'"
    )
    covered_years = {int(r[0]) for r in cur.fetchall()}
    year_coverage = round(len(covered_years) / len(TARGET_YEARS) * 100, 1)
    missing_years = list(TARGET_YEARS - covered_years)

    # ==========================================
    # 4. 高分段覆盖率 (650+, 2024物理)
    # ==========================================
    cur.execute(
        "SELECT DISTINCT u.name FROM admission_scores a"
        " JOIN universities u ON a.university_id=u.id"
        " WHERE a.data_source='OFFICIAL' AND a.year=2024"
        " AND a.subject_type='物理类' AND a.min_score >= 650"
    )
    covered_high = {r[0] for r in cur.fetchall()}

    # 检查目标院校
    high_detail = {}
    for school in TARGET_HIGH_SCORE_SCHOOLS:
        cur.execute("SELECT COUNT(*) FROM universities WHERE name LIKE %s", (f"%{school}%",))
        exists = cur.fetchone()[0] > 0
        has_data = school in covered_high
        high_detail[school] = {
            "existsInDB": exists,
            "hasOfficialData": has_data,
        }
    high_covered = sum(1 for s in high_detail.values() if s["hasOfficialData"])
    high_total = len(TARGET_HIGH_SCORE_SCHOOLS)
    high_coverage = round(high_covered / high_total * 100, 1)

    # ==========================================
    # 5. 一分一段表真实度
    # ==========================================
    cur.execute("SELECT COUNT(*) FROM score_segments")
    seg_total = int(cur.fetchone()[0])
    seg_real = 100.0 if seg_total >= 200 else float(seg_total / 200 * 100)

    # 科类覆盖
    cur.execute("SELECT COUNT(DISTINCT subject_type) FROM score_segments")
    seg_subjects = int(cur.fetchone()[0])

    # ==========================================
    # 6. 数据来源信任度
    # ==========================================
    cur.execute(
        "SELECT COUNT(*) FROM admission_scores WHERE data_source='OFFICIAL' AND verified_level >= 3"
    )
    official_verified = int(cur.fetchone()[0])
    data_trust = 100.0 if official_verified > 0 else 0.0

    if should_close:
        cur.close()
        conn.close()

    # ==========================================
    # 商业化评分 (100分制)
    # ==========================================
    # 数据真实性 (40分): 一分一段20 + 专业组来源20
    data_score = (seg_real / 100 * 20) + 20  # 有OFFICIAL数据至少给满来源分

    # 院校覆盖 (20分)
    uni_score = uni_coverage / 100 * 20

    # 专业组覆盖 (15分)
    group_score = group_coverage / 100 * 15

    # 年份覆盖 (10分)
    year_score = year_coverage / 100 * 10

    # 高分段覆盖 (15分): 按 TOP8 院校覆盖比例
    high_score = high_coverage / 100 * 15

    commercial_score = int(round(data_score + uni_score + group_score + year_score + high_score))

    # 等级
    if commercial_score >= 90:
        grade = "A"
    elif commercial_score >= 80:
        grade = "B"
    elif commercial_score >= 70:
        grade = "C"
    elif commercial_score >= 60:
        grade = "D"
    else:
        grade = "F"

    # 收费判定
    allow_payment = commercial_score >= 85

    return {
        # 评分
        "commercialScore": commercial_score,
        "grade": grade,
        "allowPayment": allow_payment,
        "scoreBreakdown": {
            "dataAuthenticity": round(data_score, 1),
            "universityCoverage": round(uni_score, 1),
            "groupCoverage": round(group_score, 1),
            "yearCoverage": round(year_score, 1),
            "highScoreCoverage": round(high_score, 1),
        },
        # 院校
        "universityCoverage": uni_coverage,
        "coveredUniversities": covered_unis,
        "totalUniversities": TARGET_UNIVERSITIES,
        "tierDetail": tier_detail,
        # 专业组
        "groupCoverage": group_coverage,
        "coveredGroups": covered_groups,
        "targetGroups": TARGET_GROUPS,
        "groupsBySubject": group_by_subject,
        # 年份
        "yearCoverage": year_coverage,
        "coveredYears": sorted(list(covered_years)),
        "targetYears": sorted(list(TARGET_YEARS)),
        "missingYears": missing_years,
        # 高分段
        "highScoreCoverage": high_coverage,
        "highScoreDetail": high_detail,
        "coveredHighScoreSchools": high_covered,
        "targetHighScoreSchools": high_total,
        # 一分一段
        "scoreSegmentCoverage": seg_real,
        "scoreSegmentRecords": seg_total,
        "scoreSegmentSubjects": seg_subjects,
        # 元数据
        "checkedAt": datetime.now().isoformat(),
    }


def should_allow_payment():
    """供 config.py 快速调用的收费判定"""
    data = calculate_coverage()
    return data["allowPayment"]


if __name__ == "__main__":
    import json
    result = calculate_coverage()
    print(json.dumps(result, ensure_ascii=False, indent=2))
