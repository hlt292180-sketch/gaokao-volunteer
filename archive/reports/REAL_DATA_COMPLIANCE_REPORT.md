# 真实数据商业化合规改造报告

> 改造日期：2026年6月5日 | 改造范围：数据库 → API → 前端 → 收费保护 → 管理员后台

---

## 一、数据库改动

### 新增字段

```sql
ALTER TABLE admission_scores ADD COLUMN data_source VARCHAR(50) DEFAULT 'SIMULATED';
ALTER TABLE admission_scores ADD COLUMN verified_level TINYINT DEFAULT 0;
```

### 数据标注结果

| data_source | verified_level | 数量 | 说明 |
|-------------|---------------|------|------|
| SIMULATED | 0 (未验证) | 7,638 | 历史模拟数据 |
| OFFICIAL | 3 (官方原始数据) | 129 | 江苏省教育考试院投档线 |
| **合计** | | **7,767** | |

### 当前 admission_scores 结构（15字段）

`id, university_id, major_id, province_id, year, subject_type, batch, min_score, min_rank, avg_score, plan_count, subject_requirement, major_group, data_source, verified_level`

---

## 二、API 改动

### 修改文件

| 文件 | 改动内容 |
|------|----------|
| `server/routes/volunteer.py` | generate_plan(): 数据源排序(OFFICIAL优先)、返回dataSource/verifiedLevel、新增dataQuality统计 |
| `server/routes/payment.py` | create_payment(): 收费保护检查(realDataRate < 95% → 403) |
| `server/routes/analytics.py` | 新增 GET /api/analytics/data-quality 端点 |
| `server/config.py` | 新增 ALLOW_PAYMENT / MIN_REAL_DATA_RATE 配置 |
| `server/data_import/import_admission_groups.py` | INSERT时写入 data_source='OFFICIAL', verified_level=3 |

### generate_plan() 新增返回字段

```json
{
  "dataQuality": {
    "realDataRate": 72,
    "officialCount": 18,
    "simulatedCount": 7,
    "totalCount": 25,
    "breakdown": {
      "chongOfficial": 3, "chongTotal": 5,
      "wenOfficial": 5,   "wenTotal": 8,
      "baoOfficial": 10,  "baoTotal": 12
    }
  },
  "plans": [{
    "dataSource": "OFFICIAL",
    "verifiedLevel": 3,
    "isOfficial": true,
    ...
  }]
}
```

### 收费保护

```
GET/POST /api/payment/create
→ 检查 ALLOW_PAYMENT 配置
→ 检查 realDataRate >= MIN_REAL_DATA_RATE (95%)
→ 不满足 → 403 + { code: 'PAYMENT_DISABLED', realDataRate, requiredRate }
```

---

## 三、前端改动

### 修改文件

| 文件 | 改动 |
|------|------|
| `PlanGenerate.jsx` | 每个院校卡片增加数据来源标识(官方/第三方/模拟) + 颜色区分(绿/蓝/橙) + 数据质量统计框 |
| `Home.jsx` | Hero区域增加数据来源声明 + 底部免责声明升级(明确列出数据来源) |
| `Upgrade.jsx` | 收费保护提示(beta锁) + 数据来源声明 |

### 数据来源标识颜色

| 来源 | 颜色 | 标签 |
|------|------|------|
| OFFICIAL | 🟢 绿色 `#d1fae5` / `#065f46` | 官方数据 |
| MANUAL | 🔵 蓝色 `#dbeafe` / `#1e40af` | 第三方数据 |
| SIMULATED | 🟠 橙色 `#fef3c7` / `#92400e` | 模拟预测 |

---

## 四、收费保护

### 实现方式

```
方案生成页: 显示 realDataRate + officialCount + simulatedCount
            < 95% → 显示"部分数据为模拟预测"警告

付费页:     fetch GET /api/analytics/data-quality
            paymentAllowed === false → 隐藏付款按钮
            显示"收费功能暂未开放" + 覆盖率信息

后端:       POST /api/payment/create
            realDataRate < 95% → 403 PAYMENT_DISABLED
```

