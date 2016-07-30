+++
Categories = ["Python"]
Description = "Using tsinghua anaconda mirror"
Tags = ["python", "anaconda"]
date = "2016-07-30T07:00:00+08:00"
menu = "main"
title = "使用清华大学Anaconda镜像"

+++

Python的Anaconda发行版用起来真是舒服，可是官方源的速度真可谓是龟速，一直也没找到国内的镜像源。
早上看到IPython更新到5.0LTS版本，看起来很爽，不死心的又查了一下，发现[清华大学2016年4月27日新增了Anaconda的镜像](https://mirrors.tuna.tsinghua.edu.cn/news/#alpine-anaconda)，果断切换。

看这里：<https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/>

```bash
conda config --add channels 'https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/'
conda config --set show_channel_urls yes
```
