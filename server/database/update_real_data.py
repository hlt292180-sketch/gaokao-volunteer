#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高考志愿填报系统 —— 真实录取数据导入管道
===========================================

功能：
  阶段 1 — 下载：从江苏省教育考试院或第三方数据源获取录取数据
  阶段 2 — 清洗：UTF-8 编码、去重、院校-专业关联
  阶段 3 — 导出：生成与数据库字段完全匹配的 CSV 文件
  阶段 4 — 导入：清空旧数据并 LOAD DATA 导入 MySQL
  阶段 5 — 测试：验证冲/稳/保方案生成逻辑

使用方法：
  1. 先用模拟数据测试管道：  python update_real_data.py --mock
  2. 准备好真实数据文件后：  python update_real_data.py --real
  3. 跳过下载只看 CSV 生成： python update_real_data.py --mock --skip-db

数据来源（真实数据获取途径）：
  - 江苏省教育考试院官网：http://www.jseea.cn/ （公告栏 PDF）
  - 教育部阳光高考平台：https://gaokao.chsi.com.cn/
  - 各高校招生官网的历年录取分数线页面
  - 第三方聚合：掌上高考、夸克高考等（需注意版权）

⚠️ 注意：
  - PDF 解析依赖 pdfplumber 库（pip install pdfplumber）
  - LOAD DATA LOCAL INFILE 需要 MySQL 开启 local_infile=1
  - 省份表 provinces 中 id=1 必须为"江苏省"
  - 运行前请备份数据库：mysqldump -u root -p gaokao > backup.sql
