+++
Categories = ["Linux"]
Description = ""
Tags = ["linux", "ubuntu", "shell"]
date = "2016-04-27T12:00:00+08:00"
update = "2016-05-20T10:15:00+08:00"
menu = "main"
title = "Ubuntu & Linux 常用命令笔记"

+++

## 系统配置

### 安装 Oracle JDK

```sh
$ sudo add-apt-repository ppa:webupd8team/java
$ sudo apt-get update
$ sudo apt-get install oracle-java8-installer
$ sudo apt-get install oracle-java8-set-default
```

### 永久性修改系统DNS

编辑`/etc/network/interfaces`文件，在最后添加一行：

```conf
dns-nameservers 8.8.8.8 8.8.4.4
```

或者可以修改`/etc/resolvconf/resolv.conf.d/base`文件，默认为空，在其中插入：

```conf
nameserver 8.8.8.8
nameserver 8.8.4.4
```

如果有多个DNS，就每行添加一个。

NOTE：亲测，以上设置，需要重启系统后生效！

## 常用命令行工具

### 查看进程

```sh
$ ps ax
$ ps aux
$ ps ax | less
$ ps ax | grep ...
```

### 查看端口

```sh
$ netstat -tap | grep ...
$ netstat -na | grep ...
$ ss -tln | grep ...
```

查看指定进程占用的端口号：

```sh
$ ps -ef | grep "process name"
```

根据进程ID查看招用端口号：

```sh
# redhat
$ netstat -nltp | grep pid
# ubuntu
$ netstat -anp | grep pid
```

查看占用某个端口的进程：

```sh
$ lsof -i:port
```

### 监控日志文件

```sh
$ tail -f /path/to/file.log
```

### 重启 X Server

```sh
$ cat /etc/X11/default-display-manager
$ sudo restart {DISPLAY_MANAGER}
```

### 输出重定向

```sh
$ cat foo > foo.txt  # 重定向标准输出到文件
$ cat foo 2> foo.txt  # 重定向错误输出到文件
$ cat foo 2>&1  # 重定向错误输出到标准输出
$ cat foo > foo.txt 2>&1  # 重定向标准输出和错误输出到文件
```

如果要写入的文件权限不够，可以这样（`-a`选项表示追加内容到文件）：

```sh
$ sudo sh -c "echo 'xxx'" > /path/to/somefile
$ echo 'xxx' | sudo tee -a /path/to/somefile
```

