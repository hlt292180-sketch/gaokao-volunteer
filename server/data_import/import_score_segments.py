# -*- coding: utf-8 -*-
"""
一分一段表导入脚本
=================
将 real_data/ 目录下的真实一分一段表 CSV 导入 MySQL score_segments 表。

数据来源：江苏省教育考试院官方逐分段统计表
年份：2023, 2024
科类：物理类、历史类

使用方式：
    python import_score_segments.py              # 导入全部
    python import_score_segments.py --year 2024  # 仅导入2024
    python import_score_segments.py --dry-run    # 仅验证不写入
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
PROVINCE_ID = 1  # 江苏省
CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "real_data")

# 待导入的文件列表
IMPORT_FILES = {
    ("2023", "物理类"): "score_segments_2023_physics.csv",
    ("2023", "历史类"): "score_segments_2023_history.csv",
    ("2024", "物理类"): "score_segments_2024_physics.csv",
    ("2024", "历史类"): "score_segments_2024_history.csv",
}


def connect_db():
    return pymysql.connect(**DB_CONFIG)


def read_csv(filepath):
    """读取 CSV 文件，返回 [(year, subject_type, score, rank), ...]"""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append((
                int(row["year"]),
                row["subject_type"],
                int(row["score"]),
                int(row["rank"]),
            ))
    return rows


def validate_segments(rows, label):
    """验证一分一段表数据质量，返回错误列表"""
    errors = []
    if not rows:
        errors.append("数据为空")
        return errors

    scores = [r[2] for r in rows]
    ranks = [r[3] for r in rows]
    score_min, score_max = min(scores), max(scores)

    # 1. 分数严格递减
    for i in range(len(scores) - 1):
        if scores[i] <= scores[i + 1]:
            errors.append(f"分数不递减: {scores[i]} -> {scores[i + 1]} (行{i})")

    # 2. 位次严格递增（分数越低 → 位次越大）
    for i in range(len(ranks) - 1):
        if ranks[i] >= ranks[i + 1]:
            errors.append(f"位次不递增: score={scores[i]} rank={ranks[i]} -> score={scores[i + 1]} rank={ranks[i + 1]}")

    # 3. 无重复分数
    if len(scores) != len(set(scores)):
        from collections import Counter
        dupes = [s for s, c in Counter(scores).items() if c > 1]
        errors.append(f"重复分数: {dupes}")

    # 4. 分数连续性检查（一分一段应有连续分数）
    if len(scores) > 50:
        gaps = []
        for i in range(len(scores) - 1):
            if scores[i] - scores[i + 1] > 1:
                gaps.append((scores[i + 1], scores[i]))
        if gaps:
            errors.append(f"分数断层: {len(gaps)}处, 示例{gaps[:3]}")

    return errors


def import_file(conn, rows, dry_run=False):
    """导入一分一段数据到 score_segments 表"""
    if dry_run:
        return len(rows), 0, 0

    cur = conn.cursor()
    inserted, updated, skipped = 0, 0, 0

    for year, subject_type, score, rank in rows:
        # UPSERT: 如果已存在则更新，否则插入
        cur.execute(
            """INSERT INTO score_segments (province_id, year, score, `rank`, subject_type)
               VALUES (%s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE `rank` = VALUES(`rank`)""",
            (PROVINCE_ID, year, score, rank, subject_type),
        )
        if cur.rowcount == 1:
            inserted += 1
        elif cur.rowcount == 2:
            updated += 1
        else:
            skipped += 1

    conn.commit()
    return inserted, updated, skipped


def main():
    parser = argparse.ArgumentParser(description="导入真实一分一段表")
    parser.add_argument("--year", type=int, help="仅导入指定年份")
    parser.add_argument("--dry-run", action="store_true", help="仅验证不写入数据库")
    args = parser.parse_args()

    print("=" * 60)
    print("📊 一分一段表导入工具")
    print("=" * 60)

    conn = connect_db()

    # 记录导入前状态
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM score_segments")
    before_count = cur.fetchone()[0]
    print(f"\n导入前 score_segments 记录数: {before_count}")

    total_inserted, total_updated = 0, 0
    report_lines = []

    for (year_str, subject_type), filename in IMPORT_FILES.items():
        if args.year and int(year_str) != args.year:
            continue

        filepath = os.path.join(CSV_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  ⚠️ 文件不存在: {filename}，跳过")
            report_lines.append(f"| {year_str} | {subject_type} | ⚠️ 文件缺失 | — | — | — |")
            continue

        rows = read_csv(filepath)

        # 验证
        errors = validate_segments(rows, f"{year_str} {subject_type}")
        completeness = "逐分完整" if len(rows) > 50 else f"部分({len(rows)}点)"

        scores = [r[2] for r in rows]
        score_range = f"{min(scores)}~{max(scores)}"

        if errors:
            print(f"\n  ❌ {year_str} {subject_type} 验证失败 ({len(errors)}个错误):")
            for e in errors:
                print(f"     - {e}")
            report_lines.append(
                f"| {year_str} | {subject_type} | ❌ 验证失败 | {len(rows)} | {score_range} | {len(errors)}个错误 |"
            )
            continue

        # 导入
        ins, upd, skip = import_file(conn, rows, dry_run=args.dry_run)
        total_inserted += ins
        total_updated += upd

        status = "✅ 已导入" if not args.dry_run else "🔍 仅验证"
        print(f"  {status} {year_str} {subject_type}: {len(rows)}行, {completeness}, "
              f"分数{score_range}, 新增{ins} 更新{upd}")
        report_lines.append(
            f"| {year_str} | {subject_type} | {status} | {len(rows)} | {score_range} | {completeness} |"
        )

    # 导入后统计
    cur.execute("SELECT COUNT(*) FROM score_segments")
    after_count = cur.fetchone()[0]

    print(f"\n导入后 score_segments 记录数: {after_count}")
    print(f"本次新增: {total_inserted}, 更新: {total_updated}")

    # 输出验证报告
    print("\n" + "=" * 60)
    print("📋 导入验证报告")
    print("=" * 60)
    print("| 年份 | 科类 | 状态 | 行数 | 分数范围 | 完整度 |")
    print("|------|------|------|------|----------|--------|")
    for line in report_lines:
        print(line)

    # 最终数据质量检查
    print("\n🔍 最终数据质量检查:")
    cur.execute("SELECT DISTINCT subject_type FROM score_segments")
    subjects = [r[0] for r in cur.fetchall()]
    print(f"  科类覆盖: {subjects}")

    cur.execute("SELECT DISTINCT year FROM score_segments ORDER BY year")
    years = [r[0] for r in cur.fetchall()]
    print(f"  年份覆盖: {years}")

    # 检查位次单调性（全局）
    for subject_type in subjects:
        for year in years:
            cur.execute(
                "SELECT score, `rank` FROM score_segments WHERE year=%s AND subject_type=%s ORDER BY score DESC",
                (year, subject_type),
            )
            data = cur.fetchall()
            if len(data) < 2:
                continue
            errors = 0
            for i in range(len(data) - 1):
                if data[i][1] >= data[i + 1][1]:
                    errors += 1
            status = "✅" if errors == 0 else f"❌ {errors}处错误"
            print(f"  {year} {subject_type}: {len(data)}行 位次单调性 {status}")

    if args.dry_run:
        print("\n⚠️ DRY RUN 模式，数据未实际写入数据库")
        conn.rollback()
    else:
        conn.commit()

    conn.close()
    print("\n✅ 导入完成")


if __name__ == "__main__":
    main()
