+++
Categories = ["Linux"]
Description = ""
Tags = ["linux"]
date = "2016-04-02T22:33:15+08:00"
menu = "main"
title = "Linux常用打包解包命令备忘"

+++

## .tar

打包： `tar cvf file.tar dirname`

解包： `tar xvf filename.tar`

## .gz

打包： `gzip dirname`

解包： `gzip -d filename.gz`

## .tar.gz

打包： `tar zcvf file.tar.gz dirname`

解包： `tar zxvf file.tar.gz`

## .tar.bz2

打包： `tar jcvf file.tar.bz2 dirname`

解包： `tar jxvf filename.tar.bz2` or `tar jxvf filename.tar.bz`

## .zip

打包： `zip file.zip dirname`

解包： `unzip filename.zip`

## .rar

安装： `sudo apt-get install rar`

打包： `rar e dirname`

解包： `rar a filename.rar`

## .z

打包： `compress dirname`

解包： `uncompress filename.z`

## .tar.Z

打包： `tar Zcvf file.tar.Z dirname`

解包： `tar Zxvf filename.tar.Z`

## .tgz

解包： `tar zxvf filename.tgz`

## .tar.tgz

打包： `tar zcvf file.tar.tgz dirname`

解包： `tar zxvf filename.tar.tgz`

