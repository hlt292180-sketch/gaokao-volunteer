# -*- coding: utf-8 -*-
"""数据库审计脚本 - 生成完整的审计数据"""
import pymysql
import json

conn = pymysql.connect(
    host='localhost', user='root', password='292180',
    database='gaokao', charset='utf8mb4'
)
cur = conn.cursor()

results = {}

# 1. admission_scores
cur.execute('SELECT COUNT(*) FROM admission_scores')
results['admission_total'] = cur.fetchone()[0]

cur.execute('SELECT DISTINCT year FROM admission_scores ORDER BY year')
results['admission_years'] = [r[0] for r in cur.fetchall()]

cur.execute('SELECT DISTINCT subject_type FROM admission_scores')
results['admission_subjects'] = [r[0] for r in cur.fetchall()]

cur.execute('SELECT COUNT(DISTINCT university_id) FROM admission_scores')
results['admission_universities'] = cur.fetchone()[0]

cur.execute('SELECT COUNT(DISTINCT major_id) FROM admission_scores WHERE major_id IS NOT NULL')
results['admission_majors'] = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM admission_scores WHERE major_id IS NULL')
results['admission_null_major'] = cur.fetchone()[0]

cur.execute('SELECT MIN(min_score), MAX(min_score), AVG(min_score) FROM admission_scores')
r = cur.fetchone()
results['admission_score_range'] = f"{r[0]} ~ {r[1]}, avg={r[2]:.1f}"

cur.execute('SELECT MIN(min_rank), MAX(min_rank), AVG(min_rank) FROM admission_scores')
r = cur.fetchone()
results['admission_rank_range'] = f"{r[0]} ~ {r[1]}, avg={r[2]:.0f}"

cur.execute('SELECT batch, COUNT(*) FROM admission_scores GROUP BY batch')
results['admission_batches'] = [(r[0], r[1]) for r in cur.fetchall()]

cur.execute('SELECT min_score, COUNT(*) as cnt FROM admission_scores GROUP BY min_score ORDER BY cnt DESC LIMIT 5')
results['admission_top_dup_scores'] = [(r[0], r[1]) for r in cur.fetchall()]

cur.execute('SELECT COUNT(*) FROM admission_scores WHERE min_score % 5 = 0')
results['admission_mod5'] = cur.fetchone()[0]

# By tier
cur.execute('''SELECT u.level, COUNT(*), AVG(a.min_score), MIN(a.min_score), MAX(a.min_score)
FROM admission_scores a JOIN universities u ON a.university_id=u.id
GROUP BY u.level ORDER BY u.level''')
results['admission_by_tier'] = [(r[0], r[1], float(r[2]), r[3], r[4]) for r in cur.fetchall()]

# 2. score_segments
cur.execute('SELECT COUNT(*) FROM score_segments')
results['segments_total'] = cur.fetchone()[0]

cur.execute('SELECT year, subject_type, COUNT(*), COUNT(DISTINCT score), MIN(score), MAX(score) FROM score_segments GROUP BY year, subject_type')
results['segments_detail'] = [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in cur.fetchall()]

cur.execute('SELECT DISTINCT subject_type FROM score_segments')
results['segments_subjects'] = [r[0] for r in cur.fetchall()]

# Get sample ranks for key scores
results['segments_samples'] = {}
for s in [300, 400, 462, 500, 550, 600, 650, 660, 680, 690]:
    cur.execute('SELECT score, `rank` FROM score_segments WHERE year=2024 AND score=%s', (s,))
    r = cur.fetchone()
    if r:
        results['segments_samples'][s] = r[1]

# Check 3-year similarity
cur.execute('SELECT COUNT(*) FROM (SELECT score, `rank` FROM score_segments WHERE year=2023) a JOIN (SELECT score, `rank` FROM score_segments WHERE year=2024) b ON a.score=b.score AND a.`rank`=b.`rank`')
results['segments_3year_match_23_24'] = cur.fetchone()[0]

cur.execute('SELECT score FROM score_segments WHERE year=2024 ORDER BY score ASC LIMIT 10')
results['segments_first10'] = [r[0] for r in cur.fetchall()]

# Check interval pattern
cur.execute('SELECT score FROM score_segments WHERE year=2024 ORDER BY score ASC')
all_scores = [r[0] for r in cur.fetchall()]
diffs = [all_scores[i+1]-all_scores[i] for i in range(min(20, len(all_scores)-1))]
results['segments_intervals'] = diffs

# 3. major_profiles
cur.execute('SELECT COUNT(*) FROM major_profiles')
results['profiles_total'] = cur.fetchone()[0]

cur.execute('''SELECT m.name, mp.avg_starting_salary, mp.employment_rate_3yr,
    mp.postgrad_rate, mp.holland_code, mp.data_year
FROM major_profiles mp JOIN majors m ON mp.major_id=m.id''')
results['profiles_list'] = [(r[0], r[1], float(r[2]), float(r[3]), r[4], r[5]) for r in cur.fetchall()]

# 4. major_trends
cur.execute('SELECT COUNT(*) FROM major_trends')
results['trends_total'] = cur.fetchone()[0]

cur.execute('''SELECT m.name, mt.year_forecast, mt.demand_trend, mt.saturation_level,
    mt.avg_salary_forecast, mt.confidence
FROM major_trends mt JOIN majors m ON mt.major_id=m.id''')
results['trends_list'] = [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in cur.fetchall()]

# 5. majors total
cur.execute('SELECT COUNT(*) FROM majors')
results['majors_total'] = cur.fetchone()[0]

cur.execute('SELECT id, name FROM majors')
results['majors_list'] = [(r[0], r[1]) for r in cur.fetchall()]

# 6. universities
cur.execute('SELECT COUNT(*) FROM universities')
results['universities_total'] = cur.fetchone()[0]

cur.execute('SELECT level, COUNT(*) FROM universities GROUP BY level ORDER BY level')
results['universities_by_level'] = [(r[0], r[1]) for r in cur.fetchall()]

cur.execute('SELECT name, level FROM universities ORDER BY level, name')
results['universities_list'] = [(r[0], r[1]) for r in cur.fetchall()]

conn.close()

print(json.dumps(results, ensure_ascii=False, indent=2))
