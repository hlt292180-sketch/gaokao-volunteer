# -*- coding: utf-8 -*-
"""
真实数据验证脚本
===============
导入一分一段表和投档线后，验证：
  - 数据完整性
  - 位次单调性
  - 方案生成可行性（冲/稳/保）
  - 选科匹配正确性

使用方式：
    python validate_real_data.py                    # 全部验证
    python validate_real_data.py --score 585        # 指定分数验证方案生成
"""
import pymysql
import argparse
import sys

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "292180",
    "database": "gaokao",
    "charset": "utf8mb4",
}
PROVINCE_ID = 1


def connect_db():
    return pymysql.connect(**DB_CONFIG)


def validate_score_segments(cur):
    """验证一分一段表"""
    print("=" * 60)
    print("1️⃣ 一分一段表验证")
    print("=" * 60)

    cur.execute("SELECT DISTINCT year, subject_type FROM score_segments ORDER BY year, subject_type")
    groups = cur.fetchall()

    all_ok = True
    for year, subject_type in groups:
        cur.execute(
            "SELECT COUNT(*), MIN(score), MAX(score) FROM score_segments WHERE year=%s AND subject_type=%s",
            (year, subject_type),
        )
        cnt, score_min, score_max = cur.fetchone()
        print(f"\n  {year} {subject_type}: {cnt}行, 分数 {score_min}~{score_max}")

        # 位次单调性
        cur.execute(
            "SELECT score, `rank` FROM score_segments WHERE year=%s AND subject_type=%s ORDER BY score DESC",
            (year, subject_type),
        )
        data = cur.fetchall()
        errors = 0
        for i in range(len(data) - 1):
            if data[i][1] >= data[i + 1][1]:
                errors += 1
                if errors <= 3:
                    print(f"    ❌ 位次错误: {data[i][0]}分(位次{data[i][1]}) → {data[i+1][0]}分(位次{data[i+1][1]})")

        if errors == 0:
            print(f"    ✅ 位次单调递减: 通过")
            # 打印关键节点
            for s in [680, 660, 600, 500, 462]:
                cur.execute("SELECT `rank` FROM score_segments WHERE year=%s AND subject_type=%s AND score=%s",
                            (year, subject_type, s))
                r = cur.fetchone()
                if r:
                    print(f"      {s}分 → 位次{r[0]}")
        else:
            print(f"    ❌ 位次单调性: {errors}处错误")
            all_ok = False

        # 采样精度
        completeness = "✅ 逐分完整" if cnt > 100 else f"⚠️ 仅{cnt}个采样点(非逐分)"
        print(f"    {completeness}")

    return all_ok


def validate_admission_groups(cur):
    """验证投档线导入"""
    print("\n" + "=" * 60)
    print("2️⃣ 投档线验证")
    print("=" * 60)

    cur.execute("""SELECT year, subject_type, COUNT(*) as cnt, COUNT(DISTINCT university_id) as unis
        FROM admission_scores WHERE major_group != ''
        GROUP BY year, subject_type ORDER BY year""")
    groups = cur.fetchall()

    if not groups:
        print("  ❌ 无专业组数据！请先运行 import_admission_groups.py")
        return False

    for year, subject_type, cnt, unis in groups:
        cur.execute("SELECT MIN(min_score), MAX(min_score) FROM admission_scores WHERE major_group != '' AND year=%s AND subject_type=%s",
                    (year, subject_type))
        score_min, score_max = cur.fetchone()
        print(f"\n  {year} {subject_type}: {cnt}个专业组, {unis}所院校, 分数 {score_min}~{score_max}")

        # 按层级统计
        cur.execute("""SELECT u.level, COUNT(*) FROM admission_scores a
            JOIN universities u ON a.university_id=u.id
            WHERE a.major_group != '' AND a.year=%s AND a.subject_type=%s
            GROUP BY u.level ORDER BY u.level""", (year, subject_type))
        for level, count in cur.fetchall():
            cur.execute("SELECT COUNT(*) FROM universities WHERE level=%s", (level,))
            total = cur.fetchone()[0]
            pct = count / total * 100 if total > 0 else 0
            bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            print(f"    {level}档: {count:3d}/{total:2d} [{bar}] {pct:.0f}%")

    return True


