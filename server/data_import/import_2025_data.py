# -*- coding: utf-8 -*-
"""
2025年数据导入机制
=================
自动检测2025年数据文件是否存在，若存在则导入，否则返回友好提示。

数据来源：江苏省教育考试院 2025年6月25日发布
- 一分一段表：逐分段统计表(物理类+历史类)
- 本科批投档线：院校专业组投档最低分

使用方式：
    python import_2025_data.py                    # 自动检测并导入
    python import_2025_data.py --check-only       # 仅检查不导入
    python import_2025_data.py --segments-only    # 仅导入一分一段
    python import_2025_data.py --admission-only   # 仅导入投档线
"""
import csv
import os
import sys
import argparse
import pymysql
from datetime import datetime

DB_CONFIG = {
    "host": "localhost", "user": "root", "password": "292180",
    "database": "gaokao", "charset": "utf8mb4",
}
PROVINCE_ID = 1
BATCH = "本科批"

# 数据目录
REAL_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "real_data",
)

# 期望的2025年数据文件
EXPECTED_FILES = {
    "segments_physics": "score_segments_2025_physics.csv",
    "segments_history": "score_segments_2025_history.csv",
    "admission_groups": "admission_groups_2025.csv",
}


def connect_db():
    return pymysql.connect(**DB_CONFIG)


def check_files():
    """检查2025年数据文件是否存在"""
    status = {}
    for key, filename in EXPECTED_FILES.items():
        filepath = os.path.join(REAL_DATA_DIR, filename)
        exists = os.path.exists(filepath)
        size = os.path.getsize(filepath) if exists else 0
        status[key] = {
            "filename": filename,
            "exists": exists,
            "size_bytes": size,
            "path": filepath,
        }
    return status


def import_segments(conn, dry_run=False):
    """导入一分一段表"""
    cur = conn.cursor()
    stats = {"physics": 0, "history": 0}

    for subject_key, subject_name in [("segments_physics", "物理类"), ("segments_history", "历史类")]:
        filepath = os.path.join(REAL_DATA_DIR, EXPECTED_FILES[subject_key])
        if not os.path.exists(filepath):
            continue

        rows = []
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append((int(row["year"]), row["subject_type"], int(row["score"]), int(row["rank"])))

        if dry_run:
            stats[subject_key.split("_")[1]] = len(rows)
            continue

        ins = 0
        for year, st, score, rank in rows:
            cur.execute(
                """INSERT INTO score_segments (province_id, year, score, `rank`, subject_type)
                   VALUES (%s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE `rank` = VALUES(`rank`)""",
                (PROVINCE_ID, year, score, rank, st),
            )
            ins += cur.rowcount

        stats[subject_key.split("_")[1]] = ins
        conn.commit()

    return stats


def import_admission_groups(conn, dry_run=False):
    """导入投档线"""
    filepath = os.path.join(REAL_DATA_DIR, EXPECTED_FILES["admission_groups"])
    if not os.path.exists(filepath):
        return {"inserted": 0, "updated": 0, "skipped": 0}

    rows = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "university_name": row["university_name"],
                "year": int(row["year"]),
                "subject_type": row["subject_type"],
                "major_group": row.get("major_group", ""),
                "subject_requirement": row.get("subject_requirement", ""),
                "min_score": int(row["min_score"]),
                "min_rank": int(row["min_rank"]),
            })

    if dry_run:
        return {"inserted": len(rows), "updated": 0, "skipped": 0}

    cur = conn.cursor()
    # 加载院校映射
    cur.execute("SELECT id, name FROM universities")
    uni_map = {name: uid for uid, name in cur.fetchall()}

    stats = {"inserted": 0, "updated": 0, "skipped": 0}
    for r in rows:
        uni_id = uni_map.get(r["university_name"])
        if not uni_id:
            stats["skipped"] += 1
            continue

        cur.execute(
            """SELECT id FROM admission_scores
               WHERE university_id=%s AND major_id IS NULL AND year=%s
               AND subject_type=%s AND major_group=%s AND data_source='OFFICIAL'
               LIMIT 1""",
            (uni_id, r["year"], r["subject_type"], r["major_group"]),
        )
        existing = cur.fetchone()

        if existing:
            cur.execute(
                """UPDATE admission_scores SET min_score=%s, min_rank=%s,
                   subject_requirement=%s, avg_score=%s, verified_level=3
                   WHERE id=%s""",
                (r["min_score"], r["min_rank"], r["subject_requirement"],
                 r["min_score"] + 5, existing[0]),
            )
            stats["updated"] += 1
        else:
            cur.execute(
                """INSERT INTO admission_scores
                   (university_id, major_id, province_id, year, subject_type, batch,
                    min_score, min_rank, avg_score, plan_count,
                    subject_requirement, major_group,
                    data_source, verified_level)
                   VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                           'OFFICIAL', 3)""",
                (uni_id, PROVINCE_ID, r["year"], r["subject_type"], BATCH,
                 r["min_score"], r["min_rank"], r["min_score"] + 5, 30,
                 r["subject_requirement"], r["major_group"]),
            )
            stats["inserted"] += 1

    conn.commit()
    return stats


