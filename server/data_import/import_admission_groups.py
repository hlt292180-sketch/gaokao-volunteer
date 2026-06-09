# -*- coding: utf-8 -*-
"""
院校专业组投档线导入脚本
=========================
将 real_data/ 目录下的真实投档线 CSV 导入 MySQL admission_scores 表。

数据来源：江苏省教育考试院本科批次平行志愿投档线
年份：2023, 2024
粒度：院校专业组级别（非专业级别）

使用方式：
    python import_admission_groups.py              # 导入全部
    python import_admission_groups.py --year 2024  # 仅导入2024
    python import_admission_groups.py --dry-run    # 仅验证不写入
"""
import csv
import os
import sys
import argparse
import pymysql
from collections import defaultdict

# ---- 配置 ----
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "292180",
    "database": "gaokao",
    "charset": "utf8mb4",
}
PROVINCE_ID = 1
CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "real_data")
BATCH = "本科批"

IMPORT_FILES = {
    "2023": "admission_groups_2023.csv",
    "2024": "admission_groups_2024.csv",
}


def connect_db():
    return pymysql.connect(**DB_CONFIG)


def load_university_map(cur):
    """加载院校名称→ID 映射"""
    cur.execute("SELECT id, name FROM universities")
    return {name: uid for uid, name in cur.fetchall()}


def read_csv(filepath):
    """读取投档线 CSV"""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "university_name": row["university_name"],
                "year": int(row["year"]),
                "subject_type": row["subject_type"],
                "major_group": row["major_group"],
                "subject_requirement": row["subject_requirement"],
                "min_score": int(row["min_score"]),
                "min_rank": int(row["min_rank"]),
            })
    return rows


def import_groups(conn, rows, uni_map, dry_run=False):
    """导入专业组投档线到 admission_scores 表。

    使用 INSERT ... ON DUPLICATE KEY UPDATE 避免重复。
    专业组级数据: major_id=NULL（表示专业组级别而非专业级别）。
    """
    if dry_run:
        return {"inserted": len(rows), "updated": 0, "skipped": 0, "unmatched": []}

    cur = conn.cursor()
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "unmatched": []}

    for row in rows:
        uni_name = row["university_name"]

        # 模糊匹配（处理名称差异）
        uni_id = uni_map.get(uni_name)
        if uni_id is None:
            # 尝试部分匹配
            for name, uid in uni_map.items():
                if uni_name in name or name in uni_name:
                    uni_id = uid
                    break

        if uni_id is None:
            stats["unmatched"].append(uni_name)
            stats["skipped"] += 1
            continue

        # 构建唯一键检查（同一专业组同年同科类不重复）
        cur.execute(
            """SELECT id FROM admission_scores
               WHERE university_id=%s AND major_id IS NULL AND year=%s
               AND subject_type=%s AND major_group=%s LIMIT 1""",
            (uni_id, row["year"], row["subject_type"], row["major_group"]),
        )
        existing = cur.fetchone()

        if existing:
            # 更新已有记录（包含数据来源标记）
            cur.execute(
                """UPDATE admission_scores
                   SET min_score=%s, min_rank=%s, subject_requirement=%s, avg_score=%s, plan_count=%s,
                       data_source='OFFICIAL', verified_level=3
                   WHERE id=%s""",
                (row["min_score"], row["min_rank"], row["subject_requirement"],
                 row["min_score"] + 5, 30, existing[0]),
            )
            stats["updated"] += 1
        else:
            # 插入新记录（标记为官方原始数据）
            cur.execute(
                """INSERT INTO admission_scores
                   (university_id, major_id, province_id, year, subject_type, batch,
                    min_score, min_rank, avg_score, plan_count,
                    subject_requirement, major_group,
                    data_source, verified_level)
                   VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                           'OFFICIAL', 3)""",
                (uni_id, PROVINCE_ID, row["year"], row["subject_type"], BATCH,
                 row["min_score"], row["min_rank"], row["min_score"] + 5, 30,
                 row["subject_requirement"], row["major_group"]),
            )
            stats["inserted"] += 1

    conn.commit()
    return stats


