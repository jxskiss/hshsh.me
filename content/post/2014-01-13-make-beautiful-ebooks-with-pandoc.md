+++
Categories = ["Software"]
Description = ""
Tags = ["pandoc", "ebooks"]
date = "2014-01-13T10:38:00+08:00"
menu = "main"
title = "使用Pandoc制作精美的EPUB、MOBI、PDF电子书"

+++

## 缘起

在亚马逊上购买了一部 Kindle Paperwhite，设备还没有拿到手，就先在网上找一找电子书。结果是网络上的电子书资源确实是不少，但是质量确是参差不齐，只有少数书籍排版精美，书签完整，大多数简直惨不忍睹，可以说严重影响阅读体验。

之前接触到了Pandoc这个文本格式转换的瑞士军刀，知道它可以简便的输出HTML、PDF、EPUB、DOCX等等各类格式，所以就想着能不能自己动手制作排版精美的电子书。经过一番探索，发现可以使用Pandoc和KindleGen非常方便的制作排版精良的电子书。本着造福买不起纸质书的广大群众的意愿，将所得方法及操作技巧发布出来，于是有了本文。


## 简便制作和精美电子书的定义

**简便制作**：

* 从网络上到处可以下载到的TXT格式可以方便的转换为排好版的电子书
* 源文件一次整理，可以直接输出为不同格式的电子文档，比如通过一条命名，或者一两次鼠标点击
* 简单方便的控制书籍排版格式（全书格式统一），比如通过一个CSS文件
* 修改书籍内容时，不影响书籍排版格式

**精美电子书**：

* 带有目录，支持EPUB、MOBI阅读软件导航功能
* 标题、正文、引用字段使用不同字体区分，便于识别阅读
* 段落距离、缩进与行距设置适中，便于识别阅读
* 整书排版格式统一，清晰易读，无过多分散注意力的元素

----

## 相关技术说明

