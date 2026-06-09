# 高考志愿填报辅助系统 - 技术实现计划（重构版）

> 更新时间：2026年6月1日  
> 当前进度：阶段 9 联调测试中

---

## 一、项目概述

**目标**：构建一个 Web 版高考志愿填报辅助系统，专门针对江苏省考生，包含免费版（获客引流）和付费版（深度决策辅助），两者有明显价值梯度。

**用户**：江苏高考考生（主用） + 家长（买单）  
**平台**：Web 网站（响应式，PC + 移动端）  
**一句话定位**：用数据代替拍脑袋，把每一分都用到极致——江苏高考志愿决策工具

---

## 二、技术选型

| 层 | 技术 | 语言 | 说明 |
|---|---|---|---|
| 前端框架 | React 18 + Vite | JavaScript | HMR 快速开发 |
| 路由 | React Router v6 | — | SPA 页面路由 |
| 状态管理 | Zustand | — | 轻量 |
| 样式 | Tailwind CSS | — | 原子化 CSS |
| 设计辅助 | Anthropic frontend-design skill | — | 避免 AI 审美 |
| 图表 | Recharts | — | 专业对比可视化 |
| 后端框架 | Flask | Python | 轻量灵活、学习曲线平 |
| 数据库 | MySQL | SQL | 用户已熟悉 |
| 认证 | JWT（PyJWT） | — | 无状态鉴权 |
| 支付 | 个人收款码 + 手动确认 | — | 无需营业执照 |

---

## 三、项目目录结构（待实现）

```
gaokao-volunteer/
├── client/                          # React 前端
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx                 # 入口
│       ├── App.jsx                  # 路由配置
│       ├── components/              # 通用组件
│       │   ├── Layout.jsx           # 页面布局（导航+页脚）
│       │   ├── Navbar.jsx           # 顶部导航
│       │   ├── Footer.jsx           # 页脚
│       │   ├── ProtectedRoute.jsx   # 登录保护路由
│       │   └── PaidFeature.jsx      # 付费功能门控组件
│       ├── pages/
│       │   ├── Home.jsx             # 首页（纯宣传页）
│       │   ├── Login.jsx / Register.jsx
│       │   ├── ScoreConvert.jsx     # 分数位次换算
│       │   ├── UniversityList.jsx / UniversityDetail.jsx
│       │   ├── MajorList.jsx / MajorDetail.jsx
│       │   ├── Assessment.jsx / AssessmentResult.jsx
│       │   ├── VolunteerCheck.jsx   # 志愿体检
│       │   ├── PlanGenerate.jsx / PlanList.jsx / PlanDetail.jsx
│       │   ├── MajorCompare.jsx     # 多专业对比
│       │   ├── Profile.jsx          # 个人中心
│       │   └── Admin.jsx            # 管理员后台
│       ├── services/api.js          # API 请求封装
│       └── store/authStore.js       # 认证状态管理
│
├── server/                          # Flask 后端
│   ├── requirements.txt
│   ├── app.py                       # 入口
│   ├── config.py                    # 配置
│   ├── models.py                    # 数据库模型
│   ├── routes/
│   │   ├── auth.py                  # 注册/登录
│   │   ├── score.py                 # 分数位次
│   │   ├── university.py           # 院校
│   │   ├── major.py                # 专业
│   │   ├── assessment.py           # 测评
│   │   ├── volunteer.py            # 志愿方案
│   │   └── payment.py              # 支付
│   └── services/                    # 业务逻辑
│       ├── score_service.py        # 位次换算
│       ├── plan_service.py         # 方案生成
│       └── match_service.py        # 匹配度算法
│
└── 学习笔记.md
```

---

## 四、数据库设计（12张表，已完成）

### 表结构（共 12 张表）

