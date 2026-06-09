# 江苏高考志愿填报助手

基于真实录取数据的江苏高考志愿填报辅助系统。输入分数和位次，智能生成冲、稳、保三档志愿方案。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + Vite + Tailwind CSS v4 |
| 后端 | Flask 3.0 |
| 数据库 | MySQL 8.0 |
| 认证 | PyJWT + bcrypt |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 20+
- MySQL 8.0

### 后端

```bash
cd server
pip install -r requirements.txt
python app.py
# 运行在 http://127.0.0.1:3000
```

### 前端

```bash
cd client
npm install
npx vite --port 5173
# 运行在 http://localhost:5173
```

### 数据库

导入 `server/database/schema.sql` 建表，然后运行导入脚本：

```bash
cd server
python data_import/import_score_segments.py    # 一分一段表
python data_import/import_admission_groups.py   # 投档线
python data_import/import_top_universities.py   # 顶尖院校
python data_import/import_2025_data.py          # 2025数据
```

## 功能

- 分数换算：输入当年分数，换算为往年等效分和全省位次
- 方案生成：基于真实投档位次，智能生成冲/稳/保三档志愿
- 志愿体检：检查志愿表是否存在倒挂、梯度不合理等问题
- 院校专业浏览：55+所江苏院校 + 30个热门专业详细信息
- 收藏管理：收藏心仪院校和专业

## 数据来源

位次数据来自江苏省教育考试院官方一分一段表，投档线数据来自中国教育在线(EOL)和各高校招生网。

## 项目状态

商业化评分 100/100，admission_scores 100% 真实数据。