这里应该先从Markdown说起，作为一种轻量级的标记语言，Markdown很适合用来写作，能够让作者把精力集中在书籍的内容撰写上面，而不会被排版等问题分散精力。在一份典型的Markdown文件中，作者使用简单的符号来标记诸如标题、段落、引用、列表、图表等等结构元素，而不记录排版相关的内容。具体的排版工作留给编译器来处理，也就是在从Markdown源文件输出HTML、PDF、EPUB等出版格式的时候才确定，并且可以简便的通过格式控制指令（CSS文件、Latex模板）来控制排版格式。Pandoc就是这么一个编译器，它与其它Markdown解释器相比，有它自己的优点：扩展的Markdown的语法，弥补了Markdown语法结构简单的问题；可以生成很多种格式的文件，甚至Word文档也可以；使用模板控制输出结果，定制简单，等等。关于Markdown和Pandoc的更多信息，请参阅本节的[拓展阅读](#markdown-pandoc-readings)和文末的[参考资料](#foot-reference)。

对于使用OCR或者网络下载的TXT文件制作电子书来说，并不需要掌握Markdown和Pandoc的全部知识，只需要知道基本的Markdown语法就行了：标题、段落、引用、列表、图表等，这些很简单，查看Markdown的语法说明，一会儿就能掌握。按照Markdown的语法对TXT文件进行格式化，然后使用本文中展示的模板文件和编译命令，就可以直接输出为EPUB、MOBI、PDF（A4、6寸，或者其它定制尺寸）文件了。

生成EPUB是Pandoc原生自带的功能，只需要在源文件中填入相关的metadata属性，整理好书籍内容，直接一条命名就OK了。

生成MOBI使用亚马逊的KindleGen软件，由上面生成的EPUB文件为参数转换而来，生成的MOBI文件同时包含旧的MOBI格式和新的KF8格式，可以直接向Amazon网上商店发布，也可以使用Calibre软件（需要安装MobiUnpack插件）拆分为单独的MOBI和AZW3文件。

生成6寸或A4尺寸的PDF，也是Pandoc原生自带的功能，Pandoc根据源文件生成Latex文件，然后使用Latex来生成PDF文件。Latex生成的PDF质量高、排版精美是众所周知的，但是它的语法非常复杂，学习曲线陡峭，把一般用户远远地挡在了大门外。现在有了Pandoc，我们就可以以非常少的工作享用Latex输出的高质量PDF了，当然了这需要Latex软件，只要安装Pandoc用户指南中推荐的[MikTex][]即可。不同尺寸的PDF只需要在运行pandoc命令时指定相应的模板文件就行了。

[MikTex]: http://miktex.org/

<span id="markdown-pandoc-readings"></span>
关于Markdown和Pandoc的拓展阅读：

1. [Markdown - 维基百科](http://zh.wikipedia.org/wiki/Markdown)
1. [Markdown+Pandoc 最佳写作拍档](http://iout.in/archives/454.html)

----

## 操作步骤

前面已经把使用到的程序，相关的原理都已经交代了，实际上真正操作起来，步骤非常简单。

### 安装使用到的软件

**安装Pandoc**：

从Pandoc官方网站[下载适用于Windows的安装包](https://code.google.com/p/pandoc/downloads/list)安装，下一步、下一步，就OK了[^fn-pandoc]。

[^fn-pandoc]: 撰写本文时，Pandoc最新版本为 1.12.3

**安装MikTex**：

从[MikTex][]官方网站下载MikTex安装包进行安装，可以选择安装版本或者便携版本均可。 如果选择使用便携版本，需要把MikTex的执行文件路径添加到系统路径中。

### 整理源文件

用Pandoc的语法把文章的结构标记出来，各章节标题、引用、表格、插图等等。并把书籍内容文件命名为 `book.md` 。如果对正则表达式熟悉的话，这里可以使用sed或者其它编辑器对文件进行批量处理。这不是本文的讨论内容，这里就不再详述，如果有兴趣，请自行查阅相关资料。

添加EPUB元数据到 `meta.md` 文件，这里使用markdown文件中内嵌的YAML来书写，详见[Pandoc用户指南中的EPUB元数据部分](http://johnmacfarlane.net/pandoc/README.html#epub-metadata)和本文样书源文件中的 `meta.md` 。

下载或制作一张封面图片命名为 `cover.jpg` 与书籍的源文件放在同一个目录。

### 根据需要修改模板文件

本文附件模板中的 epub.css 文件是控制生成的EPUB和MOBI文件排版格式的，如果有需要，请根据需要进行修改，比如正文字体、引用段落字体、各级标题字体字号等。需要注意的是MOBI并不能支持完整的CSS规范，详情请参阅[参考资料 Amazon Kindle Publishing Guidelines](#foot-reference)。

附件模板中的 default.epub 文件是Pandoc生成EPUB时使用的HTML模板，需要放在用户数据目录下的 `templates` 文件夹中，详细见[参考资料 Pandoc User's Guide](#foot-reference) 中的 `--data-dir` 部分。如有需要，也可以进行修改。

附件模板中的 kindle.latex (6 inch) 和 zhtw.latex (A4) 文件是控制生成的PDF文件排版格式的，如果有需要，请根据需要进行修改，页边距、字体、字号、段落间距、行间距等。

### 生成电子书

把源文件整理好后，只需要运行下面的命令就可以输出包含目录、支持导航、排版精美的电子书了。

使用Pandoc和KindleGen生成电子书的命令（模板文件 `_tmpl/build.bat`）：

<div><pre><code>:: A4 pdf
pandoc meta.md book.md --toc --template=zhtw --latex-engine=xelatex ^
	--no-tex-ligatures -V documentclass=scrartcl -o A4.pdf
:: 6 inch pdf
pandoc meta.md book.md --toc --template=kindle --latex-engine=xelatex ^
	--no-tex-ligatures -V documentclass=scrartcl -o output.pdf
:: epub
pandoc meta.md book.md -o output.epub
:: mobi
kindelgen output.epub
</code></pre></div>

通过上面这几条命令，已经生成好了各种格式和尺寸的电子书，是不是很简便？有没有很过瘾的感觉？

顺带一提，本文及本网站也都是用Pandoc生成的 ~ ~

最后，忠心的祝愿网络上能够有越来越多的高质量电子书供我们这些买不起纸质书的穷屌丝们阅读。

----

## 模板及样书下载

前文中提到的文件模板，以及南怀瑾大师著述的《南怀瑾选集·第十卷·原本大学微言》源文件和生成的电子书（包括EPUB、MOBI、6寸和A4尺寸的PDF）作为示例样书，可以从我的百度网盘下载：

<small style="color: red; font-style:italic">（2016/4/2更新：链接已失效，暂时没有时间更新）</small>

* 模板：<s>http://pan.baidu.com/s/1o6rvZAU</s>
* 源文件：<s>http://pan.baidu.com/s/1iWWdo</s>
* 电子书：<s>http://pan.baidu.com/s/1nt6Xcud</s>

<span id="foot-reference"></span>
## 参考资料

1. [Pandoc User's Guide](http://johnmacfarlane.net/pandoc/README.html)：Pandoc用法，以YAML格式书写 epub metadata
2. [Amazon Kindle Publishing Guidelines](http://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf)：Amazon Kindle MOBI 格式参考
3. [How We Automated Our Ebook Builds With Pandoc and KindleGen](http://puppetlabs.com/blog/automated-ebook-generation-convert-markdown-epub-mobi-pandoc-kindlegen)：从epub文件自动生成mobi文件
4. [Pandoc latex 模板参考](https://github.com/tzengyuxio/pages/tree/gh-pages/pandoc)：Pandoc 中文 PDF 模板
5. [xelatex在文档处理中的使用](http://www.bibodeng.com/tools/140.html)：Pandoc latex 中文字体处理
6. [LaTeX quote 重定义](hi.baidu.com/asnahu/item/59ce80a9ce7e9a15a8cfb707)：Pandoc latex 模板定制

