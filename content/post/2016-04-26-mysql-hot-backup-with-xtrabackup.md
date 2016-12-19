+++
Categories = ["Database"]
Description = ""
Tags = ["ubuntu", "mysql", "database", "xtrabackup"]
date = "2016-04-26T18:30:00+08:00"
menu = "main"
title = "XtraBackup热备份MySQL主从同步笔记"

+++

公司的MySQL数据库单实例裸跑了一个多月，今天终于做了主从同步，暂时主要起备份作用，庆幸这段时间没有发生意外。

先说主要的参考资料，强烈推荐阅读：

- [XtraBackup不停机不锁表搭建MySQL主从同步实践](http://wsgzao.github.io/post/xtrabackup/)
- [使用 Xtrabackup 在线对MySQL做主从复制](http://seanlook.com/2015/12/14/mysql-replicas/)
- [通过XtraBackup实现不停机不锁表搭建主从同步](https://segmentfault.com/a/1190000002575399)

**更新历史**:

2016-04-26: 初稿.

2016-12-19:

  1. 修复 innobackupex 命令错误: "xtrabackup: Error: --defaults-file must be specified first on the command line".
  2. 添加 "主从复制心跳和连接超时" 内容.

## 简介

转载一下主从同步和XtraBackup的简介：

**MySQL主从同步原理**

MySQL主从同步是在MySQL主从复制(Master-Slave Replication)基础上实现的，通过设置在Master MySQL上的binlog(使其处于打开状态)，Slave MySQL上通过一个I/O线程从Master MySQL上读取binlog，然后传输到Slave MySQL的中继日志中，然后Slave MySQL的SQL线程从中继日志中读取中继日志，然后应用到Slave MySQL的数据库中。这样实现了主从数据同步功能。

**XtraBackup备份原理**

innobackupex在后台线程不断追踪InnoDB的日志文件，然后复制InnoDB的数据文件。数据文件复制完成之后，日志的复制线程也会结束。这样就得到了不在同一时间点的数据副本和开始备份以后的事务日志。完成上面的步骤之后，就可以使用InnoDB崩溃恢复代码执行事务日志（redo log），以达到数据的一致性。

备份分为两个过程：

1. backup，备份阶段，追踪事务日志和复制数据文件（物理备份）。
2. preparing，重放事务日志，使所有的数据处于同一个时间点，达到一致性状态。

**XtraBackup的优点**

1. 可以快速可靠的完成数据备份（复制数据文件和追踪事务日志）
2. 数据备份过程中不会中断事务的处理（热备份）
3. 节约磁盘空间和网络带宽
4. 自动完成备份鉴定
5. 因更快的恢复时间而提高在线时间

## 操作笔记

参考的两篇文章里面说的挺详细的，但是有部分命令和命令执行顺序写的不大明白，这里简单记录以下。

**完整的步骤**

1. 主、从服务器上都搭好MySQL服务，从服务器上MySQL版本大于等于主服务器，最好完全一致
2. 在要做主从同步的服务器上分别安装XtraBackup
3. 如果从服务器上有MySQL实例，停掉服务，备份删除数据库内容，保留数据库目录
4. 配置主从服务器打开主从同步功能
5. 主服务器上执行备份
6. 传输备份文件到从服务器，并同步数据文件（apply-log）
7. 从服务器上恢复备份
8. 主服务器上授权同步帐号
9. 从服务器上设置MASTER并开启同步

完成，可以检查同步状态了！

**具体操作过程**

NOTE：以下命令以普通用户权限运行，如果需要ROOT权限，均使用`sudo`执行。默认均使用Ubuntu发行版仓库中的MySQL，版本比较旧，如果使用官方发行版本，需要注意相关选项、目录等配置。

一、主从服务器上搭建MySQL服务，并检查MySQL版本：

```bash
# master & slave
sudo apt-get install mysql-server
mysql --version
```

> mysql  Ver 14.14 Distrib 5.5.49, for debian-linux-gnu (x86_64) using readline 6.3

二、主从服务器上分别安装XtraBackup，根据官方网站指导使用打包好的二进制，选择最新的稳定版2.4：

```bash
# master & slave
wget https://repo.percona.com/apt/percona-release_0.1-3.$(lsb_release -sc)_all.deb
sudo dpkg -i percona-release_0.1-3.$(lsb_release -sc)_all.deb
sudo apt-get update
sudo apt-get install percona-xtrabackup-24
```

三、停掉从服务器上MySQL服务，备份原有数据库，并删除原有数据库内容：

```bash
mysqldump -u$USER -p$PASSWORD -h127.0.0.1 -P3306 --routines \
  --default-character-set=utf8 --locak-all-tables --add-drop-database -A \
  db.all.sql
sudo service mysql stop
sudo cd /var/lib/mysql
# 下面这句千万别打错了，后果会很严重
sudo rm -rf ./*
```

四、配置MySQL打开主从同步功能

主服务器上编辑`/etc/mysql/my.conf`文件：

```conf
[mysqld]
# 注意主从之间的server-id不能相同
server-id    = 1
log_bin      = /var/log/mysql/mysql-bin.log
```

如果主服务器上MySQL是已经上线的系统，需要重启一下（实测`/etc/init.d/mysql reload`不起作用）：

```bash
sudo service mysql restart
```

从服务器上编辑`/etc/mysql/my.conf`文件：

```conf
[mysqld]
# 注意主从之间的server-id不能相同
server-id    = 2
# 最好设置从服务器为只读
# 注意：即使这里设置了只读，使用具有super权限的用户登录，也还是可以做写操作的
read_only    = ON
```

查询主从服务器状态：

```bash
mysql -u USER -p PASSWD -e "show global variables like 'server-id';"
    +---------------+-------+
    | Variable_name | Value |
    +---------------+-------+
    | server_id     | 1     |
    +---------------+-------+

mysql -u USER -p PASSWD -e "show global variables like 'log_bin';"
    +---------------+-------+
    | Variable_name | Value |
    +---------------+-------+
    | log_bin       | ON    |
    +---------------+-------+
```

五、主服务器上执行备份操作

```bash
sudo innobackupex --defaults-file=/etc/mysql/my.cnf --user=USER --password \
  --parallel=4 /tmp/mybackup
```

命令输出的最后几行通常类似这样：

```
innobackupex: Backup created in directory '/tmp/mybackup/2016-04-26_17-41-51'
innobackupex: MySQL binlog position: filename 'mysql-bin.000003', position 1946
111225 00:00:53 innobackupex: completed OK!
```

命令执行完在`/tmp/mybackup`目录下生成的`2016-04-26_17-41-51`目录，里面存储的是备份的数据，下一步要传输到从服务器上的即是这个文件夹。

输出中的`MySQL binlog position: filename 'mysql-bin.000003', position 1946`里面的两个数字，要记录以下，后面恢复到从服务器上的时候要用到。

六、传输并同步备份数据

读取备份数据需要ROOT权限，下面的命令需要使用sudo执行。

```bash
mkdir /tmp/mybackup
sudo scp -r /tmp/mybackup/2016-04-26_17-44-49 USER@SLAVE:/tmp/mybackup/2016-04-26
```

在从服务器上执行：

```bash
sudo innobackupex --apply-log /tmp/mybackup/2016-04-26
```

七、从服务器上恢复备份数据

```bash
# 恢复数据
sudo innobackupex --defaults-file=/etc/mysql/my.cnf --user=USER --password \
  --copy-back /tmp/mybackup/2016-04-26/
# 需要恢复权限给mysql
sudo chown -R mysql:mysql /var/lib/mysql
# 启动MySQL
sudo service mysql start
```

NOTE: 如果从数据库存在多个MySQL，执行命令有所不同，请另行查阅相关资料。

八、主服务器上授权同步帐号

```sql
mysql -u USER -p PASSWD -h HOST -P PORT
> grant replication slave on *.* to 'slave'@'10.10.16.24' identified by 'slave_passport';
> flush privileges;
>
> select distinct concat('User: ''',user,'''@''',host,''';') as query from mysql.user;
>
```

最后一条语句查询当前数据库中的用户信息，检查`slave_passport`是否在其中。

九、配置从服务器开启同步

```sql
mysql -u USER -p PASSWD -h HOST -p PORT
> change master to
> master_host = '10.10.16.51',
> master_user = 'slave',
> master_password = 'slave_password',
> master_port = 3306,
> master_log_file = 'mysql-bin.000003',
> master_log_pos = 1946;
>
> start slave;
```

查看主库同步状态：

```bash
mysql -u USER -p PASSWD -h MASTER_HOST -P MASTER_PORT \
  -e "show master status \G;"
mysql -u USER -p PASSWD -h SLAVE_HOST -P SLAVE_PORT \
  -e "show processlist \G;" | grep -i 'master'
```

检查第二条命令输出是否类似“State: Master has sent all binlog to slave; waiting for binlog to be updated”这样。


查看从库同步状态：

```bash
mysql -u USER -p PASSWD -h SLAVE_HOST -P SLAVE_PORT \
  -e "show slave status \G;"
mysql -u USER -p PASSWD -h SLAVE_HOST -P SLAVE_PORT \
  -e "show processlist \G;" | egrep -i '(master|slave)'
```

检查命令输出是否包含类似下面这样的语句：

```
Slave_IO_State: Waiting for master to send event
Slave_IO_Running: Yes
Slave_SQL_Running: Yes
Slave_SQL_Running_State: Slave has read all relay log; waiting for the slave I/O thread to update it

State: Waiting for master to send event
State: Slave has read all relay log; waiting for the slave I/O thread to update it
```

## MySQL主从切换

这里暂时还没有用到主从切换，不过参考资料[XtraBackup不停机不锁表搭建MySQL主从同步实践](http://wsgzao.github.io/post/xtrabackup/)中有写到主从切换的过程，复制粘贴一下以后好找：

```sql
#查看主库状态
show processlist;
Master has sent all binlog to slave; waiting for binlog to be updated
show master status \G

#从库停止 IO_THREAD 线程
stop slave IO_THREAD;
show processlist;
Slave has read all relay log; waiting for the slave I/O thread to update it
show slave status \G

#从库切换为主库
stop slave;
reset master;
reset slave all;
show master status \G

#激活帐户
SELECT DISTINCT CONCAT('User: ''',user,'''@''',host,''';') AS query FROM mysql.user;
GRANT REPLICATION SLAVE ON *.* TO 'slave_passport'@'10.10.16.51' IDENTIFIED BY 'slave_passport';
FLUSH PRIVILEGES;

#切换原有主库为从库
reset master;
reset slave all;

CHANGE MASTER TO
MASTER_HOST='10.10.16.24',
MASTER_USER='slave_passport',
MASTER_PASSWORD='slave_passport',
MASTER_PORT=3306,
MASTER_LOG_FILE='mysql-bin.000001',
MASTER_LOG_POS=804497686;

#检查主库
SHOW PROCESSLIST;
show master status \G

#启动从库
SHOW PROCESSLIST;
start slave;
show slave status \G
```

## 2016-12-19更新: 主从复制心跳和连接超时

实际运行过程中, 由于没有专门的人做运维, 从服务器也只是起备份作用, 偶尔发现从服务器已经没有跟主服务器同步, 数据滞后了很长时间了, 估计是跟公司网络环境不大稳定有关系.

在网上了解到MySQL 5.5以上版本的主从复制还有一个心跳功能, 参考这里: [MySQL运维-主从复制心跳](http://blog.csdn.net/JesseYoung/article/details/42914577). 果断打开心跳功能.

连接从服务器, 执行下面指令配置心跳周期和连接超时:

```
mysql> stop slave;
mysql> change master to master_heartbeat_period = 10;
mysql> set global slave_net_timeout = 25;
mysql> start slave;
```

可以通过以下命令检查心跳状态:

```bash
mysql -uUSER -pPASSWORD -hHOST -PPORT -e "show status like 'slave%';"
    +----------------------------+--------+
    | Variable_name              | Value  |
    +----------------------------+--------+
    | Slave_heartbeat_period     | 10.000 |
    | Slave_last_heartbeat       |        |
    | Slave_open_temp_tables     | 0      |
    | Slave_received_heartbeats  | 0      |
    | Slave_retried_transactions | 0      |
    | Slave_running              | ON     |
    +----------------------------+--------+
```
