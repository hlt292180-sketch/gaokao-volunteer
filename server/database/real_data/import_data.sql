
-- ===== 备份提示 =====
-- 执行前请先备份：mysqldump -u root -p gaokao > backup_20260604.sql

-- ===== 清空旧数据（保留省份表） =====
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM admission_scores;
DELETE FROM major_trends;
DELETE FROM major_profiles;
DELETE FROM majors;
DELETE FROM universities;
ALTER TABLE universities AUTO_INCREMENT = 1;
ALTER TABLE majors AUTO_INCREMENT = 1;
ALTER TABLE admission_scores AUTO_INCREMENT = 1;
SET FOREIGN_KEY_CHECKS = 1;

-- ===== 导入院校数据 =====
LOAD DATA LOCAL INFILE 'E:/志愿填报/server/database/real_data/universities.csv'
INTO TABLE universities
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(name, province_id, city, level, type,
 is_985, is_211, is_double_first_class,
 website, intro);

-- ===== 导入专业数据 =====
LOAD DATA LOCAL INFILE 'E:/志愿填报/server/database/real_data/majors.csv'
INTO TABLE majors
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(name, category, subcategory, intro, degree, duration);

-- ===== 导入录取分数 =====
LOAD DATA LOCAL INFILE 'E:/志愿填报/server/database/real_data/admission_scores.csv'
INTO TABLE admission_scores
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(university_id, major_id, province_id, year,
 subject_type, batch, min_score, min_rank,
 avg_score, plan_count);
