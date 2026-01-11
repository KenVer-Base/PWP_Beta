-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jan 08, 2026 at 07:35 AM
-- Server version: 8.4.3
-- PHP Version: 8.3.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `social_media_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `comments`
--

CREATE TABLE `comments` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `post_id` int NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `comments`
--

INSERT INTO `comments` (`id`, `user_id`, `post_id`, `content`, `created_at`) VALUES
(6, 1, 5, 'iya weh', '2026-01-05 10:44:22'),
(7, 1, 8, 'kenapa bang', '2026-01-05 12:09:01'),
(8, 3, 5, 'bejir', '2026-01-05 13:00:25'),
(10, 2, 11, 'sindrom ai gila', '2026-01-07 16:34:46'),
(11, 2, 8, '@El Faqih gatau yak', '2026-01-07 16:38:50'),
(12, 2, 11, 'sama sih wkwkkw', '2026-01-07 16:40:59');

-- --------------------------------------------------------

--
-- Table structure for table `follows`
--

CREATE TABLE `follows` (
  `follower_id` int NOT NULL,
  `followed_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `follows`
--

INSERT INTO `follows` (`follower_id`, `followed_id`, `created_at`) VALUES
(1, 2, '2026-01-05 10:26:47'),
(2, 1, '2026-01-07 16:29:54'),
(3, 1, '2026-01-05 10:55:35'),
(3, 2, '2026-01-05 10:55:18');

-- --------------------------------------------------------

--
-- Table structure for table `likes`
--

CREATE TABLE `likes` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `post_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `likes`
--

INSERT INTO `likes` (`id`, `user_id`, `post_id`) VALUES
(168, 1, 5),
(179, 1, 7),
(171, 1, 8),
(170, 1, 11),
(147, 2, 5),
(116, 2, 7),
(173, 2, 8),
(172, 2, 11),
(89, 3, 5),
(135, 3, 7),
(128, 3, 8),
(174, 4, 11);

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int NOT NULL,
  `sender_id` int NOT NULL,
  `receiver_id` int NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id`, `sender_id`, `receiver_id`, `message`, `created_at`) VALUES
(1, 2, 1, 'oi', '2026-01-05 09:53:45'),
(2, 1, 2, 'oi mmk', '2026-01-05 09:54:09'),
(3, 2, 1, 'apasi kntol', '2026-01-05 09:54:26'),
(4, 1, 2, 'coklah', '2026-01-05 09:58:35'),
(5, 2, 1, 'kenapa?', '2026-01-05 09:59:31'),
(6, 1, 2, 'anjay', '2026-01-05 10:29:03'),
(7, 3, 1, 'halo bang', '2026-01-05 10:59:21'),
(8, 1, 2, 'memeg', '2026-01-05 11:33:57'),
(9, 2, 3, 'woylah', '2026-01-05 11:50:14'),
(10, 1, 3, 'yo kenapa', '2026-01-05 12:09:19'),
(11, 2, 4, 'yo nigga, why are you so bad?', '2026-01-07 15:04:33'),
(12, 2, 4, 'you fckin liar', '2026-01-07 15:04:44'),
(13, 1, 4, 'yo', '2026-01-07 15:10:50'),
(14, 1, 4, 'p', '2026-01-07 15:10:58'),
(15, 4, 1, 'o', '2026-01-07 15:11:00');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `type` enum('like','comment','follow') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'like',
  `target_id` int NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `message`, `is_read`, `created_at`, `type`, `target_id`) VALUES
(1, 1, 'El Magnifico menyukai postingan Anda.', 1, '2026-01-05 09:53:36', 'like', 0),
(2, 1, 'El Magnifico mengomentari postingan Anda.', 1, '2026-01-05 09:56:59', 'like', 0),
(3, 1, 'El Magnifico mengomentari postingan Anda.', 1, '2026-01-05 09:59:19', 'like', 0),
(4, 1, 'El Magnifico mengomentari postingan Anda.', 1, '2026-01-05 10:24:33', 'like', 0),
(5, 2, 'El Faqih mulai mengikuti Anda.', 1, '2026-01-05 10:26:47', 'like', 0),
(6, 2, 'El Faqih mengomentari postingan Anda.', 1, '2026-01-05 10:44:22', 'like', 0),
(7, 2, 'Vicco mulai mengikuti Anda.', 1, '2026-01-05 10:54:45', 'like', 0),
(8, 2, 'Vicco mulai mengikuti Anda.', 1, '2026-01-05 10:55:18', 'like', 0),
(9, 1, 'Vicco mulai mengikuti Anda.', 1, '2026-01-05 10:55:35', 'like', 0),
(10, 2, 'El Faqih mengomentari postingan Anda.', 1, '2026-01-05 12:09:01', 'like', 0),
(11, 2, 'Vicco mengomentari postingan Anda.', 1, '2026-01-05 13:00:25', 'like', 0),
(12, 1, 'El Magnifico mulai mengikuti Anda.', 1, '2026-01-07 16:28:41', 'like', 0),
(13, 1, 'El Magnifico mulai mengikuti Anda.', 1, '2026-01-07 16:29:51', 'like', 0),
(14, 1, 'El Magnifico mulai mengikuti Anda.', 1, '2026-01-07 16:29:54', 'like', 0),
(15, 1, 'El Magnifico mengomentari postingan Anda.', 1, '2026-01-07 16:34:46', 'like', 0),
(16, 1, 'El Magnifico mengomentari postingan Anda.', 1, '2026-01-07 16:40:59', 'like', 0),
(17, 4, 'El Magnifico mulai mengikuti Anda.', 0, '2026-01-08 02:44:39', 'like', 0);

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `caption` text COLLATE utf8mb4_unicode_ci,
  `file_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_type` enum('text','foto','video') COLLATE utf8mb4_unicode_ci DEFAULT 'text',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `posts`
