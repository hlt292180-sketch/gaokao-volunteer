mysqldump: [Warning] Using a password on the command line interface can be insecure.
-- MySQL dump 10.13  Distrib 8.0.37, for Win64 (x86_64)
--
-- Host: localhost    Database: gaokao
-- ------------------------------------------------------
-- Server version	8.0.37

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `universities`
--

DROP TABLE IF EXISTS `universities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `universities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `province_id` int DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `level` varchar(20) DEFAULT NULL,
  `type` varchar(30) DEFAULT NULL,
  `is_985` tinyint DEFAULT '0',
  `is_211` tinyint DEFAULT '0',
  `is_double_first_class` tinyint DEFAULT '0',
  `website` varchar(200) DEFAULT NULL,
  `intro` text,
  PRIMARY KEY (`id`),
  KEY `province_id` (`province_id`),
  CONSTRAINT `universities_ibfk_1` FOREIGN KEY (`province_id`) REFERENCES `provinces` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `universities`
--

LOCK TABLES `universities` WRITE;
/*!40000 ALTER TABLE `universities` DISABLE KEYS */;
INSERT INTO `universities` VALUES (1,'南京大学',1,'南京','本科','综合',1,1,1,NULL,'C9联盟成员，华东五校，天文学/地质学全国第一。'),(2,'东南大学',1,'南京','本科','理工',1,1,1,NULL,'建筑老八校，电子/信息/生物医学工程突出。'),(3,'南京航空航天大学',1,'南京','本科','理工',0,1,1,NULL,'航空航天特色。'),(4,'南京理工大学',1,'南京','本科','理工',0,1,1,NULL,'国防七子之一，兵器科学/光学突出。'),(5,'河海大学',1,'南京','本科','理工',0,1,1,NULL,'水利工程全国第一。'),(6,'南京师范大学',1,'南京','本科','师范',0,1,1,NULL,'211师范，地理学/教育学突出。'),(7,'苏州大学',1,'苏州','本科','综合',0,1,1,NULL,'发展迅猛的211，材料/医学进步显著。'),(8,'江南大学',1,'无锡','本科','综合',0,1,1,NULL,'食品科学全国第一。'),(9,'中国矿业大学',1,'徐州','本科','理工',0,1,1,NULL,'矿业工程全国顶尖。'),(10,'中国药科大学',1,'南京','本科','医药',0,1,1,NULL,'药学最高学府。'),(11,'南京农业大学',1,'南京','本科','农林',0,1,1,NULL,'农业资源/作物学全国领先。'),(12,'南京邮电大学',1,'南京','本科','理工',0,0,1,NULL,'双一流，通信/计算机优势。'),(13,'南京信息工程大学',1,'南京','本科','理工',0,0,1,NULL,'双一流，大气科学全国第一。'),(14,'南京林业大学',1,'南京','本科','农林',0,0,1,NULL,'双一流，林学/风景园林。'),(15,'南京医科大学',1,'南京','本科','医药',0,0,1,NULL,'双一流，公共卫生全国领先。'),(16,'南京工业大学',1,'南京','本科','理工',0,0,0,NULL,'化工/材料/安全工程较强。'),(17,'江苏大学',1,'镇江','本科','综合',0,0,0,NULL,'农机特色省重点。'),(18,'扬州大学',1,'扬州','本科','综合',0,0,0,NULL,'农学/兽医学特色。'),(19,'南通大学',1,'南通','本科','综合',0,0,0,NULL,'医学/纺织特色。'),(20,'常州大学',1,'常州','本科','理工',0,0,0,NULL,'化工/材料优势。'),(21,'清华大学',NULL,'北京','本科','综合',1,1,1,NULL,'中国顶尖工科。'),(22,'北京大学',NULL,'北京','本科','综合',1,1,1,NULL,'中国最著名学府。'),(23,'复旦大学',NULL,'上海','本科','综合',1,1,1,NULL,'华东五校，文理医管强。'),(24,'上海交通大学',NULL,'上海','本科','综合',1,1,1,NULL,'工科医学突出。'),(25,'浙江大学',NULL,'杭州','本科','综合',1,1,1,NULL,'学科门类齐全。'),(26,'中国科学技术大学',NULL,'合肥','本科','理工',1,1,1,NULL,'C9，量子信息世界领先。'),(27,'武汉大学',NULL,'武汉','本科','综合',1,1,1,NULL,'最美校园，测绘/法学强。'),(28,'华中科技大学',NULL,'武汉','本科','理工',1,1,1,NULL,'工科医学强势。'),(29,'同济大学',NULL,'上海','本科','理工',1,1,1,NULL,'土木建筑全国第一。'),(30,'北京航空航天大学',NULL,'北京','本科','理工',1,1,1,NULL,'航空航天翘楚。'),(31,'中国人民大学',NULL,'北京','本科','综合',1,1,1,NULL,'人文社科最高学府。'),(32,'哈尔滨工业大学',NULL,'哈尔滨','本科','理工',1,1,1,NULL,'C9，航天/机器人强。'),(33,'西安交通大学',NULL,'西安','本科','综合',1,1,1,NULL,'C9，电气/能动顶尖。'),(34,'南开大学',NULL,'天津','本科','综合',1,1,1,NULL,'文理基础扎实。');
/*!40000 ALTER TABLE `universities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admission_scores`
--

DROP TABLE IF EXISTS `admission_scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admission_scores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `university_id` int NOT NULL,
  `major_id` int DEFAULT NULL,
  `province_id` int NOT NULL,
  `year` int NOT NULL,
  `subject_type` varchar(20) NOT NULL,
  `batch` varchar(30) NOT NULL,
  `min_score` int NOT NULL,
  `min_rank` int DEFAULT NULL,
  `avg_score` int DEFAULT NULL,
  `plan_count` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_admission` (`university_id`,`major_id`,`province_id`,`year`,`subject_type`,`batch`),
  KEY `major_id` (`major_id`),
  KEY `province_id` (`province_id`),
  CONSTRAINT `admission_scores_ibfk_1` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`),
  CONSTRAINT `admission_scores_ibfk_2` FOREIGN KEY (`major_id`) REFERENCES `majors` (`id`),
  CONSTRAINT `admission_scores_ibfk_3` FOREIGN KEY (`province_id`) REFERENCES `provinces` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admission_scores`
--

LOCK TABLES `admission_scores` WRITE;
/*!40000 ALTER TABLE `admission_scores` DISABLE KEYS */;
INSERT INTO `admission_scores` VALUES (1,1,NULL,1,2025,'物理类','本科批',672,520,678,220),(2,1,NULL,1,2024,'物理类','本科批',670,580,676,210),(3,1,NULL,1,2023,'物理类','本科批',671,540,677,215),(4,2,NULL,1,2025,'物理类','本科批',662,1100,669,280),(5,2,NULL,1,2024,'物理类','本科批',664,950,671,270),(6,2,NULL,1,2023,'物理类','本科批',663,1020,670,275),(7,3,NULL,1,2025,'物理类','本科批',642,3600,650,350),(8,3,NULL,1,2024,'物理类','本科批',644,3200,652,340),(9,3,NULL,1,2023,'物理类','本科批',643,3400,651,345),(10,4,NULL,1,2025,'物理类','本科批',638,4300,646,330),(11,4,NULL,1,2024,'物理类','本科批',640,3900,648,320),(12,4,NULL,1,2023,'物理类','本科批',639,4100,647,325),(13,5,NULL,1,2025,'物理类','本科批',626,7100,634,400),(14,5,NULL,1,2024,'物理类','本科批',628,6600,636,390),(15,5,NULL,1,2023,'物理类','本科批',627,6850,635,395),(16,6,NULL,1,2025,'物理类','本科批',612,11500,620,500),(17,6,NULL,1,2024,'物理类','本科批',614,10800,622,490),(18,6,NULL,1,2023,'物理类','本科批',613,11200,621,495),(19,7,NULL,1,2025,'物理类','本科批',618,9600,626,450),(20,7,NULL,1,2024,'物理类','本科批',620,9000,628,440),(21,7,NULL,1,2023,'物理类','本科批',619,9300,627,445),(22,8,NULL,1,2025,'物理类','本科批',608,12800,616,420),(23,8,NULL,1,2024,'物理类','本科批',610,12000,618,410),(24,8,NULL,1,2023,'物理类','本科批',609,12400,617,415),(25,9,NULL,1,2025,'物理类','本科批',598,16800,607,380),(26,9,NULL,1,2024,'物理类','本科批',600,15800,609,370),(27,9,NULL,1,2023,'物理类','本科批',599,16300,608,375),(28,10,NULL,1,2025,'物理类','本科批',615,10300,622,260),(29,10,NULL,1,2024,'物理类','本科批',617,9600,624,255),(30,10,NULL,1,2023,'物理类','本科批',616,9900,623,258),(31,11,NULL,1,2025,'物理类','本科批',596,17500,604,360),(32,11,NULL,1,2024,'物理类','本科批',598,16500,606,350),(33,11,NULL,1,2023,'物理类','本科批',597,17000,605,355),(34,12,NULL,1,2025,'物理类','本科批',610,12100,618,400),(35,12,NULL,1,2024,'物理类','本科批',612,11300,620,390),(36,12,NULL,1,2023,'物理类','本科批',611,11700,619,395),(37,13,NULL,1,2025,'物理类','本科批',592,19500,601,380),(38,13,NULL,1,2024,'物理类','本科批',594,18300,603,370),(39,13,NULL,1,2023,'物理类','本科批',593,18900,602,375),(40,14,NULL,1,2025,'物理类','本科批',580,28000,590,350),(41,14,NULL,1,2024,'物理类','本科批',582,26500,592,340),(42,14,NULL,1,2023,'物理类','本科批',581,27200,591,345),(43,15,NULL,1,2025,'物理类','本科批',630,6200,638,300),(44,15,NULL,1,2024,'物理类','本科批',632,5800,640,290),(45,15,NULL,1,2023,'物理类','本科批',631,6000,639,295),(46,16,NULL,1,2025,'物理类','本科批',570,33000,580,420),(47,16,NULL,1,2024,'物理类','本科批',572,31200,582,410),(48,16,NULL,1,2023,'物理类','本科批',571,32100,581,415),(49,17,NULL,1,2025,'物理类','本科批',562,38000,573,450),(50,17,NULL,1,2024,'物理类','本科批',564,36000,575,440),(51,17,NULL,1,2023,'物理类','本科批',563,37000,574,445),(52,18,NULL,1,2025,'物理类','本科批',555,44000,566,430),(53,18,NULL,1,2024,'物理类','本科批',557,42000,568,420),(54,18,NULL,1,2023,'物理类','本科批',556,43000,567,425),(55,19,NULL,1,2025,'物理类','本科批',540,59000,552,400),(56,19,NULL,1,2024,'物理类','本科批',542,57000,554,390),(57,19,NULL,1,2023,'物理类','本科批',541,58000,553,395),(58,20,NULL,1,2025,'物理类','本科批',530,69000,542,380),(59,20,NULL,1,2024,'物理类','本科批',532,67000,544,370),(60,20,NULL,1,2023,'物理类','本科批',531,68000,543,375),(61,21,NULL,1,2025,'物理类','本科批',690,75,694,45),(62,21,NULL,1,2024,'物理类','本科批',692,55,696,42),(63,21,NULL,1,2023,'物理类','本科批',691,65,695,44),(64,22,NULL,1,2025,'物理类','本科批',688,95,692,40),(65,22,NULL,1,2024,'物理类','本科批',690,72,694,38),(66,22,NULL,1,2023,'物理类','本科批',689,85,693,42),(67,23,NULL,1,2025,'物理类','本科批',676,400,682,80),(68,23,NULL,1,2024,'物理类','本科批',678,320,684,75),(69,23,NULL,1,2023,'物理类','本科批',677,360,683,78),(70,24,NULL,1,2025,'物理类','本科批',680,280,686,85),(71,24,NULL,1,2024,'物理类','本科批',682,220,688,80),(72,24,NULL,1,2023,'物理类','本科批',681,250,687,82),(73,25,NULL,1,2025,'物理类','本科批',674,450,680,90),(74,25,NULL,1,2024,'物理类','本科批',676,380,682,85),(75,25,NULL,1,2023,'物理类','本科批',675,420,681,88),(76,26,NULL,1,2025,'物理类','本科批',678,340,683,60),(77,26,NULL,1,2024,'物理类','本科批',680,280,685,55),(78,26,NULL,1,2023,'物理类','本科批',679,310,684,58),(79,27,NULL,1,2025,'物理类','本科批',655,1800,663,110),(80,27,NULL,1,2024,'物理类','本科批',657,1550,665,105),(81,27,NULL,1,2023,'物理类','本科批',656,1680,664,108),(82,28,NULL,1,2025,'物理类','本科批',658,1620,666,120),(83,28,NULL,1,2024,'物理类','本科批',660,1380,668,115),(84,28,NULL,1,2023,'物理类','本科批',659,1500,667,118),(85,29,NULL,1,2025,'物理类','本科批',665,950,672,95),(86,29,NULL,1,2024,'物理类','本科批',667,820,674,90),(87,29,NULL,1,2023,'物理类','本科批',666,880,673,92),(88,30,NULL,1,2025,'物理类','本科批',668,820,675,70),(89,30,NULL,1,2024,'物理类','本科批',670,700,677,68),(90,30,NULL,1,2023,'物理类','本科批',669,760,676,72),(91,31,NULL,1,2025,'物理类','本科批',660,1400,667,55),(92,31,NULL,1,2024,'物理类','本科批',662,1200,669,50),(93,31,NULL,1,2023,'物理类','本科批',661,1300,668,52),(94,32,NULL,1,2025,'物理类','本科批',652,2100,660,100),(95,32,NULL,1,2024,'物理类','本科批',654,1850,662,95),(96,32,NULL,1,2023,'物理类','本科批',653,1980,661,98),(97,33,NULL,1,2025,'物理类','本科批',650,2350,658,105),(98,33,NULL,1,2024,'物理类','本科批',652,2050,660,100),(99,33,NULL,1,2023,'物理类','本科批',651,2200,659,102),(100,34,NULL,1,2025,'物理类','本科批',648,2600,656,80),(101,34,NULL,1,2024,'物理类','本科批',650,2300,658,78),(102,34,NULL,1,2023,'物理类','本科批',649,2450,657,79),(103,1,1,1,2025,'物理类','本科批',678,380,682,50),(104,2,1,1,2025,'物理类','本科批',668,900,674,45),(105,12,1,1,2025,'物理类','本科批',618,9800,626,60),(106,15,7,1,2025,'物理类','本科批',640,4000,648,55),(107,10,29,1,2025,'物理类','本科批',622,8200,630,35);
/*!40000 ALTER TABLE `admission_scores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `majors`
--

DROP TABLE IF EXISTS `majors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `majors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `category` varchar(30) NOT NULL,
  `subcategory` varchar(50) DEFAULT NULL,
  `intro` text,
  `degree` varchar(30) DEFAULT NULL,
  `duration` int DEFAULT '4',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `majors`
--

LOCK TABLES `majors` WRITE;
/*!40000 ALTER TABLE `majors` DISABLE KEYS */;
INSERT INTO `majors` VALUES (1,'计算机科学与技术','工学','计算机类','研究计算机系统与软件开发。','工学学士',4),(2,'软件工程','工学','计算机类','软件开发流程、项目管理。','工学学士',4),(3,'人工智能','工学','计算机类','机器学习、深度学习、NLP。人才缺口大。','工学学士',4),(4,'数据科学与大数据技术','工学','计算机类','数据分析、挖掘、大数据平台。','工学学士',4),(5,'电子信息工程','工学','电子信息类','电子电路、信号处理、通信。','工学学士',4),(6,'通信工程','工学','电子信息类','信息传输与交换，5G/6G。','工学学士',4),(7,'临床医学','医学','临床医学类','诊断治疗疾病，学制长门槛高。','医学学士',5),(8,'口腔医学','医学','口腔医学类','口腔颌面疾病防治，收入可观。','医学学士',5),(9,'金融学','经济学','金融学类','资金融通、投资、风险管理。','经济学学士',4),(10,'会计学','管理学','工商管理类','财务会计、审计、税务。','管理学学士',4),(11,'法学','法学','法学类','法律理论与实务，需法考。','法学学士',4),(12,'机械工程','工学','机械类','机械设计制造及自动化。','工学学士',4),(13,'电气工程及其自动化','工学','电气类','电力系统、电机控制。','工学学士',4),(14,'土木工程','工学','土木类','房屋桥梁隧道设计建造。','工学学士',4),(15,'建筑学','工学','建筑类','工程技术与艺术审美融合。','建筑学学士',5),(16,'数学与应用数学','理学','数学类','基础学科，培养逻辑思维。','理学学士',4),(17,'英语','文学','外国语言文学类','语言应用和跨文化交际。','文学学士',4),(18,'汉语言文学','文学','中国语言文学类','中国语言和文学。','文学学士',4),(19,'工商管理','管理学','工商管理类','企业管理/营销/人力资源。','管理学学士',4),(20,'市场营销','管理学','工商管理类','市场分析/消费者行为。','管理学学士',4),(21,'信息管理与信息系统','管理学','管理科学与工程类','IT+管理交叉学科。','管理学学士',4),(22,'新能源科学与工程','工学','能源动力类','新能源技术，碳中和。','工学学士',4),(23,'生物医学工程','工学','生物医学工程类','工程学与医学交叉。','工学学士',4),(24,'网络空间安全','工学','计算机类','网络攻防、密码学。','工学学士',4),(25,'护理学','医学','护理学类','临床护理、管理。','理学学士',4),(26,'物联网工程','工学','计算机类','传感器、嵌入式、网络。','工学学士',4),(27,'心理学','理学','心理学类','心理现象和行为规律。','理学学士',4),(28,'环境工程','工学','环境科学与工程类','水处理、大气治理。','工学学士',4),(29,'药学','医学','药学类','药物研发、生产、质控。','理学学士',4),(30,'交通运输','工学','交通运输类','交通规划设计运营。','工学学士',4);
/*!40000 ALTER TABLE `majors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `major_profiles`
--

DROP TABLE IF EXISTS `major_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `major_profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `major_id` int NOT NULL,
  `avg_starting_salary` int DEFAULT NULL,
  `employment_rate_3yr` decimal(5,2) DEFAULT NULL,
  `top_industries` text,
  `top_positions` text,
  `top_cities` text,
  `postgrad_rate` decimal(5,2) DEFAULT NULL,
  `holland_code` varchar(10) DEFAULT NULL,
  `data_year` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `major_id` (`major_id`),
  CONSTRAINT `major_profiles_ibfk_1` FOREIGN KEY (`major_id`) REFERENCES `majors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `major_profiles`
--

LOCK TABLES `major_profiles` WRITE;
/*!40000 ALTER TABLE `major_profiles` DISABLE KEYS */;
INSERT INTO `major_profiles` VALUES (1,1,8500,95.20,'[\"互联网\",\"软件开发\",\"金融科技\",\"AI\",\"通信\"]','[\"软件工程师\",\"算法工程师\"]','[\"南京\",\"苏州\",\"上海\",\"杭州\",\"北京\"]',25.30,'IRC',2024),(2,2,8200,94.80,'[\"互联网\",\"游戏\",\"金融IT\"]','[\"软件工程师\",\"项目经理\"]','[\"南京\",\"苏州\",\"上海\",\"杭州\"]',22.10,'IRC',2024),(3,3,10000,91.50,'[\"AI\",\"互联网\",\"自动驾驶\"]','[\"AI算法工程师\",\"NLP工程师\"]','[\"上海\",\"北京\",\"深圳\",\"杭州\",\"苏州\"]',40.50,'IRC',2024),(4,4,8800,93.00,'[\"互联网\",\"金融\",\"电商\",\"政务\"]','[\"数据分析师\",\"大数据工程师\"]','[\"上海\",\"北京\",\"南京\"]',28.00,'IRC',2024),(5,7,5800,97.80,'[\"医院\",\"社区卫生中心\"]','[\"临床医师\",\"住院医师\"]','[\"全省各城市\"]',65.20,'ISR',2024),(6,8,7000,96.50,'[\"口腔医院\",\"私立诊所\"]','[\"口腔医师\",\"正畸医师\"]','[\"全省各城市\"]',45.30,'IRS',2024),(7,9,7500,91.00,'[\"银行\",\"证券\",\"基金\",\"保险\"]','[\"投资分析师\",\"理财经理\"]','[\"上海\",\"南京\",\"苏州\",\"北京\"]',32.50,'ECS',2024),(8,10,6500,93.50,'[\"会计师事务所\",\"企业财务\",\"银行\"]','[\"审计师\",\"税务师\"]','[\"全省各城市\"]',20.80,'CES',2024),(9,11,6000,88.20,'[\"律所\",\"法院\",\"企业法务\"]','[\"律师\",\"法务\",\"合规官\"]','[\"南京\",\"苏州\",\"上海\",\"北京\"]',55.30,'ESA',2024),(10,12,7000,92.80,'[\"汽车\",\"新能源装备\",\"机器人\"]','[\"机械设计师\",\"制造工程师\"]','[\"苏州\",\"无锡\",\"常州\",\"上海\"]',28.60,'RCI',2024),(11,13,7800,94.50,'[\"国家电网\",\"新能源\",\"电气设备\"]','[\"电气工程师\",\"新能源工程师\"]','[\"全省各城市\"]',30.20,'RIC',2024),(12,22,7500,88.00,'[\"新能源\",\"光伏\",\"储能\"]','[\"新能源工程师\",\"项目经理\"]','[\"苏州\",\"无锡\",\"常州\",\"盐城\"]',25.00,'RIC',2024),(13,24,9000,94.20,'[\"网络安全公司\",\"政府网安\"]','[\"安全工程师\",\"渗透测试师\"]','[\"南京\",\"苏州\",\"上海\",\"北京\"]',30.80,'IRC',2024);
/*!40000 ALTER TABLE `major_profiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `major_trends`
--

DROP TABLE IF EXISTS `major_trends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `major_trends` (
  `id` int NOT NULL AUTO_INCREMENT,
  `major_id` int NOT NULL,
  `year_forecast` int NOT NULL,
  `demand_trend` varchar(20) NOT NULL,
  `saturation_level` varchar(20) NOT NULL,
  `avg_salary_forecast` int DEFAULT NULL,
  `confidence` varchar(10) DEFAULT NULL,
  `data_source` text,
  `summary` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_trend` (`major_id`,`year_forecast`),
  CONSTRAINT `major_trends_ibfk_1` FOREIGN KEY (`major_id`) REFERENCES `majors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `major_trends`
--

LOCK TABLES `major_trends` WRITE;
/*!40000 ALTER TABLE `major_trends` DISABLE KEYS */;
INSERT INTO `major_trends` VALUES (1,1,2030,'增长','平衡',12000,'高','教育部IT行业报告','计算机需求持续增长，但竞争加剧。AI/云计算方向最旺。江苏软件产业大省，南京苏州机会多。'),(2,3,2030,'快速增长','供不应求',18000,'中','新一代AI发展规划','AI人才缺口巨大。江苏智能制造布局创造大量AI岗位。'),(3,7,2030,'稳定','平衡',9000,'高','国家卫健委数据','医生需求稳定增长，基层缺口大。三甲竞争激烈需深造。'),(4,9,2030,'稳定','供过于求',10000,'中','中国金融行业发展报告','传统金融饱和，量化/金融科技有缺口。'),(5,10,2030,'稳定','供过于求',8500,'高','财政部会计司统计','基础会计饱和。CPA持证人仍有缺口。'),(6,12,2030,'稳定','平衡',9500,'中','中国机械工业联合会','传统机械向智能转型。苏锡机器人产业对复合人才需求大。'),(7,13,2030,'增长','平衡',11000,'高','国家能源局数据','新能源/智能电网人才缺口大。江苏海上风电全国领先。'),(8,24,2030,'快速增长','供不应求',15000,'中','中国信通院网安报告','网安人才缺口百万级。建议多参加CTF实战。');
/*!40000 ALTER TABLE `major_trends` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-04  2:38:00
