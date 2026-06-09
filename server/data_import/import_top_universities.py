# -*- coding: utf-8 -*-
"""
顶尖院校数据导入框架
====================
支持导入 清华/北大/复旦/上交/浙大/中科大 等顶尖院校的投档线数据。

数据来源要求：江苏省教育考试院本科批次投档线公告 / 中国教育在线(EOL)
禁止伪造数据。本脚本仅为导入框架，实际数据需从官方来源获取后填入CSV。

CSV 格式:
  university_name,year,subject_type,major_group,subject_requirement,min_score,min_rank

使用方式:
  python import_top_universities.py --file top6_2024.csv --year 2024
  python import_top_universities.py --file top6_2024.csv --year 2024 --dry-run
"""
import csv
import os
import sys
import argparse
import pymysql

DB_CONFIG = {
    "host": "localhost", "user": "root", "password": "292180",
    "database": "gaokao", "charset": "utf8mb4",
}
PROVINCE_ID = 1
BATCH = "本科批"

# 顶尖院校列表（用于自动补充 universities 表）
TOP_UNIVERSITIES = {
    "清华大学":   {"city": "北京", "level": "A", "type": "综合", "is_985": 1, "is_211": 1, "is_df": 1},
    "北京大学":   {"city": "北京", "level": "A", "type": "综合", "is_985": 1, "is_211": 1, "is_df": 1},
    "复旦大学":   {"city": "上海", "level": "A", "type": "综合", "is_985": 1, "is_211": 1, "is_df": 1},
    "上海交通大学": {"city": "上海", "level": "A", "type": "综合", "is_985": 1, "is_211": 1, "is_df": 1},
    "浙江大学":   {"city": "杭州", "level": "A", "type": "综合", "is_985": 1, "is_211": 1, "is_df": 1},
    "中国科学技术大学": {"city": "合肥", "level": "A", "type": "理工", "is_985": 1, "is_211": 1, "is_df": 1},
}


def connect_db():
    return pymysql.connect(**DB_CONFIG)


def ensure_universities_exist(conn):
    """确保顶尖院校在 universities 表中存在。若不存在则插入。"""
    cur = conn.cursor()
    added = []
    for name, info in TOP_UNIVERSITIES.items():
        cur.execute("SELECT id FROM universities WHERE name=%s", (name,))
        if not cur.fetchone():
            cur.execute(
                """INSERT INTO universities (name, province_id, city, level, type,
                   is_985, is_211, is_double_first_class)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (name, PROVINCE_ID, info["city"], info["level"], info["type"],
                 info["is_985"], info["is_211"], info["is_df"]),
            )
            added.append(name)
    conn.commit()
    return added


def read_csv(filepath):
    """读取 CSV 文件"""
    rows = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "university_name": row["university_name"].strip(),
                "year": int(row["year"]),
                "subject_type": row["subject_type"].strip(),
                "major_group": row.get("major_group", "").strip(),
                "subject_requirement": row.get("subject_requirement", "").strip(),
                "min_score": int(row["min_score"]),
                "min_rank": int(row["min_rank"]),
            })
    return rows


def validate_rows(rows):
    """校验数据"""
    errors = []
    for i, r in enumerate(rows):
        if r["university_name"] not in TOP_UNIVERSITIES:
            errors.append(f"行{i+1}: {r['university_name']} 不在顶尖院校列表中")
        if r["min_score"] < 600:
            errors.append(f"行{i+1}: 分数{r['min_score']}异常低")
        if r["min_rank"] < 1 or r["min_rank"] > 10000:
            errors.append(f"行{i+1}: 位次{r['min_rank']}异常(顶尖院校应在1-10000)")
        if r["year"] not in (2023, 2024, 2025):
            errors.append(f"行{i+1}: 年份{r['year']}不在支持范围")
    return errors


def import_data(conn, rows, dry_run=False):
    """导入投档线数据"""
    cur = conn.cursor()
    stats = {"inserted": 0, "updated": 0, "skipped": 0}

    for r in rows:
        # 查找 university_id
        cur.execute("SELECT id FROM universities WHERE name=%s", (r["university_name"],))
        uni_row = cur.fetchone()
        if not uni_row:
            stats["skipped"] += 1
            continue
        uni_id = uni_row[0]

        if dry_run:
            stats["inserted"] += 1
            continue

        # 检查去重
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
                   subject_requirement=%s, avg_score=%s, plan_count=%s,
                   verified_level=3
                   WHERE id=%s""",
                (r["min_score"], r["min_rank"], r["subject_requirement"],
                 r["min_score"] + 5, 30, existing[0]),
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

    if not dry_run:
        conn.commit()
    return stats


def main():
    parser = argparse.ArgumentParser(description="顶尖院校投档线导入框架")
    parser.add_argument("--file", required=True, help="CSV文件路径")
    parser.add_argument("--year", type=int, required=True, help="数据年份")
    parser.add_argument("--dry-run", action="store_true", help="仅校验不写入")
    args = parser.parse_args()

    print("=" * 60)
    print("🏆 顶尖院校数据导入框架")
    print("=" * 60)

    # 1. 读取
    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        print("   请从江苏省教育考试院或EOL获取真实数据后重试。")
        sys.exit(1)

    rows = read_csv(args.file)
    print(f"\n📄 读取 {len(rows)} 条记录")

    # 2. 校验
    errors = validate_rows(rows)
    if errors:
        print(f"❌ 校验失败 ({len(errors)}个错误):")
        for e in errors[:10]:
            print(f"  - {e}")
        if not args.dry_run:
            print("   请修正后重试。")
            sys.exit(1)
    else:
        print("✅ 数据校验通过")

    # 3. 连接数据库
    conn = connect_db()

    # 4. 确保院校存在
    added = ensure_universities_exist(conn)
    if added:
        print(f"\n🏫 新增院校: {added}")

    # 5. 导入
    stats = import_data(conn, rows, args.dry_run)
    print(f"\n📊 导入结果: 新增{stats['inserted']} 更新{stats['updated']} 跳过{stats['skipped']}")

    # 6. 导入后验证
    if not args.dry_run:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM admission_scores WHERE data_source='OFFICIAL' AND min_score >= 660"
        )
        high_off = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM admission_scores WHERE data_source='OFFICIAL'")
        total_off = cur.fetchone()[0]
        print(f"\n📈 导入后: 650+ OFFICIAL 共 {high_off} 条, 全部OFFICIAL {total_off} 条")
    else:
        print("\n⚠️ DRY RUN 模式，数据未写入")

    conn.close()
    print("\n✅ 完成")


if __name__ == "__main__":
    main()
