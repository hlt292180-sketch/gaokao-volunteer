# 商业化评分计算公式说明

> 评分引擎：`server/services/coverage_service.py`
> 收费门槛：commercialScore ≥ 85/100

---

## 一、评分公式

```
commercialScore = Σ(各项得分)

data_authenticity    (满分40) = segmentScore(20) + sourceScore(20)
university_coverage  (满分20) = coveredUniversities / targetUniversities × 20
major_group_coverage (满分15) = coveredGroups / targetGroups × 15
year_coverage        (满分10) = coveredYears / targetYears × 10
high_score_coverage  (满分15) = coveredTopSchools / targetTopSchools × 15
```

## 二、各项参数定义

| 参数 | 当前值 | 目标值 | 说明 |
|------|--------|--------|------|
| coveredUniversities | 55 | 55 | 有OFFICIAL数据的院校数 |
| targetUniversities | 55 | 55 | 系统内江苏院校总数 |
| coveredGroups | 100 | 165 | 不重复(院校+专业组)组合数 |
| targetGroups | 165 | 165 | 55校×3组/校 |
| coveredYears | 2 | 3 | {2023, 2024} |
| targetYears | 3 | 3 | {2023, 2024, 2025} |
| coveredTopSchools | 2 | 8 | 650+有OFFICIAL的TOP院校 |
| targetTopSchools | 8 | 8 | 清北复交浙科南东 |

## 三、当前评分拆解（80分/B级）

```
数据真实性      40.0 ████████████████████  ✅ (一分一段100%真 + 有OFFICIAL数据)
院校覆盖        20.0 ██████████             ✅ (55/55 = 100%)
专业组覆盖       9.1 ████▌                  ⚠️ (100/165 = 60.6%)
年份覆盖         6.7 ███▎                   ⚠️ (2/3 = 66.7%)
高分段覆盖       3.8 █▉                     🔴 (2/8 = 25%)
────────────────────────────────────────────────────
总分            80/100  B级
```

## 四、评分等级

| 等级 | 分数范围 | 含义 |
|------|----------|------|
| A | ≥90 | 商业化就绪 |
| B | ≥80 | 接近商业化(当前) |
| C | ≥70 | 公测质量 |
| D | ≥60 | 内部测试 |
| F | <60 | 不可用 |

## 五、收费判定

```
if commercialScore >= 85:
    ALLOW_PAYMENT = True   # 自动开启
else:
    ALLOW_PAYMENT = False  # 自动锁定
```

环境变量 `ALLOW_PAYMENT=true` 可手动覆盖（管理员强制开启）。