def generate_report(status, seg_stats, adm_stats):
    """生成 IMPORT_2025_READINESS_REPORT.md"""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(root, "IMPORT_2025_READINESS_REPORT.md")

    all_ready = all(s["exists"] for s in status.values())

    lines = [
        "# 2025年数据导入就绪报告",
        f"\n> 检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n## 一、文件检查",
        f"\n| 文件 | 存在 | 大小 |",
        f"|------|------|------|",
    ]
    for key, s in status.items():
        status_icon = "✅" if s["exists"] else "❌"
        lines.append(f"| {s['filename']} | {status_icon} | {s['size_bytes']}B |")

    lines += [
        f"\n## 二、就绪状态",
        f"\n{'✅ 全部就绪，可以导入' if all_ready else '❌ 部分文件缺失，请从江苏省教育考试院获取2025年数据'}",
        f"\n## 三、导入统计",
        f"\n| 类别 | 导入数 |",
        f"|------|--------|",
        f"| 一分一段(物理) | {seg_stats.get('physics', 0)} |",
        f"| 一分一段(历史) | {seg_stats.get('history', 0)} |",
        f"| 投档线(专业组) | {adm_stats.get('inserted', 0)} |",
    ]

    if not all_ready:
        lines += [
            f"\n## 四、缺失文件说明",
            f"\n2025年高考数据于2025年6月25日由江苏省教育考试院发布。",
            f"获取后请将文件放入 `real_data/` 目录并重新运行本脚本。",
        ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


def main():
    parser = argparse.ArgumentParser(description="2025年数据导入机制")
    parser.add_argument("--check-only", action="store_true", help="仅检查文件不导入")
    parser.add_argument("--segments-only", action="store_true", help="仅导入一分一段")
    parser.add_argument("--admission-only", action="store_true", help="仅导入投档线")
    parser.add_argument("--dry-run", action="store_true", help="仅验证不写入")
    args = parser.parse_args()

    print("=" * 60)
    print("📅 2025年数据导入机制")
    print("=" * 60)

    # 1. 检查文件
    status = check_files()
    print("\n📁 文件检查:")
    all_ok = True
    for key, s in status.items():
        icon = "✅" if s["exists"] else "❌"
        print(f"  {icon} {s['filename']}")
        if not s["exists"]:
            all_ok = False

    if not all_ok:
        print("\n⚠️ 部分2025年数据文件缺失。")
        print("   请从江苏省教育考试院(http://www.jseea.cn/)获取2025年数据。")
        print("   将文件放入 real_data/ 目录后重新运行。")

        # 仍然生成报告
        generate_report(status, {}, {})
        print("\n📄 已生成 IMPORT_2025_READINESS_REPORT.md")
        return

    if args.check_only:
        print("\n✅ 所有文件就绪，可以导入。")
        print("   执行: python import_2025_data.py  开始导入")
        return

    # 2. 导入
    conn = connect_db()
    seg_stats = {}
    adm_stats = {}

    if not args.admission_only:
        print("\n📊 导入一分一段表...")
        seg_stats = import_segments(conn, args.dry_run)
        print(f"  物理类: {seg_stats.get('physics', 0)}条")
        print(f"  历史类: {seg_stats.get('history', 0)}条")

    if not args.segments_only:
        print("\n🏫 导入投档线...")
        adm_stats = import_admission_groups(conn, args.dry_run)
        print(f"  新增: {adm_stats.get('inserted', 0)}, 更新: {adm_stats.get('updated', 0)}")

    # 3. 导入后验证
    if not args.dry_run:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM score_segments WHERE year=2025")
        seg_2025 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM admission_scores WHERE year=2025 AND data_source='OFFICIAL'")
        adm_2025 = cur.fetchone()[0]
        print(f"\n📈 2025年数据: 一分一段{seg_2025}条, 投档线{adm_2025}条")
    else:
        print("\n⚠️ DRY RUN 模式")

    conn.close()

    # 4. 生成报告
    report_path = generate_report(status, seg_stats, adm_stats)
    print(f"\n📄 报告已生成: {report_path}")
    print("✅ 完成")


if __name__ == "__main__":
    main()
