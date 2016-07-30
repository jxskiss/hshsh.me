+++
Categories = ["Ubuntu"]
Description = "Using aliyun mirror for ubuntu 14.04"
Tags = ["linux", "ubuntu"]
date = "2016-07-30T07:20:00+08:00"
menu = "main"
title = "Ubuntu 14.04 使用阿里云源"

+++

Ubuntu的官方源也是慢的不行不行的，怎么办？换阿里云的源，速度杠杠的！

```sh
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak  # 备份
sudo vim /etc/apt/sources.list  # 修改配置
sudo apt-get clean && sudo apt-get update  # 更新列表
```

修改源配置如下：

```txt
deb http://mirrors.aliyun.com/ubuntu/ trusty main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ trusty-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ trusty-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ trusty-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ trusty-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-backports main restricted universe multiverse

## Uncomment the following two lines to add software from Canonical's
## 'partner' repository.
## This software is not part of Ubuntu, but is offered by Canonical and the
## respective vendors as a service to Ubuntu users.
# deb http://archive.canonical.com/ubuntu trusty partner
# deb-src http://archive.canonical.com/ubuntu trusty partner

## This software is not part of Ubuntu, but is offered by third-party
## developers who want to ship their latest software.
deb http://extras.ubuntu.com/ubuntu trusty main
deb-src http://extras.ubuntu.com/ubuntu trusty main
deb http://packagecloud.io/grafana/testing/debian/ wheezy main
```
