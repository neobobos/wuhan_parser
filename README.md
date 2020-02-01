# wuhan_parser
武汉疫情数量与新闻数据爬取

#### 确诊与死亡病例数据来自百度

#### 新闻信息来自丁香园

### 环境 python3.6.5

### 主要安装包
```
import requests
import re
import time
import re
from lxml import etree
import json
import pymysql
import operator
```
### 结果表mysql table结构，用于存储爬取的数据。
##### sarl 全国城市确诊数量表
``` 
/*
CREATE TABLE `sarl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provinceShortName` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `city` text,
  `confirmedCount` int(255) DEFAULT NULL,
  `suspectedCount` int(255) DEFAULT NULL,
  `curedCount` int(255) DEFAULT NULL,
  `deadCount` int(255) DEFAULT NULL,
  `modifyTime` varchar(255) DEFAULT NULL,
  `insert_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

*/
```
##### sarl_news新闻表
```
/**
CREATE TABLE `sarl_news` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pubDateStr` varchar(255) DEFAULT NULL,
  `pubDate` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `summary` text,
  `infoSource` varchar(255) DEFAULT NULL,
  `sourceUrl` varchar(255) DEFAULT NULL,
  `provinceId` varchar(255) DEFAULT NULL,
  `provinceName` varchar(255) DEFAULT NULL,
  `createTime` varchar(255) DEFAULT NULL,
  `modifyTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
**/
```
