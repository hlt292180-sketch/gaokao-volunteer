# 数据库运维手册

> 最后更新：2026年6月5日

## 一、当前数据库快照

| 表名 | 行数 | 说明 |
|------|------|------|
| universities | 55 | A-E五档院校 |
| majors | 30 | 七大学科门类 |
| admission_scores | 7,638 | 3年×2科类×55校×30专业 |
| score_segments | 162 | 一分一段表 |
| major_profiles | **13** ✅ | 6月5日恢复 | 就业画像种子数据 |
| major_trends | **8** ✅ | 6月5日恢复 | 趋势预测种子数据 |
| users | 3 | 测试用户 |
| payments | 3 | 测试支付 |
| volunteer_plans | 51 | 测试方案(上线前清理) |

## 二、备份文件

| 文件 | 日期 | 大小 | 用途 |
|------|------|------|------|
| `real_data/backup_20260605.sql` | 6月5日 | 23KB | 导入前旧数据(34校/107条) |
| `real_data/backup_20260604_193213.sql` | 6月5日 | 474KB | **当前最新备份(55校/7638条)** |
| `real_data/universities.csv` | 6月5日 | 5KB | 55所院校 |
| `real_data/majors.csv` | 6月5日 | 3KB | 30个专业 |
| `real_data/admission_scores.csv` | 6月5日 | 376KB | 7,638条录取分数 |
| `real_data/import_data.sql` | 6月5日 | 1.5KB | 导入SQL脚本 |

## 三、MySQL 环境

```
版本:    MySQL 8.0.37 Community Server
用户:    root@localhost
权限:    ALL PRIVILEGES + SYSTEM_VARIABLES_ADMIN
数据库:  gaokao
字符集:  utf8mb4
```

### local_infile 状态

```
当前: ON  ⚠️ 生产环境应设为 OFF
命令: SET GLOBAL local_infile = 0
```

## 四、恢复流程

### 恢复最新备份

```bash
# 1. 确认备份文件
ls -la e:/志愿填报/server/database/real_data/backup_*.sql

# 2. 恢复
mysql -u root -p292180 gaokao < e:/志愿填报/server/database/real_data/backup_20260604_193213.sql

# 3. 验证
mysql -u root -p292180 gaokao -e "SELECT COUNT(*) FROM universities; SELECT COUNT(*) FROM admission_scores"
```

### 从 CSV 重建

```bash
cd e:/志愿填报/server/database
SET GLOBAL local_infile = 1
python update_real_data.py --mock --dry-run   # 生成 SQL
mysql -u root -p292180 --local-infile=1 gaokao < real_data/import_data.sql
SET GLOBAL local_infile = 0
```

## 五、数据修复

### major_profiles / major_trends 恢复

**已执行（2026-06-05）：**

```bash
# 1. 从旧备份提取种子数据
# backup_20260605.sql → restore_profiles_trends.sql (13 profiles + 8 trends)

# 2. 校验外键完整性
# major_profiles: major_id 1-13 → majors.id 全部匹配 ✅
# major_trends:   major_id 1-8  → majors.id 全部匹配 ✅

# 3. 导入
mysql -u root -p292180 gaokao < real_data/restore_profiles_trends.sql

# 4. 验证
# major_profiles: 13行 ✅  major_trends: 8行 ✅  孤儿记录: 0 ✅
# 趋势API测试: majors/1 计算机 ✅  majors/3 人工智能 ✅  majors/7 机械 ✅
```

**如需重新恢复：**
```bash
cd e:/志愿填报/server/database
mysql -u root -p292180 gaokao < real_data/restore_profiles_trends.sql
```

## 六、上线前检查清单

- [ ] `SET GLOBAL local_infile = 0`
- [ ] 清理测试 volunteer_plans、payments
- [ ] 恢复 major_profiles、major_trends 种子数据
- [ ] 创建最新 mysqldump 备份
- [ ] 修改 config.py 密码为强密码
- [ ] 修改 JWT_SECRET 为随机字符串