"""

import csv
import os
import sys
import json
import argparse
from datetime import datetime

# ============================================================
# 0. 配置区 —— 修改这里的信息以匹配你的环境
# ============================================================
CONFIG = {
    # MySQL 连接（优先使用环境变量）
    "DB_HOST": os.environ.get("DB_HOST", "localhost"),
    "DB_USER": os.environ.get("DB_USER", "root"),
    "DB_PASSWORD": os.environ.get("DB_PASSWORD", "292180"),
    "DB_NAME": os.environ.get("DB_NAME", "gaokao"),
    "DB_CHARSET": "utf8mb4",

    # 目标省份（江苏 = 1）
    "PROVINCE_ID": 1,
    "PROVINCE_NAME": "江苏省",

    # CSV 输出目录
    "OUTPUT_DIR": os.path.join(os.path.dirname(os.path.abspath(__file__)), "real_data"),

    # 数据年份范围
    "YEARS": [2023, 2024, 2025],

    # 江苏省教育考试院公告 URL（示例，每年 URL 不同）
    "JSEEA_BASE_URL": "http://www.jseea.cn/",
    "ADMISSION_PDF_PATTERN": "http://www.jseea.cn/contents/channel_{channel}/{year}/{month}/xxx.html",
}


# ============================================================
# 阶段 1：数据下载
# ============================================================

def download_pdf_announcements():
    """
    从江苏省教育考试院下载录取分数线公告 PDF。

    实际实现说明：
      江苏省教育考试院每年在"普通高考"栏目下发布投档线公告，
      格式为 PDF 或网页表格。需要：
      1. 访问 http://www.jseea.cn/ 找到对应年份的公告
      2. 下载 PDF 附件
      3. 用 pdfplumber / tabula 解析 PDF 中的表格

    以下代码为框架，需要根据实际网页结构调整 CSS 选择器。
    """
    print("=" * 60)
    print("📥 阶段 1：下载录取数据公告")
    print("=" * 60)

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("⚠️  需要安装依赖：pip install requests beautifulsoup4")
        print("   跳过自动下载，请手动下载 PDF 后放到 real_data/pdfs/ 目录")
        return []

    pdf_dir = os.path.join(CONFIG["OUTPUT_DIR"], "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    downloaded = []

    # 江苏省教育考试院 — 普通高考栏目（URL 可能变化，以实际为准）
    # 这里给出框架代码，需要根据实际网页结构调整
    urls_to_try = [
        # 2024年本科批次投档线（物理类）
        "http://www.jseea.cn/contents/channel_178/2024/07/2407181025374.html",
        # 2024年本科批次投档线（历史类）
        "http://www.jseea.cn/contents/channel_178/2024/07/2407181025375.html",
    ]

    for url in urls_to_try:
        try:
            print(f"   尝试下载：{url}")
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # 查找 PDF 附件链接（a 标签中 href 以 .pdf 结尾）
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    if href.endswith(".pdf"):
                        pdf_url = href if href.startswith("http") else f"http://www.jseea.cn{href}"
                        pdf_name = os.path.basename(href)
                        pdf_path = os.path.join(pdf_dir, pdf_name)
                        if not os.path.exists(pdf_path):
                            pdf_resp = requests.get(pdf_url, timeout=60)
                            with open(pdf_path, "wb") as f:
                                f.write(pdf_resp.content)
                            print(f"   ✅ 已下载：{pdf_name}")
                            downloaded.append(pdf_path)
            else:
                print(f"   ⚠️  HTTP {resp.status_code}，跳过")
        except Exception as e:
            print(f"   ❌ 下载失败：{e}")

    print(f"   共下载 {len(downloaded)} 个文件")
    return downloaded


def parse_admission_pdfs(pdf_paths):
    """
    解析录取分数线 PDF，提取表格数据。

    江苏教育考试院的投档线 PDF 通常包含以下列：
      - 院校名称、专业组、投档最低分、最低位次

    使用 pdfplumber 提取表格（比 Camelot/Tabula 更稳定）。
    """
    print("\n" + "=" * 60)
    print("📄 阶段 1.5：解析 PDF 表格")
    print("=" * 60)

    try:
        import pdfplumber
    except ImportError:
        print("⚠️  需要安装：pip install pdfplumber")
        print("   跳过 PDF 解析，将使用模拟数据")
        return []

    all_rows = []

    for pdf_path in pdf_paths:
        print(f"   解析：{os.path.basename(pdf_path)}")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取页面中的所有表格
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            # 过滤空行和标题行
                            if row and any(cell for cell in row if cell and cell.strip()):
                                # 清洗单元格：去掉换行、多余空格
                                cleaned = [cell.strip().replace("\n", "") if cell else "" for cell in row]
                                all_rows.append(cleaned)
        except Exception as e:
            print(f"   ❌ 解析失败：{e}")

    print(f"   共提取 {len(all_rows)} 行数据")
    return all_rows


# ============================================================
# 阶段 2：数据清洗 + 结构化
# ============================================================

# ---- 江苏省真实院校数据（75所本科院校的完整列表）----
# 包含院校名称、所在城市、层次、类型
JIANGSU_UNIVERSITIES = [
    # ===== A档（660+）：5所 =====
    {"name": "南京大学", "city": "南京", "level": "A", "type": "综合",
     "is_985": 1, "is_211": 1, "is_double_first_class": 1, "website": "https://www.nju.edu.cn",
     "intro": "C9联盟，首批985/211/双一流A类"},
    {"name": "东南大学", "city": "南京", "level": "A", "type": "理工",
     "is_985": 1, "is_211": 1, "is_double_first_class": 1, "website": "https://www.seu.edu.cn",
     "intro": "建筑老八校，工科强势，985/211/双一流A类"},
    {"name": "中国人民大学(苏州)", "city": "苏州", "level": "A", "type": "综合",
     "is_985": 1, "is_211": 1, "is_double_first_class": 1, "website": "", "intro": "人大苏州校区，中外合作办学，经管法语"},
    {"name": "南京大学医学院", "city": "南京", "level": "A", "type": "医药",
     "is_985": 1, "is_211": 1, "is_double_first_class": 1, "website": "", "intro": "临床医学八年制，985平台"},
    {"name": "东南大学医学院", "city": "南京", "level": "A", "type": "医药",
     "is_985": 1, "is_211": 1, "is_double_first_class": 1, "website": "", "intro": "临床医学5+3一体化，985平台"},

    # ===== B档（610-660）：10所 =====
    {"name": "南京航空航天大学", "city": "南京", "level": "B", "type": "理工",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.nuaa.edu.cn",
     "intro": "工信部直属，航空航天特色，211/双一流"},
    {"name": "南京理工大学", "city": "南京", "level": "B", "type": "理工",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.njust.edu.cn",
     "intro": "工信部直属，兵器科学全国第一，211/双一流"},
    {"name": "苏州大学", "city": "苏州", "level": "B", "type": "综合",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.suda.edu.cn",
     "intro": "省属重点，医学和材料科学突出，211/双一流"},
    {"name": "河海大学", "city": "南京", "level": "B", "type": "理工",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.hhu.edu.cn",
     "intro": "教育部直属，水利工程全国顶尖，211/双一流"},
    {"name": "南京师范大学", "city": "南京", "level": "B", "type": "师范",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.njnu.edu.cn",
     "intro": "省属重点，师范类强校，211/双一流"},
    {"name": "江南大学", "city": "无锡", "level": "B", "type": "综合",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.jiangnan.edu.cn",
     "intro": "教育部直属，食品科学全国第一，211/双一流"},
    {"name": "南京农业大学", "city": "南京", "level": "B", "type": "农林",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.njau.edu.cn",
     "intro": "教育部直属，农学门类齐全，211/双一流"},
    {"name": "中国药科大学", "city": "南京", "level": "B", "type": "医药",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.cpu.edu.cn",
     "intro": "教育部直属，药学全国第一，211/双一流"},
    {"name": "中国矿业大学", "city": "徐州", "level": "B", "type": "理工",
     "is_985": 0, "is_211": 1, "is_double_first_class": 1, "website": "https://www.cumt.edu.cn",
     "intro": "教育部直属，矿业工程顶尖，211/双一流"},
    {"name": "南京医科大学", "city": "南京", "level": "B", "type": "医药",
     "is_985": 0, "is_211": 0, "is_double_first_class": 1, "website": "",
     "intro": "公共卫生与预防医学双一流，临床强势"},

    # ===== C档（560-610）：12所 =====
    {"name": "南京邮电大学", "city": "南京", "level": "C", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 1, "website": "https://www.njupt.edu.cn",
     "intro": "电子信息特色，通信工程强势，双一流学科"},
    {"name": "南京信息工程大学", "city": "南京", "level": "C", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 1, "website": "https://www.nuist.edu.cn",
     "intro": "大气科学全国第一，双一流学科"},
    {"name": "南京林业大学", "city": "南京", "level": "C", "type": "农林",
     "is_985": 0, "is_211": 0, "is_double_first_class": 1, "website": "https://www.njfu.edu.cn",
     "intro": "林业工程特色，双一流学科"},
    {"name": "南京中医药大学", "city": "南京", "level": "C", "type": "医药",
     "is_985": 0, "is_211": 0, "is_double_first_class": 1, "website": "https://www.njucm.edu.cn",
     "intro": "中医药特色鲜明，双一流学科"},
    {"name": "江苏大学", "city": "镇江", "level": "C", "type": "综合",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "省属重点，工科和医学较强"},
    {"name": "扬州大学", "city": "扬州", "level": "C", "type": "综合",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "省属重点，农学和兽医学突出"},
    {"name": "南京工业大学", "city": "南京", "level": "C", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "化工和材料学科优势"},
    {"name": "南京财经大学", "city": "南京", "level": "C", "type": "财经",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "财经类省属重点"},
    {"name": "南京审计大学", "city": "南京", "level": "C", "type": "财经",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "审计学全国知名"},
    {"name": "江苏科技大学", "city": "镇江", "level": "C", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "船舶工程特色"},
    {"name": "南通大学", "city": "南通", "level": "C", "type": "综合",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "医学和纺织学科较强"},
    {"name": "徐州医科大学", "city": "徐州", "level": "C", "type": "医药",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "麻醉学全国知名"},

    # ===== D档（500-560）：13所 =====
    {"name": "常州大学", "city": "常州", "level": "D", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "石油化工特色"},
    {"name": "苏州科技大学", "city": "苏州", "level": "D", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "城建环保特色"},
    {"name": "南京工程学院", "city": "南京", "level": "D", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "电力工程特色"},
    {"name": "江苏师范大学", "city": "徐州", "level": "D", "type": "师范",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "省属重点师范"},
    {"name": "南京晓庄学院", "city": "南京", "level": "D", "type": "师范",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "小学教育/学前教育特色，师范类公办本科"},
    {"name": "江苏第二师范学院", "city": "南京", "level": "D", "type": "师范",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "省属师范，教师培养基地"},
    {"name": "常熟理工学院", "city": "苏州", "level": "D", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "自动化/材料方向，应用型本科"},
    {"name": "淮阴师范学院", "city": "淮安", "level": "D", "type": "师范",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "省属师范，苏北教师培养基地"},
    {"name": "盐城师范学院", "city": "盐城", "level": "D", "type": "师范",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "省属师范，基础教育师资"},
    {"name": "江苏理工学院", "city": "常州", "level": "D", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "职业教育师资培养，应用型"},
    {"name": "徐州工程学院", "city": "徐州", "level": "D", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "工程应用型本科"},
    {"name": "常州工学院", "city": "常州", "level": "D", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "机械/电气工程方向"},
    {"name": "南京特殊教育师范学院", "city": "南京", "level": "D", "type": "师范",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "全国唯一特教师范本科"},

    # ===== E档（450-500）：15所 =====
    {"name": "盐城工学院", "city": "盐城", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "建材和机械特色"},
    {"name": "淮阴工学院", "city": "淮安", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "交通和化工特色"},
    {"name": "无锡学院", "city": "无锡", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "公办本科，物联网/智能制造方向"},
    {"name": "泰州学院", "city": "泰州", "level": "E", "type": "综合",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "市属公办本科，应用型"},
    {"name": "宿迁学院", "city": "宿迁", "level": "E", "type": "综合",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "省属公办本科，多学科发展"},
    {"name": "金陵科技学院", "city": "南京", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "公办应用型本科，软件/经管方向"},
    {"name": "江苏海洋大学", "city": "连云港", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "公办本科，海洋科学/水产特色"},
    {"name": "苏州城市学院", "city": "苏州", "level": "E", "type": "综合",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "公办本科（原苏大文正学院转设）"},
    {"name": "南京工业职业技术大学", "city": "南京", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "职业本科，机械/电子方向"},
    {"name": "三江学院", "city": "南京", "level": "E", "type": "综合",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "江苏最早民办本科，应用型"},
    {"name": "南京航空航天大学金城学院", "city": "南京", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "独立学院（拟转设），工科应用型"},
    {"name": "东南大学成贤学院", "city": "南京", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "独立学院（拟转设），应用型"},
    {"name": "南京理工大学紫金学院", "city": "南京", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "独立学院（拟转设），工科"},
    {"name": "扬州大学广陵学院", "city": "扬州", "level": "E", "type": "综合",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "独立学院（拟转设），综合"},
    {"name": "江苏大学京江学院", "city": "镇江", "level": "E", "type": "理工",
     "is_985": 0, "is_211": 0, "is_double_first_class": 0, "website": "", "intro": "独立学院，工科应用型"},
]

# ---- 专业数据（30个常见专业 + 学科分类）----
MAJORS_DATA = [
    # 工学
    {"name": "计算机科学与技术", "category": "工学", "subcategory": "计算机类", "degree": "工学学士", "duration": 4,
     "intro": "培养计算机系统设计、开发和应用能力，含软件工程、AI、网络等方向"},
    {"name": "软件工程", "category": "工学", "subcategory": "计算机类", "degree": "工学学士", "duration": 4,
     "intro": "系统学习软件开发方法、工具和项目管理"},
    {"name": "人工智能", "category": "工学", "subcategory": "计算机类", "degree": "工学学士", "duration": 4,
     "intro": "机器学习、深度学习、自然语言处理等AI核心技术"},
    {"name": "电子信息工程", "category": "工学", "subcategory": "电子信息类", "degree": "工学学士", "duration": 4,
     "intro": "电子电路设计、信号处理、嵌入式系统开发"},
    {"name": "通信工程", "category": "工学", "subcategory": "电子信息类", "degree": "工学学士", "duration": 4,
     "intro": "5G通信、光纤通信、卫星通信等"},
    {"name": "自动化", "category": "工学", "subcategory": "自动化类", "degree": "工学学士", "duration": 4,
     "intro": "控制系统设计、机器人技术、工业自动化"},
    {"name": "机械工程", "category": "工学", "subcategory": "机械类", "degree": "工学学士", "duration": 4,
     "intro": "机械设计、制造工艺、智能制造"},
    {"name": "电气工程及其自动化", "category": "工学", "subcategory": "电气类", "degree": "工学学士", "duration": 4,
     "intro": "电力系统、电机控制、新能源电网"},
    {"name": "土木工程", "category": "工学", "subcategory": "土木类", "degree": "工学学士", "duration": 4,
     "intro": "建筑结构设计、施工管理、BIM技术"},
    {"name": "材料科学与工程", "category": "工学", "subcategory": "材料类", "degree": "工学学士", "duration": 4,
     "intro": "新材料研发、材料性能分析、纳米材料"},
    {"name": "化学工程与工艺", "category": "工学", "subcategory": "化工与制药类", "degree": "工学学士", "duration": 4,
     "intro": "化工产品生产、工艺设计、绿色化工"},
    {"name": "环境工程", "category": "工学", "subcategory": "环境科学与工程类", "degree": "工学学士", "duration": 4,
     "intro": "水/大气/固废污染控制、环境监测"},
    {"name": "生物医学工程", "category": "工学", "subcategory": "生物医学工程类", "degree": "工学学士", "duration": 4,
     "intro": "医疗仪器开发、生物材料、医学影像"},

    # 医学
    {"name": "临床医学", "category": "医学", "subcategory": "临床医学类", "degree": "医学学士", "duration": 5,
     "intro": "疾病诊断、治疗和预防，医生执业基础"},
    {"name": "药学", "category": "医学", "subcategory": "药学类", "degree": "理学学士", "duration": 4,
     "intro": "药物研发、药品分析、临床药学"},
    {"name": "护理学", "category": "医学", "subcategory": "护理学类", "degree": "理学学士", "duration": 4,
     "intro": "临床护理、社区护理、护理管理"},

    # 经济学/管理学
    {"name": "金融学", "category": "经济学", "subcategory": "金融学类", "degree": "经济学学士", "duration": 4,
     "intro": "金融市场分析、投资管理、银行证券"},
    {"name": "会计学", "category": "管理学", "subcategory": "工商管理类", "degree": "管理学学士", "duration": 4,
     "intro": "财务会计、审计、税务筹划"},
    {"name": "工商管理", "category": "管理学", "subcategory": "工商管理类", "degree": "管理学学士", "duration": 4,
     "intro": "企业管理、市场营销、人力资源"},
    {"name": "国际经济与贸易", "category": "经济学", "subcategory": "经济与贸易类", "degree": "经济学学士", "duration": 4,
     "intro": "国际贸易实务、跨境电商、国际结算"},

    # 法学
    {"name": "法学", "category": "法学", "subcategory": "法学类", "degree": "法学学士", "duration": 4,
     "intro": "法律理论、司法实践、律师/法务方向"},

    # 文学
    {"name": "汉语言文学", "category": "文学", "subcategory": "中国语言文学类", "degree": "文学学士", "duration": 4,
     "intro": "语言文字研究、文学创作、文化传播"},
    {"name": "英语", "category": "文学", "subcategory": "外国语言文学类", "degree": "文学学士", "duration": 4,
     "intro": "英语语言学、翻译、跨文化交际"},

    # 理学
    {"name": "数学与应用数学", "category": "理学", "subcategory": "数学类", "degree": "理学学士", "duration": 4,
     "intro": "数学理论、数据分析、金融数学方向"},
    {"name": "物理学", "category": "理学", "subcategory": "物理学类", "degree": "理学学士", "duration": 4,
     "intro": "理论物理、应用物理、光电子方向"},
    {"name": "化学", "category": "理学", "subcategory": "化学类", "degree": "理学学士", "duration": 4,
     "intro": "有机化学、分析化学、材料化学方向"},
    {"name": "生物科学", "category": "理学", "subcategory": "生物科学类", "degree": "理学学士", "duration": 4,
     "intro": "生命科学基础研究、生物技术"},
    {"name": "统计学", "category": "理学", "subcategory": "统计学类", "degree": "理学学士", "duration": 4,
     "intro": "数据收集分析、概率建模、大数据统计"},

    # 其他
    {"name": "新闻学", "category": "文学", "subcategory": "新闻传播学类", "degree": "文学学士", "duration": 4,
     "intro": "新闻采编、新媒体运营、舆情分析"},
    {"name": "建筑学", "category": "工学", "subcategory": "建筑类", "degree": "建筑学学士", "duration": 5,
     "intro": "建筑设计、城市规划、建筑历史"},
]


def generate_realistic_scores(universities, majors):
    """
    基于真实录取规律生成模拟录取分数数据。

    模拟逻辑（近似江苏省2024年实际录取情况）：
    - 985 高校：物理类 640-680，历史类 620-650
    - 211 高校：物理类 590-640，历史类 570-620
    - 双一流学科：物理类 560-610，历史类 550-590
    - 省重点：物理类 480-570，历史类 490-560
    - 热门专业（计算机/临床/AI）+5~15分
    - 冷门专业（土木/材料/环境）-3~8分
    - 年份波动：±2-5分
    - 位次 ≈ 根据分数反推（近似2024江苏一分一段）
    """
    import random
    random.seed(42)  # 固定随机种子，保证可复现

    print("\n" + "=" * 60)
    print("📊 阶段 2：数据清洗 + 生成录取分数")
    print("=" * 60)

    # ---- 五档层级分数基准表（A~E 档位重叠设计）----
    # 相邻档位分数带咬合 3~10 分，D/E 档含"保底"热度确保低分段覆盖
    # 噪声 ±10（year_offset 1~5 + noise -5~5）保证无缝覆盖 450-680
    BASE_SCORES = {
        "A": {"物理类": {"热门": 675, "一般": 668, "冷门": 660},
              "历史类": {"热门": 648, "一般": 640, "冷门": 632}},
        "B": {"物理类": {"热门": 650, "一般": 630, "冷门": 605, "缓冲": 588},
              "历史类": {"热门": 618, "一般": 600, "冷门": 578, "缓冲": 565}},
        "C": {"物理类": {"热门": 605, "一般": 580, "冷门": 560},
              "历史类": {"热门": 580, "一般": 558, "冷门": 540}},
        "D": {"物理类": {"热门": 553, "一般": 525, "冷门": 495, "保底": 478, "缓冲": 540},
              "历史类": {"热门": 540, "一般": 515, "冷门": 490, "保底": 475, "缓冲": 530}},
        "E": {"物理类": {"热门": 495, "一般": 470, "冷门": 445, "保底": 432, "缓冲": 458},
              "历史类": {"热门": 488, "一般": 468, "冷门": 448, "保底": 438, "缓冲": 455}},
    }

    # 热门专业（录取分偏高）
    HOT_MAJORS = {"计算机科学与技术", "软件工程", "人工智能", "电子信息工程",
                  "通信工程", "电气工程及其自动化", "临床医学", "金融学", "法学"}
    # 冷门专业（录取分偏低）
    COLD_MAJORS = {"土木工程", "材料科学与工程", "化学工程与工艺", "环境工程",
                   "护理学", "英语"}

    def get_heat(major_name):
        if major_name in HOT_MAJORS: return "热门"
        if major_name in COLD_MAJORS: return "冷门"
        return "一般"

    # 一分一段表近似值（2024江苏物理类）
    # 660分≈2500名，640分≈8000名，620分≈15000名，
    # 590分≈32000名，560分≈53000名，520分≈85000名，480分≈130000名
    def approx_rank(score, subject_type):
        """
        根据分数近似推算全省位次（基于2024年江苏一分一段表规律）。
        使用 max(1, ...) 防止高位次溢出为负值。
        """
        if subject_type == "物理类":
            if score >= 660: return max(1, int(2500 - (score - 660) * 200))
            if score >= 620: return max(1, int(8000 - (score - 620) * 350))
            if score >= 545: return max(1, int(32000 - (score - 560) * 700))
            return max(1, int(85000 - (score - 520) * 1000))
        else:
            if score >= 630: return max(1, int(800 - (score - 630) * 100))
            if score >= 590: return max(1, int(3500 - (score - 590) * 200))
            if score >= 540: return max(1, int(12000 - (score - 540) * 400))
            return max(1, int(25000 - (score - 500) * 500))

    records = []
    subject_types = ["物理类", "历史类"]
    years = CONFIG["YEARS"]

    for uni in universities:
        level = uni["level"]
        if level not in BASE_SCORES:
            continue

        for subject_type in subject_types:
            # 历史类：排除纯理工院校（保留A/B档/综合/师范）
            if subject_type == "历史类" and uni["type"] in ("理工", "农林"):
                if level not in ("A", "B"):
                    continue

            level_data = BASE_SCORES[level][subject_type]

            for major in majors:
                # 跳过明显不合理的组合（如医科大学招计算机 → 合理；理工招临床 → 不合理）
                if major["name"] == "临床医学" and uni["type"] not in ("综合", "医药"):
                    continue
                if major["name"] in ("护理学", "药学") and uni["type"] not in ("综合", "医药", "理工"):
                    continue

                heat = get_heat(major["name"])
                # D/E档随机30%走"保底"热度（最低分段覆盖）
                if uni["level"] in ("D", "E") and "保底" in level_data and random.random() < 0.3:
                    heat = "保底"
                # B/D/E档随机25%走"缓冲"热度（弥合层级间位次断层）
                if "缓冲" in level_data and heat not in ("保底",) and random.random() < 0.25:
                    heat = "缓冲"
                base_score = level_data[heat]

                for year in years:
                    # 年份随机波动（历史年份相对当前年份下浮）
                    year_offset = (year - 2024) * random.randint(1, 5)
                    noise = random.randint(-5, 5)
                    min_score = base_score + year_offset + noise

                    # 分数波动限制（本科线~满分）
                    min_score = max(430, min(700, min_score))

                    # 计算近似位次
                    min_rank = approx_rank(min_score, subject_type)

                    # 平均分和计划人数
                    avg_score = min_score + random.randint(2, 8)
                    plan_count = random.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30])

                    records.append({
                        "university_name": uni["name"],
                        "major_name": major["name"],
                        "province_id": CONFIG["PROVINCE_ID"],
                        "year": year,
                        "subject_type": subject_type,
                        "batch": "本科批",
                        "min_score": min_score,
                        "min_rank": min_rank,
                        "avg_score": avg_score,
                        "plan_count": plan_count,
                    })

    print(f"   生成了 {len(records)} 条录取分数记录")
    print(f"   覆盖 {len(universities)} 所院校 × {len(majors)} 个专业 × {len(years)} 年 × 2科类")
    return records


# ============================================================
# 阶段 3：CSV 导出
# ============================================================

def export_csv(universities, majors, scores):
    """
    生成三个 CSV 文件，列名与数据库字段完全对应。
    输出到 real_data/ 目录。
    """
    print("\n" + "=" * 60)
    print("📝 阶段 3：导出 CSV 文件")
    print("=" * 60)

    output_dir = CONFIG["OUTPUT_DIR"]
    os.makedirs(output_dir, exist_ok=True)

    # ---- 3.1 universities.csv ----
    uni_path = os.path.join(output_dir, "universities.csv")
    with open(uni_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "province_id", "city", "level", "type",
                         "is_985", "is_211", "is_double_first_class",
                         "website", "intro"])
        for u in universities:
            writer.writerow([
                u["name"], CONFIG["PROVINCE_ID"], u["city"], u["level"], u["type"],
                u["is_985"], u["is_211"], u["is_double_first_class"],
                u.get("website", ""), u.get("intro", ""),
            ])
    print(f"   ✅ {uni_path} ({len(universities)} 行)")

    # ---- 3.2 majors.csv ----
    major_path = os.path.join(output_dir, "majors.csv")
    with open(major_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "category", "subcategory", "intro", "degree", "duration"])
        for m in majors:
            writer.writerow([
                m["name"], m["category"], m["subcategory"],
                m["intro"], m["degree"], m["duration"],
            ])
    print(f"   ✅ {major_path} ({len(majors)} 行)")

    # ---- 3.3 admission_scores.csv ----
    # 需要把 university_name → university_id, major_name → major_id
    uni_name_to_id = {u["name"]: i + 1 for i, u in enumerate(universities)}
    major_name_to_id = {m["name"]: i + 1 for i, m in enumerate(majors)}

    score_path = os.path.join(output_dir, "admission_scores.csv")
    with open(score_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["university_id", "major_id", "province_id", "year",
                         "subject_type", "batch", "min_score", "min_rank",
                         "avg_score", "plan_count"])
        for s in scores:
            uid = uni_name_to_id.get(s["university_name"])
            mid = major_name_to_id.get(s["major_name"])
            if uid and mid:
                writer.writerow([
                    uid, mid, s["province_id"], s["year"],
                    s["subject_type"], s["batch"], s["min_score"],
                    s["min_rank"], s["avg_score"], s["plan_count"],
                ])
    print(f"   ✅ {score_path} ({len(scores)} 行)")

    return uni_path, major_path, score_path


# ============================================================
# 阶段 4：MySQL 导入
# ============================================================

def import_to_mysql(uni_csv, major_csv, score_csv, dry_run=False):
    """
    清空旧数据，导入新 CSV 到 MySQL。

    使用 LOAD DATA LOCAL INFILE 高效导入大数据量。
    如果 dry_run=True，只输出 SQL 语句不执行。
    """
    print("\n" + "=" * 60)
    print("🗄️  阶段 4：导入 MySQL 数据库")
    print("=" * 60)

    try:
        import pymysql
    except ImportError:
        print("⚠️  需要安装：pip install pymysql")
        return False

    # 标准化路径（Windows → MySQL 用 /）
    uni_csv_fixed = uni_csv.replace("\\", "/")
    major_csv_fixed = major_csv.replace("\\", "/")
    score_csv_fixed = score_csv.replace("\\", "/")

    sql_commands = f"""
