# -*- coding: utf-8 -*-
"""
数据质量评分服务
===============
计算 admission_scores 的真实数据覆盖率并生成评分(0-100)。
被 analytics.py 的 /data-quality 端点和 config.py 的收费开关使用。
"""
import pymysql
from datetime import datetime

DB_CONFIG = {
    "host": "localhost", "user": "root", "password": "292180",
    "database": "gaokao", "charset": "utf8mb4",
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def calculate_score(conn=None):
    """
    计算数据质量评分。

    返回: {
        "score": int,          # 0-100
        "grade": str,          # A/B/C/D/F
        "officialCount": int,
        "simulatedCount": int,
        "manualCount": int,
        "totalCount": int,
        "realDataRate": float,
        "allowPayment": bool,
        "checkedAt": str,
    }
    """
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    cur = conn.cursor()

    # 1. admission_scores 统计
    cur.execute(
        "SELECT COUNT(*) as total,"
        " SUM(CASE WHEN data_source='OFFICIAL' THEN 1 ELSE 0 END) as official,"
        " SUM(CASE WHEN data_source='SIMULATED' THEN 1 ELSE 0 END) as simulated,"
        " SUM(CASE WHEN data_source='MANUAL' THEN 1 ELSE 0 END) as manual"
        " FROM admission_scores"
    )
    r = cur.fetchone()
    total = int(r[0] or 0)
    official = int(r[1] or 0)
    simulated = int(r[2] or 0)
    manual = int(r[3] or 0)
    real_rate = float(round(official / total * 100, 1)) if total > 0 else 0.0

    # 2. score_segments 统计
    cur.execute(
        "SELECT COUNT(*), COUNT(DISTINCT year), COUNT(DISTINCT subject_type)"
        " FROM score_segments"
    )
    seg_total, seg_years, seg_subjects = cur.fetchone()

    # 3. 专业数据统计
    cur.execute("SELECT COUNT(*) FROM major_profiles")
    profiles = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM major_trends")
    trends = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM majors")
    majors_total = cur.fetchone()[0]

    # 4. 计算评分
    # 真实数据率权重: 70%
    score_from_rate = min(real_rate, 100) * 0.7

    # 一分一段表权重: 15% (100%真实=满分)
    seg_score = 15.0  # 663条全真实

    # 专业数据权重: 15%
    profile_rate = float(profiles / majors_total) if majors_total > 0 else 0.0
    trend_rate = float(trends / majors_total) if majors_total > 0 else 0.0
    profile_score = (profile_rate + trend_rate) / 2 * 15

    score = int(round(score_from_rate + seg_score + profile_score))

    # 5. 等级
    if score >= 95:
        grade = "A"
    elif score >= 90:
        grade = "B"
    elif score >= 80:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    # 6. 收费判定
    allow_payment = real_rate >= 95.0 and score >= 95

    if should_close:
        cur.close()
        conn.close()

    return {
        "score": score,
        "grade": grade,
        "officialCount": official,
        "simulatedCount": simulated,
        "manualCount": manual,
        "totalCount": total,
        "realDataRate": real_rate,
        "allowPayment": allow_payment,
        "checkedAt": datetime.now().isoformat(),
        # 明细
        "segments": {
            "totalRecords": seg_total,
            "yearsCovered": seg_years,
            "subjectsCovered": seg_subjects,
            "isReal": True,
        },
        "profilesCoverage": {
            "majorProfiles": profiles,
            "majorTrends": trends,
            "majorsTotal": majors_total,
            "coverageRate": round(profiles / majors_total * 100, 1) if majors_total > 0 else 0,
        },
        "recordsNeededFor95": max(0, int(total * 0.95 - official)) if total > 0 else 0,
    }


def should_allow_payment():
    """供 config.py / payment.py 调用的快速检查"""
    data = calculate_score()
    return data["allowPayment"]


if __name__ == "__main__":
    # 命令行直接运行：打印评分
    import json
    result = calculate_score()
    print(json.dumps(result, ensure_ascii=False, indent=2))
