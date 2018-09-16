-- 新一级行业二级行业表（201809）
CREATE TABLE IF NOT EXISTS industry_new (
  id int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
  industry_level tinyint NOT NULL DEFAULT 1 COMMENT '行业分级，（1 一级行业| 2 二级行业）',
  parent_id int(10) NOT NULL DEFAULT 0 COMMENT '1，一级行业为0。2，二级行业对应一级行业的ID。',
  industry_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '行业名称',
  status TINYINT NOT NULL DEFAULT '1' COMMENT '是否有效(1-有效，0-无效)',
  create_time DATETIME NOT NULL DEFAULT current_timestamp COMMENT '创建时间',
  update_time DATETIME NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp COMMENT '更新时间'
) ENGINE=InnoDB CHARSET=utf8 COMMENT='新一级行业二级行业表';

-- 新行业对应的职位表（201809）
CREATE TABLE IF NOT EXISTS position_new (
  id int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
  industry_id int(10) NOT NULL DEFAULT 0 COMMENT '职位所属的一级行业ID,industry_new.id',
  position_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '职位名称',
  status TINYINT NOT NULL DEFAULT '1' COMMENT '是否有效(1-有效，0-无效)',
  create_time DATETIME NOT NULL DEFAULT current_timestamp COMMENT '创建时间',
  update_time DATETIME NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp COMMENT '更新时间'
) ENGINE=InnoDB CHARSET=utf8 COMMENT='新职位表';


