DROP DATABASE IF EXISTS `phototransform`;
CREATE DATABASE `phototransform` CHARACTER SET `utf8mb4`;
USE `phototransform`;


ALTER TABLE `fil_tag` DROP FOREIGN KEY `fk_fil_tag_fil_id`;
ALTER TABLE `fil_tag` DROP FOREIGN KEY `fk_fil_tag_tag_id`;
ALTER TABLE `mem_use_log` DROP FOREIGN KEY `fk_mem_use_log_fil_id`;
ALTER TABLE `mem_use_log` DROP FOREIGN KEY `fk_mem_use_log_act`;
ALTER TABLE `mem_star` DROP FOREIGN KEY `fk_mem_star_act`;
ALTER TABLE `mem_star` DROP FOREIGN KEY `fk_mem_star_fil_id`;

DROP INDEX `act_pwd_index` ON `member`;
DROP INDEX `account_index` ON `member`;
DROP INDEX `tag_name_index` ON `tag`;
DROP INDEX `fil_tag_index` ON `fil_tag`;
DROP INDEX `act_fil_index` ON `mem_star`;

DROP TABLE IF EXISTS `member`;
DROP TABLE IF EXISTS `filter`;
DROP TABLE IF EXISTS `tag`;
DROP TABLE IF EXISTS `fil_tag`;
DROP TABLE IF EXISTS `mem_use_log`;
DROP TABLE IF EXISTS `fil_log`;
DROP TABLE IF EXISTS `mem_star`;
DROP TABLE IF EXISTS `mem_star_log`;
DROP TABLE IF EXISTS `code`;
DROP TABLE IF EXISTS `mem_log`;

CREATE TABLE `member` (
`account` varchar(64) NOT NULL,
`username` varchar(64) NULL,
`gender` tinyint(3) NULL,
`password` varchar(32) NOT NULL,
`mobile` varchar(32) NULL,
`email` varchar(32) NULL,
`qq` varchar(32) NULL,
`is_qq_auth` tinyint(3) NULL,
`signature` varchar(255) NULL,
`created_dt` datetime NULL,
`valid` tinyint(3) NULL,
PRIMARY KEY (`account`) ,
UNIQUE INDEX `act_pwd_index` (`account` ASC, `password` ASC) USING HASH,
UNIQUE INDEX `account_index` (`account` ASC) USING HASH
)
COMMENT = '会员表，主要记录登录方式与个人信息，account为主键。';

CREATE TABLE `filter` (
`fil_id` bigint(11) NOT NULL,
`name` varchar(255) NOT NULL,
`path` varchar(255) NULL,
`created_dt` datetime NULL,
`created_by` varchar(255) NULL COMMENT '创建会员，如果为系统自有，则为空',
`is_default` tinyint(3) NULL COMMENT '是否为系统自有',
`valid` tinyint(3) NULL,
PRIMARY KEY (`fil_id`) 
)
COMMENT = '滤镜表，记录所有系统与会员发布的滤镜。';

CREATE TABLE `tag` (
`tag_id` bigint(11) NOT NULL,
`tag_name` varchar(32) NULL COMMENT '记录tag内容，加有unique限制',
`created_dt` datetime NULL COMMENT '创建时间',
`created_by` varchar(32) NULL COMMENT '创建者',
`is_default` tinyint(3) NULL COMMENT '是否为系统自有',
`valid` tinyint(3) NULL,
PRIMARY KEY (`tag_id`) ,
UNIQUE INDEX `tag_name_index` (`tag_name` ASC) USING HASH COMMENT 'tag_name 应当全表唯一' 
)
COMMENT = 'tag表记录所有的标签信息。';

CREATE TABLE `fil_tag` (
`fil_id` bigint(11) NOT NULL,
`tag_id` bigint(11) NOT NULL,
`created_dt` datetime NULL,
`valid` tinyint(3) NULL,
PRIMARY KEY (`fil_id`, `tag_id`) ,
UNIQUE INDEX `fil_tag_index` (`fil_id` ASC, `tag_id` ASC) USING HASH COMMENT 'tag表与filter表的关联表' 
);