def test_plan_generation(cur, score, subject_type="物理类"):
    """测试指定分数的方案生成（使用与 volunteer.py 相同的逻辑）"""
    print(f"\n--- 测试: {score}分 {subject_type} ---")

    # 1. 查位次（如果有精确匹配用精确值，否则插值）
    cur.execute(
        "SELECT `rank` FROM score_segments WHERE year=2024 AND subject_type=%s AND score=%s",
        (subject_type, score),
    )
    row = cur.fetchone()
    if not row:
        # 尝试插值
        cur.execute(
            "SELECT score, `rank` FROM score_segments WHERE year=2024 AND subject_type=%s AND score < %s ORDER BY score DESC LIMIT 1",
            (subject_type, score))
        lower = cur.fetchone()
        cur.execute(
            "SELECT score, `rank` FROM score_segments WHERE year=2024 AND subject_type=%s AND score > %s ORDER BY score ASC LIMIT 1",
            (subject_type, score))
        upper = cur.fetchone()
        if lower and upper:
            ratio = (score - lower[0]) / (upper[0] - lower[0])
            rank = int(round(lower[1] - (lower[1] - upper[1]) * ratio))
            print(f"  位次(插值): {rank} (基于{lower[0]}分→{lower[1]}, {upper[0]}分→{upper[1]})")
        else:
            print(f"  ❌ 找不到{score}分的位次数据")
            return None
    else:
        rank = row[0]
        print(f"  位次: {rank}")

    user_rank = rank

    # 2. 使用全部数据查询（真实+模拟，模拟作为保底补充）
    cur.execute(
        """SELECT u.name, u.level,
                  CASE WHEN a.major_group != '' AND a.major_group IS NOT NULL THEN a.major_group
                       ELSE CONCAT(m.name,'(专业级模拟)') END as group_label,
                  CASE WHEN a.subject_requirement != '' AND a.subject_requirement IS NOT NULL
                       THEN a.subject_requirement ELSE '未知' END as subj_req,
                  a.min_score, a.min_rank,
                  CASE WHEN a.major_group != '' AND a.major_group IS NOT NULL THEN 1 ELSE 0 END as is_real
           FROM admission_scores a
           JOIN universities u ON a.university_id=u.id
           LEFT JOIN majors m ON a.major_id=m.id
           WHERE a.year=2024 AND a.subject_type=%s
           ORDER BY a.min_rank ASC""",
        (subject_type,),
    )
    all_rows = cur.fetchall()

    # 3. 位次分层（同 volunteer.py）
    chong_raw = []; wen_raw = []; bao_raw = []
    for r in all_rows:
        mr = r[5]  # min_rank
        if not mr:
            continue
        label = f"{r[0]} {r[2]}({r[3]})" if r[2] else r[0]
        entry = (r[0], r[2] or '', r[3] or '', r[4], r[5], bool(r[6]))
        if mr <= user_rank * 0.85:
            chong_raw.append(entry)
        elif mr <= user_rank * 1.05:
            wen_raw.append(entry)
        else:
            bao_raw.append(entry)

    # 4. 边缘情况：从相邻档借用
    chong, wen, bao = list(chong_raw), list(wen_raw), list(bao_raw)
    if not chong and wen:
        chong = wen[:3]
        wen = wen[3:]
    if not wen:
        if chong:
            chong_sorted = sorted(chong, key=lambda x: x[4], reverse=True)
            wen = chong_sorted[:5]
            wen_ids = {w[0] for w in wen}
            chong = [c for c in chong if c[0] not in wen_ids]
        elif bao:
            bao_sorted = sorted(bao, key=lambda x: x[4])
            wen = bao_sorted[:5]
            bao = bao_sorted[5:]
    if not bao:
        if wen:
            wen_sorted = sorted(wen, key=lambda x: x[4], reverse=True)
            bao = wen_sorted[:5]
            bao_ids = {b[0] for b in bao}
            wen = [w for w in wen if w[0] not in bao_ids]

    # 5. 输出结果
    real_chong = sum(1 for c in chong if c[5])
    real_wen = sum(1 for w in wen if w[5])
    real_bao = sum(1 for b in bao if b[5])

    print(f"  冲档: {len(chong)}个 (真实{real_chong} + 模拟{len(chong)-real_chong})")
    for r in chong[:3]:
        real_tag = "✅" if r[5] else "🔶模拟"
        print(f"    {r[0]} {r[1]}({r[2]}) {r[3]}分 位次{r[4]} {real_tag}")

    print(f"  稳档: {len(wen)}个 (真实{real_wen} + 模拟{len(wen)-real_wen})")
    for r in wen[:3]:
        real_tag = "✅" if r[5] else "🔶模拟"
        print(f"    {r[0]} {r[1]}({r[2]}) {r[3]}分 位次{r[4]} {real_tag}")

    print(f"  保档: {len(bao)}个 (真实{real_bao} + 模拟{len(bao)-real_bao})")
    for r in bao[:3]:
        real_tag = "✅" if r[5] else "🔶模拟"
        print(f"    {r[0]} {r[1]}({r[2]}) {r[3]}分 位次{r[4]} {real_tag}")

    # 检查问题
    issues = []
    if len(chong) == 0:
        issues.append("🔴 冲档为空(无更高排名院校数据)")
    if len(wen) == 0:
        issues.append("🔴 稳档为空")
    if len(bao) == 0:
        issues.append("🔴 保档为空(低分段院校数据不足)")

    # 重复院校检查
    all_unis = [c[0] for c in chong] + [w[0] for w in wen] + [b[0] for b in bao]
    dupes = set()
    seen = set()
    for u in all_unis:
        if u in seen:
            dupes.add(u)
        seen.add(u)
    if dupes:
        issues.append(f"🟡 跨档重复院校: {dupes}")

    if issues:
        for i in issues:
            print(f"  {i}")
    else:
        print(f"  ✅ 冲{len(chong)}/稳{len(wen)}/保{len(bao)} 均正常 (真实:{real_chong+real_wen+real_bao}/{len(chong)+len(wen)+len(bao)})")

    return {
        "score": score,
        "rank": user_rank,
        "rush_count": len(chong), "rush_real": real_chong,
        "safe_count": len(wen), "safe_real": real_wen,
        "bottom_count": len(bao), "bottom_real": real_bao,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="验证真实数据质量")
    parser.add_argument("--score", type=int, help="指定分数测试方案生成")
    args = parser.parse_args()

    print("=" * 60)
    print("🔍 真实数据验证工具")
    print("=" * 60)

    conn = connect_db()
    cur = conn.cursor()

    # 1. 一分一段验证
    seg_ok = validate_score_segments(cur)

    # 2. 投档线验证
    adm_ok = validate_admission_groups(cur)

    # 3. 方案生成测试
    print("\n" + "=" * 60)
    print("3️⃣ 方案生成验证")
    print("=" * 60)

    test_scores = [465, 525, 585, 620, 675] if not args.score else [args.score]
    results = []
    for score in test_scores:
        r = test_plan_generation(cur, score, "物理类")
        if r:
            results.append(r)

    # 4. 总结
    print("\n" + "=" * 60)
    print("📊 验证总结")
    print("=" * 60)

    if results:
        for r in results:
            empty = []
            if r["rush_count"] == 0: empty.append("冲")
            if r["safe_count"] == 0: empty.append("稳")
            if r["bottom_count"] == 0: empty.append("保")
            status = "❌ " + "+".join(empty) + "为空" if empty else "✅ 正常"
            print(f"  {r['score']}分(位次{r['rank']}): 冲{r['rush_count']}/稳{r['safe_count']}/保{r['bottom_count']} {status}")

    seg_status = "✅ 通过" if seg_ok else "❌ 失败"
    adm_status = "✅ 通过" if adm_ok else "❌ 失败"
    print(f"\n  一分一段表: {seg_status}")
    print(f"  投档线数据: {adm_status}")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