```sql
-- 1. 用户表
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  phone TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  nickname TEXT,
  is_paid INTEGER DEFAULT 0,
  is_admin INTEGER DEFAULT 0,
  paid_expire_at DATETIME,
  free_check_count INTEGER DEFAULT 0,
  free_assessment_count INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 省份表
CREATE TABLE provinces (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name TEXT NOT NULL UNIQUE,
  code TEXT NOT NULL UNIQUE
);

-- 3. 一分一段表
CREATE TABLE score_segments (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  province_id INTEGER NOT NULL REFERENCES provinces(id),
  year INTEGER NOT NULL,
  score INTEGER NOT NULL,
  rank INTEGER NOT NULL,
  subject_type TEXT NOT NULL,
  UNIQUE(province_id, year, score, subject_type)
);

-- 4. 院校表
CREATE TABLE universities (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name TEXT NOT NULL,
  province_id INTEGER REFERENCES provinces(id),
  city TEXT,
  level TEXT,
  type TEXT,
  is_985 INTEGER DEFAULT 0,
  is_211 INTEGER DEFAULT 0,
  is_double_first_class INTEGER DEFAULT 0,
  website TEXT,
  intro TEXT
);

-- 5. 专业表
CREATE TABLE majors (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  subcategory TEXT,
  intro TEXT,
  degree TEXT,
  duration INTEGER DEFAULT 4
);

-- 6. 录取分数线（核心查询表）
CREATE TABLE admission_scores (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  university_id INTEGER NOT NULL REFERENCES universities(id),
  major_id INTEGER REFERENCES majors(id),
  province_id INTEGER NOT NULL REFERENCES provinces(id),
  year INTEGER NOT NULL,
  subject_type TEXT NOT NULL,
  batch TEXT NOT NULL,
  min_score INTEGER NOT NULL,
  min_rank INTEGER,
  avg_score INTEGER,
  plan_count INTEGER,
  UNIQUE(university_id, major_id, province_id, year, subject_type, batch)
);

-- 7. 专业就业画像
CREATE TABLE major_profiles (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  major_id INTEGER NOT NULL UNIQUE REFERENCES majors(id),
  avg_starting_salary INTEGER,
  employment_rate_3yr REAL,
  top_industries TEXT,
  top_positions TEXT,
  top_cities TEXT,
  postgrad_rate REAL,
  holland_code TEXT,
  data_year INTEGER
);

-- 8. 专业趋势预测
CREATE TABLE major_trends (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  major_id INTEGER NOT NULL REFERENCES majors(id),
  year_forecast INTEGER NOT NULL,
  demand_trend TEXT NOT NULL,
  saturation_level TEXT NOT NULL,
  avg_salary_forecast INTEGER,
  confidence TEXT,
  data_source TEXT,
  summary TEXT,
  UNIQUE(major_id, year_forecast)
);

-- 9. 测评题库
CREATE TABLE assessment_questions (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  question_text TEXT NOT NULL,
  options TEXT NOT NULL,
  dimension TEXT NOT NULL
);

-- 10. 用户测评结果
CREATE TABLE assessment_results (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  result_scores TEXT NOT NULL,
  primary_type TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 11. 志愿方案
CREATE TABLE volunteer_plans (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  province_id INTEGER REFERENCES provinces(id),
  plan_name TEXT,
  subject_type TEXT,
  score INTEGER,
  rank INTEGER,
  plans_data TEXT NOT NULL,
  strategy_type TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 12. 支付记录
CREATE TABLE payments (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  amount REAL NOT NULL,
  status TEXT DEFAULT 'pending',
  order_no TEXT NOT NULL UNIQUE,
  plan TEXT,
  paid_at DATETIME,
  expire_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 五、API 设计

### 公开接口（无需登录）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/provinces | 省份列表 |
| GET | /api/score-segments/:id | 一分一段查询 |
| GET | /api/score-segments/convert | 分数位次换算 |
| GET | /api/universities | 院校列表（筛选+分页） |
| GET | /api/universities/:id | 院校详情+历年录取线 |
| GET | /api/majors | 专业列表 |
| GET | /api/majors/:id | 专业基础画像 |
| GET | /api/admission-scores | 录取分数查询 |

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录→返回JWT |
| GET | /api/auth/me | 当前用户信息（含 isPaid/isAdmin） |

### 需登录接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/assessments/questions | 测评题目 |
| POST | /api/assessments/submit | 提交测评 |
| GET | /api/assessments/result/:id | 测评结果 |
| POST | /api/volunteer/check | 志愿体检 |
| GET | /api/user/profile | 用户信息 |

### 付费接口（需付费鉴权，管理员自动放行）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/volunteer/generate | AI生成志愿方案 |
| GET | /api/volunteer/plans | 方案列表 |
| GET | /api/volunteer/plans/:id | 方案详情 |
| POST | /api/majors/compare | 多专业对比 |
| GET | /api/majors/:id/trend | 专业趋势预测 |
| POST | /api/majors/match | 专业匹配度 |
| POST | /api/payment/create | 创建订单 |
| GET | /api/payment/status/:no | 支付状态 |

---

## 六、核心算法设计

### 6.1 分数→位次→同位分换算

```
输入：江苏省 2025年 物理类 620分
1. 查一分一段表：620分 → 全省位次 8680名
2. 查2024年数据：位次8680名 → 对应618分（同位分）
3. 用618分搜索2024年录取数据
关键：用"位次"而非"分数"做匹配（位次更稳定）
```

### 6.2 志愿方案生成（冲稳保策略）

```
1. 冲（前20%）：近3年最低录取位次 ≤ 考生位次 × 0.85
   → 录取概率 20%-40%
2. 稳（中间40%）：最低录取位次在考生位次 × 0.7 ~ 0.85
   → 录取概率 50%-70%
3. 保（后40%）：最低录取位次 < 考生位次 × 0.7
   → 录取概率 80%+
输出：江苏省可填40个专业组志愿，按冲稳保比例分配
```

### 6.3 志愿体检规则引擎

检测项：梯度检查、倒挂检测、保底检查、总量检查、批次一致性

### 6.4 录取概率模型

基于近3年录取位次的正态分布估算

### 6.5 专业匹配度算法

用户霍兰德测评向量 × 专业霍兰德画像向量 → 余弦相似度 → 0-100匹配分

### 6.6 趋势预测

基于教育部就业报告和行业数据，预测4年后专业需求/薪资/饱和度走势

---

## 七、定价方案

| 方案 | 价格 | 说明 |
|---|---|---|
| **标准版** | ￥168 | 单次购买，无限方案生成+全部付费功能 |
| **三人拼团** | ￥128/人 | 社交裂变传播 |

> **定价逻辑**：线下咨询师 3000-8000 元，优志愿 360-388 元，夸克 Pro 199 元。168 元卡在中间位置——比一本书贵、比竞品便宜一半，不超过 200 心理门槛。取消季卡因为志愿填报是单次决策，不存在"反复使用"场景。

---

## 八、后续可扩展方向（本次不做）

- 接入微信/支付宝真支付（需营业执照）
- 对接各省教育考试院实时数据
- 接入 AI 大模型做方案推荐
- 小程序版本