CREATE TABLE `mem_use_log` (
`log_id` bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '无意义',
`account` varchar(64) NOT NULL,
`fil_id` bigint(3) NOT NULL,
`session` varchar(64) NULL COMMENT 'session唯一标识符',
`created_dt` datetime NULL,
PRIMARY KEY (`log_id`) 
)
COMMENT = '记录会员使用滤镜日志。';

CREATE TABLE `fil_log` (
`log_id` bigint(11) NOT NULL,
`fil_id` bigint(11) NOT NULL,
`action` varchar(32) NULL COMMENT '描述滤镜更新动作',
`his_name` varchar(255) NULL,
`his_path` varchar(255) NULL,
`created_dt` datetime NULL,
PRIMARY KEY (`log_id`) 
)
COMMENT = '用于记录滤镜的更新位置。';

CREATE TABLE `mem_star` (
`account` varchar(32) NOT NULL,
`fil_id` bigint(11) NOT NULL,
`created_dt` datetime NULL,
`valid` tinyint(3) NULL,
PRIMARY KEY (`account`, `fil_id`) ,
UNIQUE INDEX `act_fil_index` (`account` ASC, `fil_id` ASC) USING HASH
)
COMMENT = '用于记录现在会员收藏滤镜。';

CREATE TABLE `mem_star_log` (
`log_id` bigint(11) NOT NULL,
`account` varchar(32) NOT NULL,
`fil_id` bigint(11) NOT NULL,
`action` varchar(32) NULL,
`created_dt` datetime NULL,
PRIMARY KEY (`log_id`) 
)
COMMENT = '用于记录会员收藏日志。';

CREATE TABLE `code` (
`code_id` int(11) NOT NULL,
`table` varchar(32) NULL,
`field` varchar(32) NULL,
`val` int(3) NULL COMMENT '如果值为int类型',
`val_str` varchar(32) NULL COMMENT '如果值为字符串',
`label` varchar(64) NULL COMMENT '标签标识val的含义',
`comment` varchar(255) NULL,
`created_dt` datetime NULL,
`valid` tinyint(11) NULL,
PRIMARY KEY (`code_id`) 
)
COMMENT = 'code表，用于规范化各个表中字段取值的情况，用于管理员阅读而非机器查询。';

CREATE TABLE `mem_log` (
`log_id` bigint(11) NOT NULL,
`account` varchar(64) NULL,
`action` varchar(32) NULL,
`his_username` varchar(64) NULL,
`his_gender` tinyint(3) NULL,
`his_password` varchar(32) NULL,
`his_mobile` varchar(32) NULL,
`his_qq` varchar(32) NULL,
`his_is_qq_auth` tinyint(3) NULL,
`his_signature` varchar(255) NULL,
`his_email` varchar(32) NULL,
`created_dt` datetime NULL,
PRIMARY KEY (`log_id`) 
)
COMMENT = '用于记录用户信息更新日志。';


ALTER TABLE `fil_tag` ADD CONSTRAINT `fk_fil_tag_fil_id` FOREIGN KEY (`fil_id`) REFERENCES `filter` (`fil_id`);
ALTER TABLE `fil_tag` ADD CONSTRAINT `fk_fil_tag_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`tag_id`);
ALTER TABLE `mem_use_log` ADD CONSTRAINT `fk_mem_use_log_fil_id` FOREIGN KEY (`fil_id`) REFERENCES `filter` (`fil_id`);
ALTER TABLE `mem_use_log` ADD CONSTRAINT `fk_mem_use_log_act` FOREIGN KEY (`account`) REFERENCES `member` (`account`);
ALTER TABLE `mem_star` ADD CONSTRAINT `fk_mem_star_act` FOREIGN KEY (`account`) REFERENCES `member` (`account`);
ALTER TABLE `mem_star` ADD CONSTRAINT `fk_mem_star_fil_id` FOREIGN KEY (`fil_id`) REFERENCES `filter` (`fil_id`);

