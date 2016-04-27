+++
Categories = ["Database"]
Description = ""
Tags = ["mysql", "database"]
date = "2016-04-27T11:42:00+08:00"
menu = "main"
title = "MySQL & SQL 常用命令笔记"

+++

## 查看数据库和数据表结构

```sh
$ mysql -u user -p
mysql> show databases;
mysql> show tables;
mysql> use {DATABASE_NAME};
mysql> show columns from {TABLE_NAME};
mysql> show create table {TABLE_NAME};
mysql>
```

## 变更数据表结构

```sql
# 重命名字段并可选修改字段类型
alter table {TABLE_NAME} change {OLD_COLUMN} {NEW_COLUMN} {COLUMN_TYPE};
# 修改字段类型不重命名字段
alter table {TABLE_NAME} modify {COLUMN_NAME} {COLUMN_TYPE};
# 增加字段
alter table {TABLE_NAME} add column {COLUMN_NAME} {COLUMN_TYPE};
# 删除字段
alter table {TABLE_NAME} drop column {COLUMN_NAME};
```

## 快速批量加载数据到数据库

**NOTE**: 下面命令中`{...}`表示必填参数，`[...]`表示选项参数

```sql
# 逗号分隔的 csv 文件, 字段列表可选
load data local infile "/path/to/file.csv" into table {TABLE_NAME}
fileds terminated by ',' [(field1, field2, field3, ...)];
# 制表符分隔的 txt 文件, 字段列表可选
laod data local infile "/path/to/file.txt" into table {TABLE_NAME}
[(field1, field2, field3, ...)];
```

可能会遇到`ERROR 1148 (42000): The used command is not allowed with this
MySQL version`的错误提示，错误原因是编译安装`mysql`的时候没有指定`--enable-local-infile`
选项，除了重新编译安装加上上面的参数外，还可以直接使用命令行执行：

```sh
$ mysql -u user -p {DATABASE_NAME} --local-infile=1 -e 'load data local \
  infile "/path/to/file.txt" into {TABLE_NAME} [(field1, field2, field3, ...)];'
```

## 数据库导出操作

导出全部数据库备份到本地目录:

```sh
$ mysqldump -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --routines \
  --default-character-set=utf8 --locak-all-tables --add-drop-database -A \
  > db.all.sql
```

导出指定数据库到本地目录：

```sh
$ mysqldump -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --routines \
  --default-character-set=utf8 --databases {DATABASE_NAME} > db.sql
```

导出某个数据库的表到本地目录：

```sh
$ mysqldump -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --routines \
  --default-character-set=utf8 --tables {DATABASE_NAME} {TABLE_NAME} \
  > db.table.sql
```

导出指定数据库的表（仅数据，可带过滤条件）到本地目录：

```sh
$ mysqldump -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --routines \
  --default-character-set=utf8 --no-create-db --no-create-info \
  --tables {DATABASE_NAME} {TABLE_NAME} \
  [--where="host='localhost'"] > db.table.sql
```

导出数据库的所有表结构：

```sh
$ mysqldump -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --routines \
  --default-character-set=utf8 --no-data --databases {DATABASE_NAME} \
  > db.nodata.sql
```

导出某个查询SQL的数据为 txt 格式文件到本地目录，各数据值之间用制表符分隔：

```sh
$ mysql -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --default-character-set=utf8 \
  --skip-column-names -B -e 'select ... from ... ;' > /path/to/file.txt
```

导出某个查询SQL的数据为 csv 格式文件到服务器：

```sh
$ mysql -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --default-character-set=UTF8
mysql> select ... from ... into outfile '/path/to/file.csv' fields terminated by ',';
mysql>
```

## 数据库导入操作

恢复全库数据到MySQL，因为包含mysql库的权限表，导入完成后需要执行
`FLUSH PRIVILEGES;`命令：

```sh
$ mysql -u$USER -p$PASSWORD -h127.0.0.1 -P3306 \
  --default-character-set=UTF8 < db.all.sql

# 方法二
$ mysql -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --default-=character-set=UTF8
mysql> source /path/to/db.all.sql
mysql> flush privileges;
```

恢复某个数据库：

```sh
$ mysql -u$USER -p$PASSWORD -h$HOST -P$PORT --default-character-set=UTF8 \
  {DATABASE_NAME} < db.table.sql

# 方法二
$ mysql -u$USER -p$PASSWORD -h$HOST -P$PORT --default-character-set=UTF8
mysql> use {DATABASE_NAME};
mysql> source /path/to/db.table.sql;
```

恢复MySQL服务器上面的 txt 格式文件（需要FILE权限，数据值之间用制表符分隔）：

```sh
$ mysql -u$USER -p$PASSWORD -h$HOST -P$PORT --default-character-set=UTF8
mysql> use {DATABASE_NAME};
mysql> load data infile '/path/to/file.txt' into table {TABLE_NAME};
mysql>
```

恢复MySQL服务器上的 csv 格式文件（需要FILE权限，数据值之间用逗号分隔）：

```sh
$ mysql -u$USER -p$PASSWORD -h$HOST -P$PORT --default-character-set=UTF8
mysql> use {DATABASE_NAME};
mysql> load data infile '/path/to/file.csv' into table {TABLE_NAME}
mysql> fields terminated by ',';
mysql>
```

恢复本地的 txt 或 csv 文件到MySQL：

```sh
$ mysql -u$USER -p$PASSWORD -h$HOST -P$PORT --default-character-set=UTF8
mysql> use {DATABASE_NAME};
mysql> load data local infile '/path/to/file.txt' into table {TABLE_NAME};
mysql> load data local infile '/path/to/file.csv' into table {TABLE_NAME}
mysql> fields terminated by ',';
mysql>
```

## 常用命令参数说明

mysqldump参数说明：

1. **-A**: 全库备份
2. **--routines**: 备份存储过程和函数
3. **--default-character-set=utf8**: 设置连接字符集
4. **--lock-all-tables**: 全局一致性锁
5. **--add-drop-database**: 在每次执行建表语句之前，先执行`drop table if exist`语句
6. **--no-create-db**: 不输出`create database`语句
7. **--no-create-info**: 不输出`create table`语句
8. **--databases**: 将后面的参数都解析为数据库名
9. **--tables**: 第一个参数为数据库名，后续参数为数据表名

mysql参数说明：

1. **--skip-column-names**: 不显示数据列的名字
2. **-B**: 以批处理的方式运行mysql程序，查询结果将显示为制表符间隔格式
3. **-e**: 执行命令后退出

`LOAD DATA`语法：

1. 如果`LOAD DATA`语句不带`LOCAL`关键字，就在MySQL的服务器上直接读取文件，
   需要具有FILE权限
2. 如果带有`LOCAL`关键字，就在客户端本地读取数据文件，通过网络传输到MySQL
3. `LOAD DATA`语句，同样会被记录到`binlog`，不过是MySQL内部的机制

## 设置默认使用utf8编码

```conf
# configuration in file /etc/mysql/my.cnf
[client]
# 客户端连接
default-character-set = utf8
[mysql]
# 命令行工具
default-character-set = utf8
[mysqld]
# 服务器默认字符集
character-set-server = utf8
```

## mysqld 服务管理

```sh
$ sudo service mysql {start | stop | restart}
$ sudo /etc/init.d/mysql {start | stop | restart}

# safe 模式启动
$ sudo safe_mysqld &

# mysqld 守护进程管理程序.
$ mysqladmin shutdown
$ mysqladmin --help
```
