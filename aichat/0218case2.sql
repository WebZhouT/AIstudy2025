/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50726 (5.7.26)
 Source Host           : localhost:3306
 Source Schema         : 0218case2

 Target Server Type    : MySQL
 Target Server Version : 50726 (5.7.26)
 File Encoding         : 65001

 Date: 21/02/2025 17:09:23
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for chat
-- ----------------------------
DROP TABLE IF EXISTS `chat`;
CREATE TABLE `chat`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sendid` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL COMMENT '用户id',
  `acceptid` int(11) NULL DEFAULT NULL COMMENT '类型 1用户发送，2 客服回复',
  `comments` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL COMMENT '聊天记录信息',
  `type` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL COMMENT '类型type txt 文字 pic 图片',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 142 CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of chat
-- ----------------------------
INSERT INTO `chat` VALUES (1, 'w6Jcv5n_YApuBC8kAAAZ', 1, '111111111111111111', 'txt');
INSERT INTO `chat` VALUES (2, 'w6Jcv5n_YApuBC8kAAAZ', 1, '32132231', 'txt');
INSERT INTO `chat` VALUES (3, 'w6Jcv5n_YApuBC8kAAAZ', 1, '32132231', 'txt');
INSERT INTO `chat` VALUES (4, 'w6Jcv5n_YApuBC8kAAAZ', 1, '32132231', 'txt');
INSERT INTO `chat` VALUES (5, 'w6Jcv5n_YApuBC8kAAAZ', 1, '32132231', 'txt');
INSERT INTO `chat` VALUES (12, 'GSlrzwPQHLmG38NpAAAH', 1, '1111111111', 'txt');
INSERT INTO `chat` VALUES (11, 'GSlrzwPQHLmG38NpAAAH', 1, '1111111111', 'txt');
INSERT INTO `chat` VALUES (13, 'GSlrzwPQHLmG38NpAAAH', 1, '1111111111', 'txt');
INSERT INTO `chat` VALUES (14, 'GSlrzwPQHLmG38NpAAAH', 1, '1111111111', 'txt');
INSERT INTO `chat` VALUES (32, 'w6Jcv5n_YApuBC8kAAAZ', 2, '1', 'txt');
INSERT INTO `chat` VALUES (31, 'w6Jcv5n_YApuBC8kAAAZ', 2, '1', 'txt');
INSERT INTO `chat` VALUES (30, 'GSlrzwPQHLmG38NpAAAH', 2, '1', 'txt');
INSERT INTO `chat` VALUES (29, 'w6Jcv5n_YApuBC8kAAAZ', 2, '1', 'txt');
INSERT INTO `chat` VALUES (28, 'w6Jcv5n_YApuBC8kAAAZ', 2, '1', 'txt');
INSERT INTO `chat` VALUES (27, 'w6Jcv5n_YApuBC8kAAAZ', 2, '123', 'txt');
INSERT INTO `chat` VALUES (26, 'w6Jcv5n_YApuBC8kAAAZ', 2, '11111111111111111111', 'txt');
INSERT INTO `chat` VALUES (33, 'w6Jcv5n_YApuBC8kAAAZ', 2, '1', 'txt');
INSERT INTO `chat` VALUES (34, 'w6Jcv5n_YApuBC8kAAAZ', 2, '1', 'txt');
INSERT INTO `chat` VALUES (35, 'w6Jcv5n_YApuBC8kAAAZ', 2, '123', 'txt');
INSERT INTO `chat` VALUES (36, 'w6Jcv5n_YApuBC8kAAAZ', 2, '333', 'txt');
INSERT INTO `chat` VALUES (37, 'w6Jcv5n_YApuBC8kAAAZ', 2, '1', 'txt');
INSERT INTO `chat` VALUES (38, 'w6Jcv5n_YApuBC8kAAAZ', 2, '123', 'txt');
INSERT INTO `chat` VALUES (39, 'w6Jcv5n_YApuBC8kAAAZ', 2, '111', 'txt');
INSERT INTO `chat` VALUES (40, 'w6Jcv5n_YApuBC8kAAAZ', 2, '111', 'txt');
INSERT INTO `chat` VALUES (41, 'GSlrzwPQHLmG38NpAAAH', 1, '123312', 'txt');
INSERT INTO `chat` VALUES (42, 'GSlrzwPQHLmG38NpAAAH', 1, '123312', 'txt');
INSERT INTO `chat` VALUES (43, 'GSlrzwPQHLmG38NpAAAH', 1, '123312', 'txt');
INSERT INTO `chat` VALUES (44, 'GSlrzwPQHLmG38NpAAAH', 1, '123312', 'txt');
INSERT INTO `chat` VALUES (45, 'GSlrzwPQHLmG38NpAAAH', 1, '123312', 'txt');
INSERT INTO `chat` VALUES (46, 'GSlrzwPQHLmG38NpAAAH', 1, '123312', 'txt');
INSERT INTO `chat` VALUES (47, 'GSlrzwPQHLmG38NpAAAH', 1, '123312', 'txt');
INSERT INTO `chat` VALUES (48, 'GSlrzwPQHLmG38NpAAAH', 1, '123312', 'txt');
INSERT INTO `chat` VALUES (49, 'GSlrzwPQHLmG38NpAAAH', 1, '111', 'txt');
INSERT INTO `chat` VALUES (50, 'GSlrzwPQHLmG38NpAAAH', 1, '123', 'txt');
INSERT INTO `chat` VALUES (51, 'w6Jcv5n_YApuBC8kAAAZ', 2, '312312', 'txt');
INSERT INTO `chat` VALUES (52, 'w6Jcv5n_YApuBC8kAAAZ', 2, '3123121', 'txt');
INSERT INTO `chat` VALUES (53, 'GSlrzwPQHLmG38NpAAAH', 2, '111111111111', 'txt');
INSERT INTO `chat` VALUES (54, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (55, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (56, 'GSlrzwPQHLmG38NpAAAH', 2, '1111111111111', 'txt');
INSERT INTO `chat` VALUES (57, 'GSlrzwPQHLmG38NpAAAH', 2, '1', 'txt');
INSERT INTO `chat` VALUES (58, 'GSlrzwPQHLmG38NpAAAH', 2, '1', 'txt');
INSERT INTO `chat` VALUES (59, 'GSlrzwPQHLmG38NpAAAH', 2, '1', 'txt');
INSERT INTO `chat` VALUES (60, 'GSlrzwPQHLmG38NpAAAH', 2, '2', 'txt');
INSERT INTO `chat` VALUES (61, 'GSlrzwPQHLmG38NpAAAH', 2, '2', 'txt');
INSERT INTO `chat` VALUES (62, 'GSlrzwPQHLmG38NpAAAH', 2, '3', 'txt');
INSERT INTO `chat` VALUES (63, 'GSlrzwPQHLmG38NpAAAH', 2, '4', 'txt');
INSERT INTO `chat` VALUES (64, 'GSlrzwPQHLmG38NpAAAH', 1, '123', 'txt');
INSERT INTO `chat` VALUES (65, 'GSlrzwPQHLmG38NpAAAH', 1, '1234', 'txt');
INSERT INTO `chat` VALUES (66, 'GSlrzwPQHLmG38NpAAAH', 2, '4', 'txt');
INSERT INTO `chat` VALUES (67, 'GSlrzwPQHLmG38NpAAAH', 2, '4', 'txt');
INSERT INTO `chat` VALUES (68, 'GSlrzwPQHLmG38NpAAAH', 2, '4', 'txt');
INSERT INTO `chat` VALUES (69, 'w6Jcv5n_YApuBC8kAAAZ', 2, '321', 'txt');
INSERT INTO `chat` VALUES (70, 'w6Jcv5n_YApuBC8kAAAZ', 2, '321', 'txt');
INSERT INTO `chat` VALUES (73, 'GSlrzwPQHLmG38NpAAAH', 2, '44', 'txt');
INSERT INTO `chat` VALUES (74, 'GSlrzwPQHLmG38NpAAAH', 2, '443', 'txt');
INSERT INTO `chat` VALUES (75, 'GSlrzwPQHLmG38NpAAAH', 2, '443', 'txt');
INSERT INTO `chat` VALUES (76, 'GSlrzwPQHLmG38NpAAAH', 2, '4432', 'txt');
INSERT INTO `chat` VALUES (77, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (80, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (81, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (83, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (84, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (85, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (86, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (87, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (88, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (89, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (90, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (91, 'GSlrzwPQHLmG38NpAAAH', 1, '1', 'txt');
INSERT INTO `chat` VALUES (92, 'GSlrzwPQHLmG38NpAAAH', 1, '1', 'txt');
INSERT INTO `chat` VALUES (93, 'GSlrzwPQHLmG38NpAAAH', 1, '1', 'txt');
INSERT INTO `chat` VALUES (94, 'GSlrzwPQHLmG38NpAAAH', 1, '12', 'txt');
INSERT INTO `chat` VALUES (95, 'GSlrzwPQHLmG38NpAAAH', 2, '321', 'txt');
INSERT INTO `chat` VALUES (96, 'GSlrzwPQHLmG38NpAAAH', 2, '321', 'txt');
INSERT INTO `chat` VALUES (97, 'GSlrzwPQHLmG38NpAAAH', 2, '3212', 'txt');
INSERT INTO `chat` VALUES (98, 'GSlrzwPQHLmG38NpAAAH', 2, '111111111111', 'txt');
INSERT INTO `chat` VALUES (99, 'GSlrzwPQHLmG38NpAAAH', 1, '123', 'txt');
INSERT INTO `chat` VALUES (100, 'GSlrzwPQHLmG38NpAAAH', 1, '32132132', 'txt');
INSERT INTO `chat` VALUES (101, 'GSlrzwPQHLmG38NpAAAH', 1, '321', 'txt');
INSERT INTO `chat` VALUES (102, 'GSlrzwPQHLmG38NpAAAH', 1, '231', 'txt');
INSERT INTO `chat` VALUES (103, 'GSlrzwPQHLmG38NpAAAH', 1, 'http://127.0.0.1:3000/uploads/file-1740124499031.png', 'img');
INSERT INTO `chat` VALUES (104, 'GSlrzwPQHLmG38NpAAAH', 2, 'http://localhost:3000/uploads/file-1740124924986.jpg', 'img');
INSERT INTO `chat` VALUES (141, 'cj_bd9yiRF2mLLCeAABJ', 1, 'http://127.0.0.1:3000/uploads/file-1740128325389.jpg', 'img');
INSERT INTO `chat` VALUES (125, 'cj_bd9yiRF2mLLCeAABJ', 1, '231', 'txt');
INSERT INTO `chat` VALUES (122, 'cj_bd9yiRF2mLLCeAABJ', 1, '123', 'txt');
INSERT INTO `chat` VALUES (127, 'cj_bd9yiRF2mLLCeAABJ', 1, 'http://127.0.0.1:3000/uploads/file-1740127190671.png', 'img');
INSERT INTO `chat` VALUES (130, 'cj_bd9yiRF2mLLCeAABJ', 1, '1111111111', 'txt');
INSERT INTO `chat` VALUES (137, 'cj_bd9yiRF2mLLCeAABJ', 1, '333', 'txt');
INSERT INTO `chat` VALUES (138, 'cj_bd9yiRF2mLLCeAABJ', 1, '3121221', 'txt');
INSERT INTO `chat` VALUES (140, 'cj_bd9yiRF2mLLCeAABJ', 1, '32', 'txt');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL COMMENT '用户名\r\n',
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL COMMENT '密码\r\n',
  `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL COMMENT '邮箱\r\n',
  `head` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 25 CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (16, 'admin', 'zJx6V5NtgqGhyluhKRg+1Q==', 'ccc@qq.com', NULL);
INSERT INTO `users` VALUES (17, '321', '321', '321', NULL);
INSERT INTO `users` VALUES (18, '111', '111', '123qwewqewqe', NULL);
INSERT INTO `users` VALUES (19, '123231213', '123', 'wdsdasda', NULL);
INSERT INTO `users` VALUES (20, 'dssdasda', '123123', 'weqewq@qq,com', NULL);
INSERT INTO `users` VALUES (21, 'sdasad', '123123', 'saddsdsa@qq.com', NULL);
INSERT INTO `users` VALUES (22, 'qwe002', 'zJx6V5NtgqGhyluhKRg+1Q==', '231321@qqq.com', NULL);
INSERT INTO `users` VALUES (23, 'cc2z004dsa', 'zJx6V5NtgqGhyluhKRg+1Q==', 'antampson@hooli.com', NULL);
INSERT INTO `users` VALUES (24, 'cc2z004', 'zJx6V5NtgqGhyluhKRg+1Q==', 'anit231mpson@hooli.com', NULL);

SET FOREIGN_KEY_CHECKS = 1;
