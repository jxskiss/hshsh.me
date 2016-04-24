+++
Categories = ["Hugo"]
Description = ""
Tags = ["hugo"]
date = "2016-04-24T11:36:14+08:00"
menu = "main"
title = "welcome to my hugo blog"

+++

Welcome to my new [Hugo](https://gohugo.io/) blog.

## 为什么又建一个博客

其实在07年开始的时候就建立了自己的博客，当时是在百度空间，内容主要是网上转载的学习资料。百度空间的排版真心费劲。后来百度空间倒下了，内容也都没有了。

后来，GAE开始流行，作为Google忠实的粉丝和一个不折腾会死星人，当然得尝试尝试了。博客搭建好了，但是却没写出什么东西来，一两年时间里，也只有寥寥数篇生活杂记。这时候，我还买了一个自己的域名。

时间大概是08年。又后来，Google退出中国，服务越来越难访问，也就没管那个站了，甚至现在都想不起来GAE上的那个二级域名是什么了。

然后，Github很火，很多人开始在Github Pages上搭建博客。了解之后，一下子又被吸引了，用Markdown书写的感觉特别爽，排版也漂亮，对代码高亮等扩展功能的支持也好。大概是13年的时候使用Jekyll在Github Pages上又搭建了一个博客，还把以前的一些乱七八糟的文字整理了过去，并且绑定了之前买的域名。这个网站现在还能访问：<http://www.imwsh.net>。

（号外：要是有人喜欢`imwsh.net`这个域名，联系我哈，便宜出售~ ~）

Github Pages上的博客搭好了，但是我却是跟IT越走越远，工作在传统行业，又跑去拉萨野了一趟，人又懒得很，也就不了了之了。

今年过完春节，贼心不死的我又在纠结工作的事情，最终在老婆和朋友的鼓励下，成功的找到了一份后端程序员的工作。于是乎又开始学习恶补，又惦记起来博客的事情，翻翻硬盘，那个博客的源码都已经被删了，而且对Ruby也不熟悉。当时正在学习Flask Web开发，干脆自己用Python写一个得了。

于是乎，互联网上便又多了一个博客程序：[meblog](https://github.com/jxskiss/meblog)。

这个博客程序简单漂亮，也非常好用，代码高亮、标签、分类什么的都支持，我自己对这个博客程序也很满意，还写了一个命令行推送发布工具，然后爽歪歪的把博客部署到SAE上去了，好事不长久，还不到一个月，在新浪云上充值的豆子就用完了，于是乎，拉倒吧……不过，这个meblog却真的是麻雀很小，五脏俱全，如果有人需要一个Python写的博客程序的话，我强烈推荐！如果还能打开的话，你可以看看她长什么样：<http://hshsh.applinzi.com>

然后，了解到了hugo这个静态博客生成器，markdown书写、单文件执行、没有依赖，同样可以方便的部署到Github Pages。看起来就很好用啊，官方网站做的还很漂亮，干脆再搭一个博客算了。这便是现在这个博客了，轻车熟路整理markdown文件，生成网站，调整CSS样式，绑定域名，半天时间，网站就上线了。

另外，我还简单写了一个[自动部署脚本](https://github.com/jxskiss/hshsh.me/blob/master/fabfile.py)，可以自动转换发布Jupyter Notebook文件哦。用Jupyter Notebook写笔记，然后自动发布称漂亮的网站，简直爽的不要不要的 ~ ~

至于搭建博客的过程，并不复杂，这里就不复制粘贴了，直接看下面的参考资料吧。

## 参考资料

- [Hugo - Hosting on GitHub Pages](https://gohugo.io/tutorials/github-pages-blog/)：这个是主要参考资料
- [使用Hugo搭建免费个人Blog](http://ulricqin.com/post/how-to-use-hugo/)
- [使用Hugo + Github搭建个人博客](http://www.jianshu.com/p/b66754c0baa6)

