-- 高考志愿填报系统 —— 建表脚本（MySQL）
-- 使用方法：mysql -u root -p gaokao < init.sql

-- ===== 1. 用户表 =====
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  phone VARCHAR(11) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nickname VARCHAR(50),
  is_paid TINYINT DEFAULT 0,
  is_admin TINYINT DEFAULT 0,
  paid_expire_at DATETIME,
  free_check_count INTEGER DEFAULT 0,
  free_assessment_count INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 2. 省份表 =====
CREATE TABLE IF NOT EXISTS provinces (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL UNIQUE,
  code VARCHAR(10) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 3. 一分一段表 =====
CREATE TABLE IF NOT EXISTS score_segments (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  province_id INTEGER NOT NULL,
  year INTEGER NOT NULL,
  score INTEGER NOT NULL,
  `rank` INTEGER NOT NULL,
  subject_type VARCHAR(20) NOT NULL,
  UNIQUE KEY uq_segment (province_id, year, score, subject_type),
  FOREIGN KEY (province_id) REFERENCES provinces(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 4. 院校表 =====
CREATE TABLE IF NOT EXISTS universities (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  province_id INTEGER,
  city VARCHAR(50),
  level VARCHAR(20),
  type VARCHAR(30),
  is_985 TINYINT DEFAULT 0,
  is_211 TINYINT DEFAULT 0,
  is_double_first_class TINYINT DEFAULT 0,
  website VARCHAR(200),
  intro TEXT,
  FOREIGN KEY (province_id) REFERENCES provinces(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 5. 专业表 =====
CREATE TABLE IF NOT EXISTS majors (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  category VARCHAR(30) NOT NULL,
  subcategory VARCHAR(50),
  intro TEXT,
  degree VARCHAR(30),
  duration INTEGER DEFAULT 4
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 6. 录取分数线（核心查询表）=====
CREATE TABLE IF NOT EXISTS admission_scores (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  university_id INTEGER NOT NULL,
  major_id INTEGER,
  province_id INTEGER NOT NULL,
  year INTEGER NOT NULL,
  subject_type VARCHAR(20) NOT NULL,
  batch VARCHAR(30) NOT NULL,
  min_score INTEGER NOT NULL,
  min_rank INTEGER,
  avg_score INTEGER,
  plan_count INTEGER,
  UNIQUE KEY uq_admission (university_id, major_id, province_id, year, subject_type, batch),
  FOREIGN KEY (university_id) REFERENCES universities(id),
  FOREIGN KEY (major_id) REFERENCES majors(id),
  FOREIGN KEY (province_id) REFERENCES provinces(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 7. 专业就业画像 =====
CREATE TABLE IF NOT EXISTS major_profiles (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  major_id INTEGER NOT NULL UNIQUE,
  avg_starting_salary INTEGER,
  employment_rate_3yr DECIMAL(5,2),
  top_industries TEXT,
  top_positions TEXT,
  top_cities TEXT,
  postgrad_rate DECIMAL(5,2),
  holland_code VARCHAR(10),
  data_year INTEGER,
  FOREIGN KEY (major_id) REFERENCES majors(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 8. 专业趋势预测 =====
CREATE TABLE IF NOT EXISTS major_trends (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  major_id INTEGER NOT NULL,
  year_forecast INTEGER NOT NULL,
  demand_trend VARCHAR(20) NOT NULL,
  saturation_level VARCHAR(20) NOT NULL,
  avg_salary_forecast INTEGER,
  confidence VARCHAR(10),
  data_source TEXT,
  summary TEXT,
  UNIQUE KEY uq_trend (major_id, year_forecast),
  FOREIGN KEY (major_id) REFERENCES majors(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 9. 测评题库 =====
CREATE TABLE IF NOT EXISTS assessment_questions (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  question_text TEXT NOT NULL,
  options TEXT NOT NULL,
  dimension VARCHAR(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 10. 用户测评结果 =====
CREATE TABLE IF NOT EXISTS assessment_results (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER NOT NULL,
  result_scores TEXT NOT NULL,
  primary_type VARCHAR(10),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 11. 志愿方案 =====
CREATE TABLE IF NOT EXISTS volunteer_plans (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER NOT NULL,
  province_id INTEGER,
  plan_name VARCHAR(100),
  subject_type VARCHAR(20),
  score INTEGER,
  `rank` INTEGER,
  plans_data TEXT NOT NULL,
  strategy_type VARCHAR(20),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (province_id) REFERENCES provinces(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 12. 支付记录 =====
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  order_no VARCHAR(50) NOT NULL UNIQUE,
  plan VARCHAR(30),
  paid_at DATETIME,
  expire_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== 13. 用户行为统计 =====
CREATE TABLE IF NOT EXISTS analytics_events (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER,
  event_type VARCHAR(50) NOT NULL COMMENT 'page_view/score_input/plan_generate/pay_click/pay_confirm/register/login',
  event_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  score INTEGER COMMENT '分数（如有）',
  `rank` INTEGER COMMENT '位次（如有）',
  device_type VARCHAR(20) COMMENT 'mobile/desktop',
  INDEX idx_event_type (event_type),
  INDEX idx_event_time (event_time),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
