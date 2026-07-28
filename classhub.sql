-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: classhub
-- ------------------------------------------------------
-- Server version	8.0.38

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
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (104,'Selvamuthu','SelvamuthU@123','Selvamuthu');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance_records`
--

DROP TABLE IF EXISTS `attendance_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int DEFAULT NULL,
  `register_number` varchar(9) DEFAULT NULL,
  `submitted_time` datetime DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `browser` varchar(100) DEFAULT NULL,
  `operating_system` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_id`,`register_number`),
  UNIQUE KEY `unique_attendance` (`session_id`,`register_number`),
  KEY `register_number` (`register_number`),
  CONSTRAINT `attendance_records_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `attendance_sessions` (`session_id`),
  CONSTRAINT `attendance_records_ibfk_2` FOREIGN KEY (`register_number`) REFERENCES `students` (`register_number`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_records`
--

LOCK TABLES `attendance_records` WRITE;
/*!40000 ALTER TABLE `attendance_records` DISABLE KEYS */;
INSERT INTO `attendance_records` VALUES (1,4,'229003136','2026-07-26 14:57:04',NULL,NULL,NULL),(2,4,'229003139','2026-07-26 14:59:28',NULL,NULL,NULL),(3,5,'229003139','2026-07-26 15:01:43',NULL,NULL,NULL),(4,6,'229003139','2026-07-26 15:17:47',NULL,NULL,NULL),(5,6,'229003136','2026-07-26 15:17:56',NULL,NULL,NULL),(6,6,'229003050','2026-07-26 15:18:10',NULL,NULL,NULL),(7,6,'228003128','2026-07-27 18:34:37','127.0.0.1',NULL,NULL),(8,13,'229003139','2026-07-27 20:41:21','127.0.0.1',NULL,NULL),(9,14,'229003139','2026-07-27 20:49:33','127.0.0.1',NULL,NULL),(10,15,'229003139','2026-07-27 20:52:48','127.0.0.1',NULL,NULL),(11,18,'229003139','2026-07-27 21:21:42','127.0.0.1',NULL,NULL),(12,21,'229003139','2026-07-27 21:40:44','127.0.0.1',NULL,NULL),(13,21,'229003136','2026-07-27 21:40:53','127.0.0.1',NULL,NULL),(14,21,'229003050','2026-07-27 21:41:05','127.0.0.1',NULL,NULL),(15,21,'229003104','2026-07-27 21:41:19','127.0.0.1',NULL,NULL),(16,22,'229003104','2026-07-27 21:54:04','127.0.0.1',NULL,NULL),(17,22,'229003139','2026-07-27 21:54:20','127.0.0.1',NULL,NULL),(18,22,'229003136','2026-07-27 21:54:26','127.0.0.1',NULL,NULL),(19,22,'229003050','2026-07-27 21:54:35','127.0.0.1',NULL,NULL),(20,23,'229003050','2026-07-27 22:05:53','127.0.0.1',NULL,NULL),(21,23,'229003139','2026-07-27 22:05:59','127.0.0.1',NULL,NULL),(22,23,'229003136','2026-07-27 22:06:06','127.0.0.1',NULL,NULL),(23,24,'229003136','2026-07-27 22:13:24','127.0.0.1',NULL,NULL),(24,24,'229003139','2026-07-27 22:13:33','127.0.0.1',NULL,NULL),(25,24,'229003050','2026-07-27 22:13:44','127.0.0.1',NULL,NULL),(26,25,'229003050','2026-07-27 22:20:35','127.0.0.1',NULL,NULL),(27,25,'229003139','2026-07-27 22:20:40','127.0.0.1',NULL,NULL),(28,25,'229003136','2026-07-27 22:20:45','127.0.0.1',NULL,NULL),(29,26,'229003136','2026-07-27 22:32:46','127.0.0.1',NULL,NULL),(30,26,'229003139','2026-07-27 22:32:52','127.0.0.1',NULL,NULL),(31,26,'229003050','2026-07-27 22:33:01','127.0.0.1',NULL,NULL),(32,27,'229003139','2026-07-27 23:24:15','127.0.0.1',NULL,NULL),(33,27,'229003136','2026-07-27 23:24:24','127.0.0.1',NULL,NULL),(34,27,'229003050','2026-07-27 23:24:36','127.0.0.1',NULL,NULL),(35,27,'229003104','2026-07-27 23:24:46','127.0.0.1',NULL,NULL);
/*!40000 ALTER TABLE `attendance_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance_sessions`
--

DROP TABLE IF EXISTS `attendance_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_sessions` (
  `session_id` int NOT NULL AUTO_INCREMENT,
  `subject` varchar(40) DEFAULT NULL,
  `period` varchar(15) DEFAULT NULL,
  `attendance_code` varchar(10) DEFAULT NULL,
  `session_date` date DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `status` enum('open','closed') DEFAULT 'open',
  `duration` int NOT NULL DEFAULT '2',
  PRIMARY KEY (`session_id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_sessions`
--

LOCK TABLES `attendance_sessions` WRITE;
/*!40000 ALTER TABLE `attendance_sessions` DISABLE KEYS */;
INSERT INTO `attendance_sessions` VALUES (1,'Mathematics','1','5ZOOZEB0','2026-07-26','2026-07-26 14:29:02',NULL,'closed',2),(2,'Computer Organization','1','IAF1JSIH','2026-07-26','2026-07-26 14:43:16',NULL,'closed',2),(3,'Computer Organization','1','PM8PU6NQ','2026-07-26','2026-07-26 14:44:29',NULL,'closed',2),(4,'Mathematics','1','EMS7SS7R','2026-07-26','2026-07-26 14:56:09',NULL,'closed',2),(5,'Computer Organization','1','FGORV2IJ','2026-07-26','2026-07-26 15:01:11',NULL,'closed',2),(6,'Computer Organization','1','JZ5WUFNY','2026-07-26','2026-07-26 15:17:35',NULL,'closed',2),(7,'Computer Organization','1','70EHT69Y','2026-07-27','2026-07-27 19:41:17','2026-07-27 19:43:17','closed',2),(8,'Computer Organization','1','DG34RIOX','2026-07-27','2026-07-27 19:52:37','2026-07-27 19:54:37','closed',2),(9,'Computer Organization','1','1FALBG1H','2026-07-27','2026-07-27 19:53:05','2026-07-27 19:55:05','closed',2),(10,'Computer Organization','1','TIFCSD1D','2026-07-27','2026-07-27 20:08:54','2026-07-27 20:10:54','closed',2),(11,'Computer Organization','1','QDFXD9SQ','2026-07-27','2026-07-27 20:09:18','2026-07-27 20:11:18','closed',2),(12,'Computer Organization','1','I3OX00YC','2026-07-27','2026-07-27 20:32:22','2026-07-27 20:34:22','closed',2),(13,'Computer Organization','1','5512Z7BL','2026-07-27','2026-07-27 20:40:32','2026-07-27 20:42:32','closed',2),(14,'Computer Organization','1','STSF0T70','2026-07-27','2026-07-27 20:49:17','2026-07-27 20:51:17','closed',2),(15,'Computer Organization','1','CB3LI6Q7','2026-07-27','2026-07-27 20:52:18','2026-07-27 20:54:18','closed',2),(16,'Computer Organization','1','AA9TZBQO','2026-07-27','2026-07-27 20:55:35','2026-07-27 20:57:35','closed',2),(17,'Computer Organization','1','YJS774GD','2026-07-27','2026-07-27 20:58:30','2026-07-27 21:00:30','closed',2),(18,'Computer Organization','1','ZD9A4Z38','2026-07-27','2026-07-27 21:21:31','2026-07-27 21:23:31','closed',2),(19,'Computer Organization','1','9OWB8BWB','2026-07-27','2026-07-27 21:28:55','2026-07-27 21:30:55','closed',2),(20,'Computer Organization','1','MXBEW2KV','2026-07-27','2026-07-27 21:33:14','2026-07-27 21:35:14','closed',2),(21,'Computer Organization','1','Z0950OT2','2026-07-27','2026-07-27 21:39:48','2026-07-27 21:41:48','closed',2),(22,'Computer Organization','1','1AT0W4Q1','2026-07-27','2026-07-27 21:53:54','2026-07-27 21:55:54','closed',2),(23,'Computer Organization','1','3ZMG70FG','2026-07-27','2026-07-27 22:05:38','2026-07-27 22:07:38','closed',2),(24,'Computer Organization','1','PBVGV5UK','2026-07-27','2026-07-27 22:13:09','2026-07-27 22:15:09','closed',2),(25,'Computer Organization','1','SABUQFDZ','2026-07-27','2026-07-27 22:20:19','2026-07-27 22:22:19','closed',2),(26,'Computer Organization','1','P7H2L72F','2026-07-27','2026-07-27 22:32:35','2026-07-27 22:34:35','closed',2),(27,'Java','3','6VHY09S3','2026-07-27','2026-07-27 23:23:50','2026-07-27 23:25:50','closed',2);
/*!40000 ALTER TABLE `attendance_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `register_number` varchar(9) NOT NULL,
  `student_name` varchar(60) NOT NULL,
  `nickname` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`register_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES ('228003128','Sadhan M',NULL),('229003001','Aafrin Farhana F',NULL),('229003002','Aakash M S',NULL),('229003006','Ajay R M',NULL),('229003007','Akash K',NULL),('229003009','Allen Joshua A',NULL),('229003010','Amirthalaxmi A',NULL),('229003017','Asvitha S',NULL),('229003018','Atchaya S',NULL),('229003025','Brindha Sri I',NULL),('229003027','Charishma Sri Sai Saranya Chavvakula',NULL),('229003028','Chennareddy Lakshmi Geethika',NULL),('229003039','Dhanya S',NULL),('229003040','Dharan R',NULL),('229003043','Dharshini V',NULL),('229003044','Dineshraj',NULL),('229003048','Dudekula Safana Homera',NULL),('229003050','Elluru Rohith',NULL),('229003052','Gayathri K',NULL),('229003054','Gayathri S R',NULL),('229003057','Gullari Navya Sri',NULL),('229003058','Hajira Banu H',NULL),('229003061','Harini T',NULL),('229003068','Jayaprakash Gagana Sai',NULL),('229003069','Jeya Suriya R',NULL),('229003071','Kalikiri Sushanth Reddy',NULL),('229003074','Kathir Bala Y',NULL),('229003080','Kothakota Raga Sri Deepika',NULL),('229003085','Madathala Deekshitha Reddy',NULL),('229003086','Maghi Shri B',NULL),('229003088','Mahima R',NULL),('229003104','Omprakash G',NULL),('229003105','Palani Balaji T',NULL),('229003106','Palla Sumanth',NULL),('229003114','Preethi S',NULL),('229003117','Ravuri Udaya Sahithi',NULL),('229003119','Reva B',NULL),('229003120','Rishikesh Suresh',NULL),('229003121','Rithishkumar J',NULL),('229003122','Rohith V',NULL),('229003127','Sahana S',NULL),('229003130','Sakthi Meenakshi S',NULL),('229003133','Santhosh S',NULL),('229003134','Santhoshni N B',NULL),('229003136','Selvamuthu S','Doraemon'),('229003139','Shaik Shamsia','Sister'),('229003141','Shri Dhanya R K',NULL),('229003144','Sivaraman R',NULL),('229003149','Suganya B',NULL),('229003152','Swetha M',NULL),('229003158','Unnam Varshitha',NULL),('229003161','Vasudevan D',NULL),('229003166','Yeddula Harideep Reddy',NULL),('229003178','Nethra R',NULL),('229003180','Ramisetty Guru Pujith Royal',NULL),('229003181','Revanth Gowtham T',NULL),('229003184','Sriimathy S V',NULL),('229003185','Srinidhi K',NULL),('229003186','Sruthy K',NULL);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-28 18:42:50
