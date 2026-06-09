-- ============================================================
-- 数据库兼容改造 V1（最小改动方案）
-- 目标：在 admission_scores 表增加 2 个字段
--       不影响现有API、方案生成、前端展示
-- 日期：2026年6月5日
-- ============================================================

-- ⚠️ 执行前请备份数据库！
-- mysqldump -u root -p292180 gaokao > gaokao_backup_$(date +%Y%m%d).sql

USE gaokao;

-- ============================================================
-- 第一步：新增字段（带默认值，兼容现有数据）
-- ============================================================

-- subject_requirement: 选科要求，如"不限"、"化学"、"化学+生物"
ALTER TABLE admission_scores
  ADD COLUMN subject_requirement VARCHAR(50) DEFAULT ''
  COMMENT '选科要求：不限/化学/化学+生物/化学(中外合作)等'
  AFTER plan_count;

-- major_group: 专业组代号，如"07专业组"、"08专业组"
ALTER TABLE admission_scores
  ADD COLUMN major_group VARCHAR(50) DEFAULT ''
  COMMENT '专业组代号：07专业组/08专业组等'
  AFTER subject_requirement;

-- ============================================================
-- 第二步：为现有模拟数据填充默认值
-- ============================================================

-- 现有模拟数据没有选科要求和专业组概念
-- 填充为''（空字符串）表示"模拟数据，无此信息"
-- 如果之前已经添加过字段，使用 UPDATE 而非 ALTER

UPDATE admission_scores
SET subject_requirement = '', major_group = ''
WHERE subject_requirement IS NULL OR major_group IS NULL;

-- ============================================================
-- 第三步：验证
-- ============================================================

-- 验证字段已添加
-- DESCRIBE admission_scores;
-- 预期输出：包含 subject_requirement VARCHAR(50) 和 major_group VARCHAR(50)

-- 验证现有数据未被破坏
-- SELECT COUNT(*) FROM admission_scores;
-- 预期输出：7638

-- 验证不影响现有查询
-- SELECT COUNT(*) FROM admission_scores WHERE min_score > 600;
-- 预期输出：与原结果一致

-- ============================================================
-- 第四步（可选）：导入真实数据后的索引优化
-- ============================================================

-- 真实数据导入后，建议添加以下索引以加速查询：
-- ALTER TABLE admission_scores ADD INDEX idx_group (major_group);
-- ALTER TABLE admission_scores ADD INDEX idx_subject_req (subject_requirement);

-- ============================================================
-- 回滚方案（如需撤销）
-- ============================================================

-- ALTER TABLE admission_scores DROP COLUMN subject_requirement;
-- ALTER TABLE admission_scores DROP COLUMN major_group;

-- ============================================================
-- 兼容性说明
-- ============================================================

-- 1. 现有 API 兼容：
--    - 所有 SELECT 查询不受影响（新增字段在末尾，不影响列顺序）
--    - volunteer.py generate_plan 的 SQL 不引用新字段，不会报错
--    - university.py 的 GROUP BY 聚合不引用新字段，不会报错
--
-- 2. 前端兼容：
--    - 前端不展示新字段，无 UI 变化
--    - API 返回的 JSON 可能包含空字符串字段，前端应能容错
--
-- 3. 方案生成兼容：
--    - 冲/稳/保算法不依赖新字段，结果不变
--    - 真实数据导入后，需更新算法以利用专业组信息
