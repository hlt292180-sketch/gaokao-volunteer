# 文档体系重构报告

> 执行日期：2026-06-05 | 操作：归档 + 合并 + 新建

---

## 一、变更摘要

| 操作 | 数量 | 详情 |
|------|------|------|
| 新建核心文档 | 4 | PROJECT_STATUS, DATA_STATUS, CHANGELOG, DOCUMENT_INVENTORY |
| 归档历史报告 | 22 | → archive/reports/ |
| 重命名 | 1 | 技术方案.md → ARCHITECTURE.md |
| 删除 | 1 | 学习笔记.md (个人笔记) |
| **根目录变化** | **25 → 7** | |

## 二、保留的文档 (7个)

| 文件 | 类型 | 说明 |
|------|------|------|
| **PROJECT_STATUS.md** | 长期维护 | 项目唯一状态源(版本/成熟度/收费/优先级) |
| **DATA_STATUS.md** | 长期维护 | 数据唯一状态源(合并15份数据报告) |
| **ARCHITECTURE.md** | 长期维护 | 技术架构(原技术方案.md) |
| **CHANGELOG.md** | 长期维护 | 版本变更日志 |
| DOCUMENT_INVENTORY.md | 参考 | 文档索引 |
| 管理员账号.md | 参考 | 系统账号信息 |
| 给GPT的项目总结.md | 参考 | AI对话上下文 |

## 三、归档的文档 (22个 → archive/reports/)

### 数据类 (15个)
`REAL_DATA_AUDIT.md` `REAL_DATA_VALIDATION_REPORT.md` `REAL_DATA_GAP_REPORT.md`
`REAL_DATA_COLLECTION_PLAN.md` `REAL_DATA_COMPLIANCE_REPORT.md` `REAL_DATA_BACKLOG.md`
`REAL_COVERAGE_GAP_REPORT.md` `DATA_ACCURACY_REPORT.md` `HIGH_SCORE_COVERAGE_REPORT.md`
`IMPORT_SCORE_SEGMENTS_REPORT.md` `IMPORT_ADMISSION_REPORT.md` `IMPORT_2025_READINESS_REPORT.md`
`真实数据源验证报告.md` `真实数据迁移方案.md` `数据库扩展方案.md`

### 商业化类 (7个)
`COMMERCIAL_DECISION_REPORT.md` `COMMERCIAL_READINESS_REPORT.md` `COMMERCIAL_SCORE_EXPLAIN.md`
`FINAL_COMMERCIAL_READINESS_REPORT.md` `PAYMENT_UNLOCK_TEST_REPORT.md`
`PRODUCTION_READINESS_REPORT.md` `GROWTH_ROADMAP.md`

## 四、新文档体系

```
项目根目录/
├── PROJECT_STATUS.md      ← 查项目状态看这个
├── DATA_STATUS.md         ← 查数据状态看这个
├── ARCHITECTURE.md        ← 查技术架构看这个
├── CHANGELOG.md           ← 查历史变更看这个
├── DOCUMENT_INVENTORY.md  ← 查文档索引看这个
├── 管理员账号.md           ← 账号信息
├── 给GPT的项目总结.md      ← AI上下文
│
└── archive/reports/       ← 历史报告归档
    ├── REAL_DATA_*.md (9个)
    ├── COMMERCIAL_*.md (5个)
    ├── IMPORT_*.md (3个)
    └── 其他调研报告 (5个)
```

## 五、维护规范

1. **PROJECT_STATUS.md** — 每次里程碑更新(版本/成熟度/优先级)
2. **DATA_STATUS.md** — 每次数据变更更新(导入/覆盖率变化)
3. **CHANGELOG.md** — 每次发布追加(按版本号)
4. **新报告** — 先写到 archive/reports/，成熟后合并到核心文档
5. **禁止** — 不要再在根目录创建一次性审计/验证/临时报告
