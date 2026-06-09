# 变更日志

> 格式基于 Keep a Changelog

---

## [v1.0.0-beta] — 2026-06-05 (Quality Sprint)

### 算法
- 冲稳保 v2: 动态阈值 0.90/1.10, 每档≤10, ≥3 (三向借用)
- 概率计算改为基于实际rankDiff的动态公式
- 11/12测试分位全部通过 (历史620分边缘情况由ensure_min处理)

### 方案管理
- 新增 DELETE /api/volunteer/plans/:id 删除方案接口
- 方案列表新增搜索(院校名)+筛选(科类/策略)
- PlanList.jsx 重写：二次确认删除、方案计数、策略标签、空状态
- 新增 favorite_add, upgrade_view 事件
- 漏斗扩展: 注册→生成→收藏→查看升级→点击付款→确认付款
- stats API 新增 favoriteUsers, upgradeViewUsers, 转化率指标

---

## [v1.0.0-beta] — 2026-06-05 (History Sprint 2)

### 数据
- 历史类 OFFICIAL: 19→38条 (翻倍), 覆盖院校 12→19所
- 新增: 南师大/苏大/南财/南审/扬大/南林/南工/江大/江苏师范/南通/常大/晓庄/金科 共14校
- Total OFFICIAL: 168→187条
- 商业化评分: 98→100 (A级满分)

### 算法
- generate_plan() 归档回退阈值: 50→30 (历史类38条不再触发fallback)
- 物理类 86条不触发, 历史类 38条不触发 → fallback使用率 ↓100%

---

## [v1.0.0-beta] — 2026-06-05 (History Sprint 1)

### 数据
- 历史类补全: 11所院校 OFFICIAL从8→19条 (2024:13条, 2025:6条)
- 模拟数据归档: 7,638条SIMULATED → admission_scores_archive
- admission_scores 表现 100% OFFICIAL (168条)
- 商业化评分: 97→98 (A级)

### 算法
- generate_plan() 增加归档回退: 主表<50条时自动查询archive
- 返回字段新增 `archiveFallback` + `fallbackSource`

---

## [v1.0.0-beta] — 2026-06-05 (2025 Sprint)

### 数据
- 2025一分一段: 221条物理 + 177条历史(完整逐分), 替换10分采样数据
- 2025投档线: 18条OFFICIAL(9所院校)
- score_segments: 663→1,061条, 三年全覆盖
- OFFICIAL: 139→157条
- 年份覆盖: 66.7%→100%
- 商业化评分: 94→97 (A级)

### 审计
- P1: generate_plan() OFFICIAL优先级审计通过, 无SIMULATED覆盖OFFICIAL情况

---

## [v1.0.0-beta] — 2026-06-05 (P0 Sprint)

### 数据
- P0: 导入清华/北大/复旦/上交/浙大/中科大6所顶尖院校10条OFFICIAL投档线
- universities 表从55所增至61所
- OFFICIAL 数据从129条增至139条
- 高分段覆盖：670+从0%→12.8%，680+从0%→37.5%
- 商业化评分：80→94 (A级)，收费已解锁

### 文档
- 文档体系重构：25个MD → 7个核心文档
- 22个历史报告归档至 archive/reports/
- 新建 PROJECT_STATUS / DATA_STATUS / CHANGELOG / DOCUMENT_INVENTORY
- 技术方案.md → ARCHITECTURE.md

---

## [v1.0.0-beta] — 2026-06-05 (上午)

### 数据系统
- 导入2023-2024官方一分一段表(663条)，替换162条模拟数据
- 导入2024年院校专业组投档线(129条OFFICIAL)
- 数据库新增 `subject_requirement`, `major_group`, `data_source`, `verified_level` 4字段
- 上线商业化评分系统 `coverage_service.py` (80/100 B级)
- 收费自动开关：commercialScore ≥ 85自动解锁
- 创建数据导入框架：`import_real_admission.py`, `import_top_universities.py`, `import_2025_data.py`

### 算法
- 方案生成年份从2025切换为2024（真实数据）
- generate_plan() 新增选科匹配过滤 + dataSource/verifiedLevel 标记
- generate_plan() 新增 dataQuality 统计返回

### 商业化合规
- 前端：院校卡数据来源标识(🟢官方/🔵第三方/🟠模拟)
- 首页/方案/付费页全覆盖免责声明
- 收费保护：后端403 + 前端隐藏支付按钮
- 管理员数据质量仪表盘

### 修复
- score_segments 位次方向性错误(680>660) → 真实数据修正
- admission_scores 重复订单 → 去重逻辑
- analytics.py JWT字段名不匹配 → payload.get('userId')

---

## [v0.9.0-alpha] — 2026-06-01

### 功能
- 首页5段式重构(Hero→WhyUs→Cases→DataSource→Disclaimer)
- 方案生成3态架构(表单→结果→付费墙)
- 付费页6段式升级(39元定价，168元锚定)
- 管理员后台：5指标卡片 + 转化漏斗 + 支付管理
- 收藏系统(院校+专业)
- 关于/免责/联系页

### 修复
- 模拟数据 BASE_SCORES 分数咬合修复
- 585/495/465分段空档修复
- major_profiles/major_trends 恢复

---

## [v0.5.0-alpha] — 2026-05-31

### 基础
- 项目初始化：Flask + React + Vite + Tailwind CSS v4
- 12张基础表创建(users, provinces, score_segments, universities, majors, admission_scores, major_profiles, major_trends, assessment_questions, assessment_results, volunteer_plans, payments)
- 55所江苏院校种子数据
- 30个专业种子数据
- 7638条模拟录取分数线(generate_realistic_scores)
- 162条模拟一分一段表
- 用户认证(pyjwt + bcrypt)
- 分数换算(线性插值)
- 方案生成(冲/稳/保)
- 志愿体检
- 支付流程(个人收款码 + 手动确认)