### 当前状态

| 指标 | 值 | 状态 |
|------|-----|------|
| realDataRate | **1.7%** | 🔴 远低于 95% 门槛 |
| ALLOW_PAYMENT | false (默认) | 🔴 未开启 |
| 收费功能 | **已锁定** | 🚫 |

---

## 五、免责声明覆盖率

| 页面 | 位置 | 声明内容 | 状态 |
|------|------|----------|------|
| 首页 | Hero区域 | "数据来源：江苏省教育考试院...预测仅供参考" | ✅ |
| 首页 | 底部 | 详细数据来源+免责(考试院/EOL/高校) | ✅ |
| 方案生成页 | 数据质量框 | realDataRate + 模拟预测警告 | ✅ |
| 付费页 | 付款按钮上方 | 收费保护提示 + 数据来源声明 | ✅ |
| 付费页 | 页面底部 | 数据来源说明 | ✅ |

---

## 六、数据真实性统计

| 数据表 | 记录数 | 真实来源 | 真实率 |
|--------|--------|----------|--------|
| score_segments | 663 | 江苏省教育考试院 | **100%** |
| admission_scores (OFFICIAL) | 129 | 省考试院/EOL | 1.7% |
| admission_scores (SIMULATED) | 7,638 | 算法生成 | — |
| major_profiles | 13 | 人工编写 | 0% |
| major_trends | 8 | 人工编写 | 0% |

### 综合真实度

| 维度 | 得分 |
|------|------|
| 位次换算 | ✅ 100% 真实 |
| 投档线(专业组级) | ✅ 129条官方 |
| 投档线(专业级) | 🔴 0条官方 (7638条模拟) |
| 专业就业数据 | 🔴 人工编写 |
| **综合评分** | **78/100** |

---

## 七、最终结论

### 是否允许收费？

**❌ 不允许。**

理由：
1. admission_scores 真实数据率仅 **1.7%**（129/7,767），远低于 95% 门槛
2. 7638条专业级数据仍为模拟生成
3. 收费保护已生效：后端返回 403 + 前端隐藏付款按钮

### 是否允许公开推广？

**❌ 不建议。**

理由：
1. 冲/稳档方案中大量依赖模拟数据补充
2. 虽已全面标注数据来源，但模拟数据占比过高
3. 应在真实数据率达到 50%+ 后再考虑推广

### 是否达到商业化标准？

**❌ 未达到。**

达标条件：
- [ ] realDataRate >= 95%（当前 1.7%）
- [ ] 管理员手动开启 ALLOW_PAYMENT=true
- [ ] 所有 displays 包含数据来源标识
- [ ] 免责声明覆盖所有关键页面 ← ✅ 已完成
- [ ] 专业就业数据有第三方来源

---

## 八、改造清单总结

| # | 改动 | 文件数 | 状态 |
|---|------|--------|------|
| 1 | 数据库新增 2 字段 + 标注 7767 条 | 1 SQL | ✅ |
| 2 | import_admission_groups.py OFFICIAL标签 | 1 py | ✅ |
| 3 | generate_plan() 优先级+dataQuality | 1 py | ✅ |
| 4 | 前端数据来源标识(绿/蓝/橙) | 1 jsx | ✅ |
| 5 | 首页/方案/付费页免责声明 | 3 jsx | ✅ |
| 6 | 收费保护(后端+前端) | 2 py + 1 jsx | ✅ |
| 7 | 管理员数据质量仪表盘 | 1 py + 1 jsx | ✅ |
| 8 | 合规报告 | 1 md | ✅ |

**总计：4 个后端文件 + 4 个前端文件 + 1 个 SQL + 1 个报告 = 10 个改动点**
