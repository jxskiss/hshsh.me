+++
Categories = ["Software", "Photoshop"]
Description = "Fix can not load extension due to incorrect signature"
Tags = ["windows", "software", "photoshop"]
date = "2016-12-22T23:30:00+08:00"
menu = "main"
title = "解决Photoshop CC 2017无法安装扩展插件的问题"

+++

安装Photoshop CC 2017后，打开PNG文件，弹出“无法加载扩展，因为它未正确签署”的错误提示，解决方法如下：

打开注册表编辑器，定位到路径“HKEY_CURRENT_USER/Software/Adobe/CSXS.7”，新建“字符串值”，名称为“PlayerDebugMode”，值为1。

关闭注册表，收工。重新打开Photoshop，可以正常安装加载扩展了。

或者可以保存以下内容为“ps2017_extensions_fix.reg”文件，并双击导入注册表：

```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\SOFTWARE\Adobe\CSXS.7]
"PlayerDebugMode"="1"
```

下面参考资料文章中有动图指导，推荐拜读原文。

参考资料：

* [一招解决PSCC2017无法安装扩展插件(原创文章)](http://www.zcool.com.cn/article/ZNDUwODY0.html)