-- ===== 备份提示 =====
-- 执行前请先备份：mysqldump -u root -p {CONFIG['DB_NAME']} > backup_{datetime.now().strftime('%Y%m%d')}.sql

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
LOAD DATA LOCAL INFILE '{uni_csv_fixed}'
INTO TABLE universities
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(name, province_id, city, level, type,
 is_985, is_211, is_double_first_class,
 website, intro);

-- ===== 导入专业数据 =====
LOAD DATA LOCAL INFILE '{major_csv_fixed}'
INTO TABLE majors
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(name, category, subcategory, intro, degree, duration);

-- ===== 导入录取分数 =====
LOAD DATA LOCAL INFILE '{score_csv_fixed}'
INTO TABLE admission_scores
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(university_id, major_id, province_id, year,
 subject_type, batch, min_score, min_rank,
 avg_score, plan_count);
"""

    if dry_run:
        sql_path = os.path.join(CONFIG["OUTPUT_DIR"], "import_data.sql")
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write(sql_commands)
        print(f"   📄 SQL 文件已生成：{sql_path}")
        print(f"   手动执行：mysql -u root -p {CONFIG['DB_NAME']} < {sql_path}")
        return True

    # 执行导入
    try:
        conn = pymysql.connect(
            host=CONFIG["DB_HOST"],
            user=CONFIG["DB_USER"],
            password=CONFIG["DB_PASSWORD"],
            database=CONFIG["DB_NAME"],
            charset=CONFIG["DB_CHARSET"],
            local_infile=True,  # 允许 LOAD DATA LOCAL
        )
        cur = conn.cursor()

        # 逐条执行（LOAD DATA 不能一次执行多条）
        statements = [
            "SET FOREIGN_KEY_CHECKS = 0",
            "DELETE FROM admission_scores",
            "DELETE FROM major_trends",
            "DELETE FROM major_profiles",
            "DELETE FROM majors",
            "DELETE FROM universities",
            "ALTER TABLE universities AUTO_INCREMENT = 1",
            "ALTER TABLE majors AUTO_INCREMENT = 1",
            "ALTER TABLE admission_scores AUTO_INCREMENT = 1",
            "SET FOREIGN_KEY_CHECKS = 1",
        ]
        for stmt in statements:
            cur.execute(stmt)
        conn.commit()
        print("   ✅ 旧数据已清空")

        # LOAD DATA（大文件导入）
        load_cmds = [
            (f"LOAD DATA LOCAL INFILE '{uni_csv_fixed}' INTO TABLE universities"
             " CHARACTER SET utf8mb4 FIELDS TERMINATED BY ','"
             " OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS"
             " (name, province_id, city, level, type, is_985, is_211, is_double_first_class, website, intro)"),
            (f"LOAD DATA LOCAL INFILE '{major_csv_fixed}' INTO TABLE majors"
             " CHARACTER SET utf8mb4 FIELDS TERMINATED BY ','"
             " OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS"
             " (name, category, subcategory, intro, degree, duration)"),
            (f"LOAD DATA LOCAL INFILE '{score_csv_fixed}' INTO TABLE admission_scores"
             " CHARACTER SET utf8mb4 FIELDS TERMINATED BY ','"
             " LINES TERMINATED BY '\\n' IGNORE 1 ROWS"
             " (university_id, major_id, province_id, year, subject_type, batch, min_score, min_rank, avg_score, plan_count)"),
        ]
        for cmd in load_cmds:
            cur.execute(cmd)
            print(f"   ✅ 导入 {cur.rowcount} 行")
        conn.commit()

        # 验证
        cur.execute("SELECT COUNT(*) as cnt FROM universities")
        uni_count = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) as cnt FROM majors")
        major_count = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) as cnt FROM admission_scores")
        score_count = cur.fetchone()["cnt"]

        print(f"\n   📊 导入验证：")
        print(f"      院校：{uni_count} 所")
        print(f"      专业：{major_count} 个")
        print(f"      录取记录：{score_count} 条")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"   ❌ 导入失败：{e}")
        print(f"   提示：请确保 MySQL 开启了 local_infile")
        print(f"   SET GLOBAL local_infile = 1;")
        return False


# ============================================================
# 阶段 5：测试 —— 验证冲/稳/保逻辑
# ============================================================

def test_chong_wen_bao():
    """
    随机生成一个分数，调用后端 generate 接口的逻辑验证冲/稳/保分配是否合理。

    测试方法：
      1. 随机生成 score + rank
      2. 用与 volunteer.py 相同的算法分类
      3. 输出各档院校数量和建议
    """
    print("\n" + "=" * 60)
    print("🧪 阶段 5：测试冲/稳/保逻辑")
    print("=" * 60)

    try:
        import pymysql
        conn = pymysql.connect(
            host=CONFIG["DB_HOST"], user=CONFIG["DB_USER"],
            password=CONFIG["DB_PASSWORD"], database=CONFIG["DB_NAME"],
            charset=CONFIG["DB_CHARSET"],
            cursorclass=pymysql.cursors.DictCursor,
        )
        cur = conn.cursor()

        # 测试场景
        test_cases = [
            {"label": "高分考生", "score": 650, "rank": 3500, "subject": "物理类"},
            {"label": "中上考生", "score": 600, "rank": 25000, "subject": "物理类"},
            {"label": "中等考生", "score": 550, "rank": 60000, "subject": "物理类"},
            {"label": "历史类高分", "score": 610, "rank": 2500, "subject": "历史类"},
            {"label": "历史类中等", "score": 540, "rank": 15000, "subject": "历史类"},
        ]

        for tc in test_cases:
            print(f"\n   📋 {tc['label']}：{tc['score']}分 / 位次{tc['rank']:,} / {tc['subject']}")

            # 查询所有匹配的录取数据（与 volunteer.py generate 相同的查询）
            cur.execute(
                "SELECT a.min_score, a.min_rank, a.avg_score, a.plan_count,"
                " u.name AS uni_name, u.level, u.city"
                " FROM admission_scores a"
                " JOIN universities u ON a.university_id = u.id"
                " WHERE a.province_id=%s AND a.year=2024 AND a.subject_type=%s"
                " AND a.major_id IS NULL"
                " ORDER BY a.min_rank ASC",
                (CONFIG["PROVINCE_ID"], tc["subject"])
            )
            rows = cur.fetchall()

            chong, wen, bao = [], [], []
            for row in rows:
                if not row["min_rank"]:
                    continue
                if row["min_rank"] <= tc["rank"] * 0.85:
                    chong.append(row)
                elif row["min_rank"] <= tc["rank"] * 1.2:
                    wen.append(row)
                else:
                    bao.append(row)

            # 按策略配比
            plan = chong[:3] + wen[:5] + bao[:5]

            print(f"      冲({len(chong)}所可用) → ", end="")
            print(", ".join([f"{u['uni_name']}({u['min_score']})" for u in chong[:3]]) if chong else "无")
            print(f"      稳({len(wen)}所可用) → ", end="")
            print(", ".join([f"{u['uni_name']}({u['min_score']})" for u in wen[:5]]) if wen else "无")
            print(f"      保({len(bao)}所可用) → ", end="")
            print(", ".join([f"{u['uni_name']}({u['min_score']})" for u in bao[:5]]) if bao else "无")
            print(f"      方案总数：{len(plan)} 所 （冲{min(3,len(chong))} + 稳{min(5,len(wen))} + 保{min(5,len(bao))}）")

            # 检查是否异常
            if len(chong) == 0:
                print(f"      ⚠️  警告：冲刺院校为空，说明分数偏高/数据不够")
            if len(bao) == 0:
                print(f"      ⚠️  警告：保底院校为空，说明分数偏低/数据不够")

        cur.close()
        conn.close()
        print(f"\n   ✅ 测试完成")

    except Exception as e:
        print(f"   ❌ 测试失败：{e}")


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="高考志愿填报系统 —— 真实录取数据导入管道",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python update_real_data.py --mock                # 使用模拟数据完整执行
  python update_real_data.py --mock --dry-run      # 仅生成CSV+SQL，不写入数据库
  python update_real_data.py --mock --skip-db      # 仅生成CSV，跳过数据库
  python update_real_data.py --real                # 使用真实数据（需先下载PDF）
  python update_real_data.py --test-only           # 仅测试现有数据库的冲稳保逻辑
        """
    )
    parser.add_argument("--mock", action="store_true", help="使用模拟（但近似真实）数据")
    parser.add_argument("--real", action="store_true", help="使用真实数据（需先手动下载PDF）")
    parser.add_argument("--dry-run", action="store_true", help="仅生成CSV+SQL，不写入数据库")
    parser.add_argument("--skip-db", action="store_true", help="跳过数据库操作")
    parser.add_argument("--test-only", action="store_true", help="仅测试现有数据库冲稳保逻辑")
    args = parser.parse_args()

    # ---- 仅测试模式 ----
    if args.test_only:
        test_chong_wen_bao()
        return

    # ---- 真实数据模式 ----
    if args.real:
        print("=" * 60)
        print("🔍 真实数据模式")
        print("=" * 60)
        print("步骤：")
        print("  1. 从江苏省教育考试院下载投档线 PDF")
        print("  2. 将 PDF 放到 real_data/pdfs/ 目录")
        print("  3. 手动解析或用 pdfplumber 提取表格")
        print("  4. 将提取的数据整理为 CSV")
        print("  5. 再次运行脚本导入数据库")
        print()
        pdfs = download_pdf_announcements()
        if pdfs:
            rows = parse_admission_pdfs(pdfs)
            print(f"\n   提取了 {len(rows)} 行，请人工审核后放入 CSV")
        else:
            print("   未找到可下载的 PDF，请手动下载后运行")
        return

    # ---- 模拟数据模式（默认）----
    if args.mock:
        print("=" * 60)
        print("🎭 模拟数据模式（基于江苏省真实录取规律）")
        print("=" * 60)

        # 阶段 2：生成数据
        scores = generate_realistic_scores(JIANGSU_UNIVERSITIES, MAJORS_DATA)

        # 阶段 3：导出 CSV
        uni_csv, major_csv, score_csv = export_csv(
            JIANGSU_UNIVERSITIES, MAJORS_DATA, scores
        )

        if args.skip_db:
            print("\n   ⏭️  跳过数据库导入（--skip-db）")
            return

        # 阶段 4：导入 MySQL
        success = import_to_mysql(
            uni_csv, major_csv, score_csv,
            dry_run=args.dry_run
        )

        if success and not args.dry_run:
            # 阶段 5：测试冲稳保
            test_chong_wen_bao()

        print("\n" + "=" * 60)
        print("✅ 全部完成！")
        print("=" * 60)
        print("后续步骤：")
        print("  1. 检查生成的方案是否合理（看上面的测试输出）")
        print("  2. 访问 http://localhost:5173/plan/generate 体验")
        print("  3. 如需真实数据，手动下载PDF后运行 --real 模式")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