--

INSERT INTO `posts` (`id`, `user_id`, `caption`, `file_path`, `file_type`, `created_at`) VALUES
(5, 2, 'Akbar katanya gey, mang eak?', NULL, 'text', '2026-01-05 10:43:19'),
(7, 2, 'ekspresi guwe', '2_a29800ccc43856d8c42c733aaa0f0d68.jpg', 'foto', '2026-01-05 11:42:44'),
(8, 2, 'guwe cape bat jiers \r\n', NULL, 'text', '2026-01-05 11:42:55'),
(11, 1, 'gw kebanyakan make ai wok\r\n', '1_download_5.jpg', 'foto', '2026-01-07 16:17:48');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `profile_pic` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT 'default.png',
  `bio` text COLLATE utf8mb4_unicode_ci,
  `cover_pic` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT 'default_cover.png',
  `joined_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `profile_pic`, `bio`, `cover_pic`, `joined_at`) VALUES
(1, 'El Faqih', 'faqih@gmail.com', 'scrypt:32768:8:1$mEafcoglyTT8udVx$c320b2b4d0b7bcab549f8ecfe9ba8a70756184a1729420059b2d451e096b126072b986465b36a3707a781f855f6c458e8005599fa3aef3c7d71cab2386d29f8d', 'pfp_1_.jpeg', 'Bio sule😭😭😭', 'cover_1_Desain_tanpa_judul.png', '2026-01-05 10:04:32'),
(2, 'El Magnifico', 'chitokinii@gmail.com', 'scrypt:32768:8:1$goPNzlHqpmMGzxR5$2e6327dfcab95aaf6aac01533d551ededba797cbe08d98b9a6659a54ac68891769f278b9d27e8b26c2d27cfb1ba17f8d17a3c87cb86e9f180b0976f7d27f5785', 'pfp_2_Bang_ryan__.jpg', 'Saya adalah manusia normal', 'cover_2_935f200405622e2aececbd50150a979d.jpg', '2026-01-05 10:04:32'),
(3, 'Vicco', 'faqihpmkt66@gmail.com', 'scrypt:32768:8:1$meFtsnQh1eMkvjVj$5eac8c2e60c4a5f2eb833e0e0263a2ca2ff6880caf8f55570763e24e17c8003e62c50a7f647292cd8dbf41c4a460e9091b507be49d4f1a7aab1be8c4f8abca39', 'pfp_3_speed_trying_not_to_laugh_.jpg', '', 'cover_3_Screenshot_2025-12-16_191458_imgupscaler.ai_V2Pro_2K.png', '2026-01-05 10:54:33'),
(4, 'JaneCiio', 'jane009@gmail.com', 'scrypt:32768:8:1$SStkrYPdZuz37RVC$c837a8b4ba62c8030c1696ee20bc24d3e3c1bd9fbe9030da7354f84bacf81e06f7301004835f0bbbd48ba8d2aba4768c2be6443ad611033fa5a755a97423fbef', 'pfp_4_downloaad.jpg', '', 'cover_4_este_fondo_de_pantalla_es_para_ustedes_jsjs.jpg', '2026-01-05 12:03:10'),
(5, 'La Dontole', 'dontole@gmail.com', 'scrypt:32768:8:1$56SlSl28zpRggpoN$e65ab2b647e6589515edc5dcd941bd28af20f322d3f742d376755efcf50d2f25c1d142f7f1382063ea8fb30db8a348e27da6b094521b732d17c506c6043df3b9', 'pfp_5_794c72a6-d473-40e7-9404-6b3cdc10e624.jpg', 'The next pirates king', 'cover_5_banner_YouTube_one_piece_1.jpeg', '2026-01-08 07:26:19');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `post_id` (`post_id`);

--
-- Indexes for table `follows`
--
ALTER TABLE `follows`
  ADD PRIMARY KEY (`follower_id`,`followed_id`),
  ADD KEY `followed_id` (`followed_id`);

--
-- Indexes for table `likes`
--
ALTER TABLE `likes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_like` (`user_id`,`post_id`),
  ADD KEY `post_id` (`post_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `comments`
--
ALTER TABLE `comments`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `likes`
--
ALTER TABLE `likes`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=180;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `comments`
--
ALTER TABLE `comments`
  ADD CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `follows`
--
ALTER TABLE `follows`
  ADD CONSTRAINT `follows_ibfk_1` FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `follows_ibfk_2` FOREIGN KEY (`followed_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `likes`
--
ALTER TABLE `likes`
  ADD CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
