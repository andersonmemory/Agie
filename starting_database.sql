/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.2-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: magil_ecosystem_clone
-- ------------------------------------------------------
-- Server version	11.8.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `discord_users`
--

DROP TABLE IF EXISTS `discord_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `discord_users` (
  `id` bigint(20) unsigned NOT NULL,
  `global_name` varchar(32) NOT NULL,
  `last_focus_date` datetime DEFAULT NULL,
  `current_focus_streak` smallint(5) unsigned NOT NULL DEFAULT 0,
  `max_focus_streak` smallint(5) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discord_users`
--

LOCK TABLES `discord_users` WRITE;
/*!40000 ALTER TABLE `discord_users` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `discord_users` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `focus_sessions`
--

DROP TABLE IF EXISTS `focus_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `focus_sessions` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `focus_datetime` datetime NOT NULL,
  `duration_minutes` smallint(5) unsigned NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `focus_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `discord_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `focus_sessions`
--

LOCK TABLES `focus_sessions` WRITE;
/*!40000 ALTER TABLE `focus_sessions` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `focus_sessions` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `moderators`
--

DROP TABLE IF EXISTS `moderators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `moderators` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `moderators_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `discord_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `moderators`
--

LOCK TABLES `moderators` WRITE;
/*!40000 ALTER TABLE `moderators` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `moderators` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Temporary table structure for view `moderators_view`
--

DROP TABLE IF EXISTS `moderators_view`;
/*!50001 DROP VIEW IF EXISTS `moderators_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `moderators_view` AS SELECT
 1 AS `id`,
  1 AS `global_name`,
  1 AS `password` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `pomodoro_preferences`
--

DROP TABLE IF EXISTS `pomodoro_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `pomodoro_preferences` (
  `user_id` bigint(20) unsigned NOT NULL,
  `pomodoro` tinyint(3) unsigned NOT NULL DEFAULT 25,
  `short_break` tinyint(3) unsigned NOT NULL DEFAULT 5,
  `long_break` tinyint(3) unsigned NOT NULL DEFAULT 15,
  `long_break_interval` tinyint(3) unsigned NOT NULL DEFAULT 4,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `pomodoro_preferences_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_configs` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pomodoro_preferences`
--

LOCK TABLES `pomodoro_preferences` WRITE;
/*!40000 ALTER TABLE `pomodoro_preferences` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `pomodoro_preferences` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `timer_possible_colors`
--

DROP TABLE IF EXISTS `timer_possible_colors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `timer_possible_colors` (
  `color` varchar(20) NOT NULL,
  PRIMARY KEY (`color`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timer_possible_colors`
--

LOCK TABLES `timer_possible_colors` WRITE;
/*!40000 ALTER TABLE `timer_possible_colors` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `timer_possible_colors` VALUES
('aleatório'),
('amarelo'),
('azul'),
('cinza'),
('laranja'),
('preto'),
('rosa'),
('roxo'),
('verde'),
('vermelho');
/*!40000 ALTER TABLE `timer_possible_colors` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `timer_visual_preferences`
--

DROP TABLE IF EXISTS `timer_visual_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `timer_visual_preferences` (
  `user_id` bigint(20) unsigned NOT NULL,
  `pomodoro_color` varchar(20) NOT NULL DEFAULT 'vermelho',
  `break_color` varchar(20) NOT NULL DEFAULT 'rosa',
  `stopwatch_color` varchar(20) NOT NULL DEFAULT 'azul',
  `pomodoro_image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `fk_visual_prefs_pomo_color` (`pomodoro_color`),
  KEY `fk_visual_prefs_pomo_break_color` (`break_color`),
  KEY `fk_visual_prefs_stopwatch_color` (`stopwatch_color`),
  CONSTRAINT `fk_visual_prefs_pomo_break_color` FOREIGN KEY (`break_color`) REFERENCES `timer_possible_colors` (`color`) ON UPDATE CASCADE,
  CONSTRAINT `fk_visual_prefs_pomo_color` FOREIGN KEY (`pomodoro_color`) REFERENCES `timer_possible_colors` (`color`) ON UPDATE CASCADE,
  CONSTRAINT `fk_visual_prefs_stopwatch_color` FOREIGN KEY (`stopwatch_color`) REFERENCES `timer_possible_colors` (`color`) ON UPDATE CASCADE,
  CONSTRAINT `fk_visual_prefs_user` FOREIGN KEY (`user_id`) REFERENCES `discord_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timer_visual_preferences`
--

LOCK TABLES `timer_visual_preferences` WRITE;
/*!40000 ALTER TABLE `timer_visual_preferences` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `timer_visual_preferences` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `user_configs`
--

DROP TABLE IF EXISTS `user_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_configs` (
  `user_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `user_configs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `discord_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_configs`
--

LOCK TABLES `user_configs` WRITE;
/*!40000 ALTER TABLE `user_configs` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `user_configs` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `warns`
--

DROP TABLE IF EXISTS `warns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `warns` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `warn_datetime` datetime NOT NULL,
  `reason` varchar(500) NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  `moderator_id` smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `moderator_id` (`moderator_id`),
  CONSTRAINT `warns_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `discord_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `warns_ibfk_2` FOREIGN KEY (`moderator_id`) REFERENCES `moderators` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warns`
--

LOCK TABLES `warns` WRITE;
/*!40000 ALTER TABLE `warns` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `warns` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Final view structure for view `moderators_view`
--

/*!50001 DROP VIEW IF EXISTS `moderators_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb3 */;
/*!50001 SET character_set_results     = utf8mb3 */;
/*!50001 SET collation_connection      = utf8mb3_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `moderators_view` AS select `discord_users`.`id` AS `id`,`discord_users`.`global_name` AS `global_name`,`moderators`.`password` AS `password` from (`moderators` join `discord_users` on(`discord_users`.`id` = `moderators`.`user_id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-07-11 17:45:34
