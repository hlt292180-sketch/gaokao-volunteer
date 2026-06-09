# 高考志愿填报辅助系统 —— 项目总结 v3（2026年6月5日更新）

## 1. 项目是什么

一个 Web 网站，帮江苏高考考生科学填报志愿。核心功能：输入分数 → 查全省位次 → 自动生成"冲/稳/保"三档志愿方案。

## 2. 目标用户

- 主要使用者：江苏高三考生（17-19岁）
- 主要买单人：家长（40-50岁，学历偏低，对线上工具不够信任）
- 传播者：高中老师 / 亲戚

## 3. 产品形态

Web 网站（PC + 手机端响应式），技术栈：React 18 + Vite + Flask + MySQL + Tailwind CSS。
编辑/杂志风设计体系（Georgia 衬线标题、深靛蓝主色、暖琥珀 CTA、暖白底）。

## 4. 免费版 vs 付费版（￥39 首批体验价）

| 免费版 | 付费版 |
|--------|--------|
| 分数 → 位次换算 | 全部免费功能 |
| 院校/专业查询 | 完整冲稳保方案（无限次） |
| 兴趣测评（1次，后端强制限制） | 完整体检报告（5项全显示） |
| 方案生成（1次，每档仅显示第1所，其余打码） | 方案全量展示 + 趋势预测 |
| 志愿体检（1次，仅显示1个问题） | 专业趋势预测（需求/饱和度/薪资/置信度） |
| 专业趋势预测（全部打码 + 付费遮罩） | |

**安全**：免费次数在前端和后端各校验一次，用户无法通过直接调 API 绕过。

## 5. 当前开发状态

### 后端（Flask）— 9 个路由模块，23 个 API 接口

| 模块 | 端点 | 说明 |
|------|------|------|
| auth | register, login, me | bcrypt + JWT，管理员自动视为付费 |
| province | GET / | 省份列表 |
| score | GET /convert | 分数→位次→等效分换算 |
| university | GET /, GET /:id | 院校列表 + 详情+历年录取线 |
| major | GET /, GET /:id, GET /:id/trend | 专业列表 + 详情+就业画像 + 趋势预测 |
| assessment | questions, submit, latest, result/:id | 霍兰德测评（30题），免费1次后端限制 |
| volunteer | check, generate, plans, plans/:id | 体检（5项）+ 冲稳保方案生成，免费各1次后端限制 |
| payment | create, status/:no, pending, approve/:no | 创建订单 + 去重 + 管理员审核列表 + 审核通过 |
| analytics | track, stats | 7类事件埋点 + 管理员统计仪表盘（JWT鉴权） |

### 数据库（MySQL）— 13 张表

users, provinces, score_segments, universities, majors, admission_scores, major_profiles, major_trends, assessment_questions, assessment_results, volunteer_plans, payments, analytics_events

种子数据：34 所院校、30 个专业、3 年录取分数线、8 条趋势预测、13 条就业画像

### 前端（React + Vite）— 17 个页面，4 个组件

```
components/  4 个：Layout, Navbar, Footer, ProtectedRoute
pages/      17 个：Home, Login, Register, ScoreConvert,
                   UniversityList, UniversityDetail,
                   MajorList, MajorDetail, Assessment,
                   VolunteerCheck, PlanGenerate, PlanList,
                   PlanDetail, Profile, Upgrade, Admin
services/    2 个：api.js（axios封装）, track.js（埋点工具）
store/       1 个：authStore.js（Zustand）
assets/      0 个（空目录，脚手架残留已清理）
```

### 本次更新（v2 → v3）完成的改动

**页面优化：**
- 首页：五屏结构（Hero → 为什么选我们 → 真实案例 → 数据来源 → 免责声明）
- 方案生成页：单页三状态（表单 → 四段式结果 → 免费次数用完付费引导）
- 付费页 Upgrade：六段结构，价格锚定（原价168划线 → 首批39）
- 专业详情页：趋势预测真实数据展示，免费用户模糊打码 + 遮罩 CTA
- 后台仪表盘：5 指标卡 + 转化漏斗 + 每日趋势 + 支付订单管理（审核/开通）

**安全修复（代码审计后）：**
- 埋点 JWT 解析 bug 修复（user_id → userId，之前所有登录用户埋点为 NULL）
- 免费测评/体检次数从纯前端限制→前后端双重校验
- 支付订单去重（同一用户已有 pending 时返回已有订单）
- 统计接口加管理员鉴权
- 过期链接修复（VolunteerCheck → /upgrade）

**代码清理：**
- 删除 5 个冗余文件（3 个 Vite 脚手架残留、AssessmentResult.jsx、PaidFeature.jsx）
- PaidFeature 逻辑内联到 MajorDetail.jsx
- 死代码导出 getPaymentStatus、getAssessmentResult 已删除
- 项目文件数：30 → 24

**支付流程：**
1. 用户访问 /upgrade → 看到功能清单 + 价格 ￥39
2. 扫码付款 → 点击"我已付款" → 创建 pending 订单（自动去重）
3. 管理员 /admin 后台 → "待审核付款"列表 → 点"确认支付"
4. 系统自动：payments.status='paid' + users.is_paid=1
5. 用户刷新 → 全部付费功能解锁

## 6. 当前已知问题

### 6.1 功能缺口

| 缺口 | 严重程度 | 说明 |
|------|----------|------|
| 真实录取数据 | **高** | 目前是种子模拟数据（34所院校、编造分数）。需要从江苏省教育考试院获取或爬取真实数据 |
| 部署上线 | **高** | 目前仅本地开发环境运行。需要买服务器/域名、配置生产环境 |
| 拼团功能 | 低 | 数据库有 payments 表但无拼团逻辑，前端无拼团入口 |
| 专业对比页 | 低 | 技术方案写了但从未创建 |
| 方案对比 | 中 | 付费权益写"多方案对比"，PlanList 只能逐个查看 |
| 收款码 | **高** | 仍为占位图。需要有真实个人收款码图片替换 |

### 6.2 体验问题

| 问题 | 说明 |
|------|------|
| 部分老页面样式不统一 | Login、Register、ScoreConvert、VolunteerCheck 等仍用 Tailwind 原生蓝（bg-blue-600），与首页/方案页的编辑风设计差距明显 |
| 无统一错误页面 | 404/500 无自定义页面 |
| CORS 未配置 | 开发时 Vite proxy 解决，生产部署需配 Flask-CORS |

### 6.3 安全提醒（开发阶段可接受）

- config.py 数据库密码和 JWT 密钥有默认值硬编码（可通过环境变量覆盖）
- 埋点 track 接口无限流保护
- 分页参数无上限（limit 可传极大值）

## 7. 我想请教 GPT 的问题

1. **部署方案**：明天（6月7日）高考，出分是 6月24日。我现在应该立刻部署上线（哪怕数据不完美），还是等真实数据到位再上线？如果现在部署，最简方案是什么（推荐服务器/域名平台）？

2. **数据获取**：江苏省教育考试院的录取数据，有什么合法合规的获取方式？如果暂时获取不到真实数据，用模拟数据上线会不会有法律风险？

3. **定价策略**：39 元首批体验价策略要不要在出分后（6月24日）涨回 168？涨价时机怎么把握？

4. **推广时机**：我是一个人，没有团队。高考前（6月7日前）、出分前（6月7-24日）、出分后（6月24日后），哪个阶段重点做什么类型的推广？

5. **现存风险**：上面列的已知问题里，有没有我低估了的、可能导致项目失败的风险点？

6. **下一步**：如果从现在到 6月24日出分只有 18 天，我应该把时间花在哪 3 件事上？优先级排序。