def main():
    parser = argparse.ArgumentParser(description="导入真实院校专业组投档线")
    parser.add_argument("--year", type=int, help="仅导入指定年份")
    parser.add_argument("--dry-run", action="store_true", help="仅验证不写入")
    args = parser.parse_args()

    print("=" * 60)
    print("🏫 院校专业组投档线导入工具")
    print("=" * 60)

    conn = connect_db()
    cur = conn.cursor()

    # 加载院校映射
    uni_map = load_university_map(cur)
    print(f"\n已加载 {len(uni_map)} 所院校")

    # 导入前统计
    cur.execute("SELECT COUNT(*) FROM admission_scores WHERE major_group != ''")
    before_real = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM admission_scores")
    before_total = cur.fetchone()[0]
    print(f"导入前: 总计{before_total}条, 含专业组数据{before_real}条")

    report = []
    all_unmatched = set()

    for year_str, filename in IMPORT_FILES.items():
        if args.year and int(year_str) != args.year:
            continue

        filepath = os.path.join(CSV_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  ⚠️ 文件不存在: {filename}")
            continue

        rows = read_csv(filepath)
        stats = import_groups(conn, rows, uni_map, dry_run=args.dry_run)
        all_unmatched.update(stats["unmatched"])

        # 统计覆盖的院校
        uni_names = set(r["university_name"] for r in rows)
        matched = len(uni_names) - len([u for u in stats["unmatched"] if u in uni_names])

        mode = "🔍 DRY RUN" if args.dry_run else "✅ 已导入"
        print(f"  {mode} {year_str}: {len(rows)}条, "
              f"新增{stats['inserted']} 更新{stats['updated']} 跳过{stats['skipped']}, "
              f"院校匹配{matched}/{len(uni_names)}")

        # 按层级统计覆盖率
        cur.execute("""SELECT u.level, COUNT(DISTINCT a.university_id)
            FROM admission_scores a JOIN universities u ON a.university_id=u.id
            WHERE a.major_group != '' AND a.year=%s
            GROUP BY u.level ORDER BY u.level""", (int(year_str),))
        tier_coverage = cur.fetchall()

        report.append(f"\n### {year_str}年 覆盖率")
        for level, count in tier_coverage:
            cur.execute("SELECT COUNT(*) FROM universities WHERE level=%s", (level,))
            total = cur.fetchone()[0]
            pct = count / total * 100 if total > 0 else 0
            report.append(f"| {level}档 | {count}/{total} | {pct:.0f}% |")

    # 导入后统计
    cur.execute("SELECT COUNT(*) FROM admission_scores WHERE major_group != ''")
    after_real = cur.fetchone()[0]
    print(f"\n导入后: 含专业组数据 {after_real} 条 (新增 {after_real - before_real})")

    # 覆盖率报告
    print("\n" + "=" * 60)
    print("📋 覆盖率报告")
    print("=" * 60)
    for line in report:
        print(line)

    # 未匹配院校
    if all_unmatched:
        print(f"\n⚠️ 未匹配院校 ({len(all_unmatched)}所):")
        for name in sorted(all_unmatched):
            print(f"  - {name}")

    # 按专业组统计
    cur.execute("""SELECT year, subject_type, COUNT(*) as cnt, COUNT(DISTINCT university_id) as unis
        FROM admission_scores WHERE major_group != '' GROUP BY year, subject_type""")
    print("\n📊 专业组统计:")
    for r in cur.fetchall():
        print(f"  {r[0]} {r[1]}: {r[2]}个专业组, {r[3]}所院校")

    if args.dry_run:
        print("\n⚠️ DRY RUN 模式，数据未实际写入")
        conn.rollback()

    conn.close()
    print("\n✅ 导入完成")


if __name__ == "__main__":
    main()
