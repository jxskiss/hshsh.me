+++
Categories = ["Database"]
Description = "Fix postgresql permission issue again"
Tags = ["database", "postgresql", "service"]
date = "2016-08-06T10:17:25+08:00"
menu = "main"
title = "升级Windows导致Postgresql服务无法启动问题"

+++

这两天升级系统到了Windows 10.1，结果Postgresql数据库又起不来了，之前重做Windows 7的时候就遇到过这个问题，但是不记得是怎么搞定的了。

查了一堆资料，基本断定问题是由于升级操作系统后，Windows建立新用户，用户SID改变导致的。可是网上始终也没有找到个有效的解决方法。记得上次就是这样，最后只能再次祭出大招，下载EnterpriseDB的安装包，重装一遍，查看它的服务进程登录用户和文件目录权限。

这里记录一下，以免下次又忘了：

* 服务进程登录用户："NT AUTHORITY\NetworkService"
* 服务进程启动命令：C:/path/to/pg_ctl.exe runservice -N "pgsql" -D "E:/path/to/data" -w
* 数据目录OWNER：Administrators (COMPUTER\Administrators)

另外数据目录上要确保下面两个权限：

* NETWORK SERVICE：完全控制
* 本地登录用户（COMPUTER\username）：完全控制

其他的权限系统默认就行了，具体权限设置就不记录了，从Cygwin开始就对着权限搞来搞去，现在Postgresql又搞权限问题，已经是轻车熟路了。
