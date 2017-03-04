+++
Categories = ["Software", "MacOSX"]
Description = "Use ikbc c87 keyboard on macbook pro."
Tags = ["macosx", "software", "ikbc", "alfred", "karabiner"]
date = "2017-03-04T14:50:00+08:00"
menu = "main"
title = "MacBook Pro上完美使用IKBC C87机械键盘"

+++

最近也用上了MacBook Pro，除了吐槽一下这个Multi Touch Bar键盘敲起来没有一点手感，还有数字"1"左边那个丧心病狂的的"Section（§）"之外，其他方面用起来真心舒服。

适应了几天Mac的键位后，琢磨着把自己的IKBC C87机械键盘接上来用，主要参考了下面的文章：

- [让机械键盘完美适配你的Mac！](http://plus.zealer.com/post/56805.html)
- [Make Home & End keys behave like Windows on Mac OS X](https://damieng.com/blog/2015/04/24/make-home-end-keys-behave-like-windows-on-mac-os-x)
- [DefaultKeyBinding.dict](http://osxnotes.net/keybindings.html)

作为一枚死宅的程序猿，我的需求很简单：

1. 把数字"1"左边的Section键换回反引号键"`~"，把半残的左边Shift键右边的反引号键还原成Shift；
2. 把IKBC C87上的Control、Win、Alt键映射成Mac的Control、Option、Command键位顺序；
3. 把IKBC C87上的Home、End、PageUp、PageDown键功能都可以正常跳转

嗯，就这样，通过一番研（sou）究（suo）之后，发现可以通过如下组合实现上面的功能：

Karabiner Elements修改建伟映射、DefaultKeyBinding.dict修改组合键功能、Alfred控制快速切换Karabiner Elements的Profile。

具体过程略过，简要记录一下主要配置。

Karabiner Elements建立三个Profiles：

1. "none"：原始键盘，不映射任何键位，这个主要是用作偶尔别人使用电脑不习惯改键或键位修改出现问题时，可以快速恢复；
2. "internal"：这个用于映射内置键盘的"§±"和"`~"键；
3. "ikbc": 用于映射机械键盘上的Control、Win、Alt键的顺序；

这三个映射使用[Karabiner Elements Profile Switcher](http://www.packal.org/workflow/karabiner-elements-profile-switcher)这个Workflow可以快速切换。因为Karabiner Elements现在还不可以根据键盘关联自动调用对应的Profile。

我给每个Profile都制定了一个快捷键（Alfred Trigger Hotkey）：

- Ctrl + Option + Command + K：切换到 "none" Profile；
- 在内置键盘上使用 F12 切换到 "internal" Profile；
- 机械键盘上的 PrtSrc 键被 Karabiner Elements 识别出来是F13，所以就用了这个 "F13" 切换到 "ikbc" Profile。

我的编码习惯经常会用到Home、End、PageUp、PageDown这几个键进行快速跳转，接上机械键盘自然能把这些键配置起来是最好了。好在实现这些功能键不需要KE和Alfred的功能，直接使用系统配置就可以完成。

把要绑定的键的配置写入到文件"~/Library/KeyBindings/DefaultKeyBinding.dict"就可以了。更多绑定和功能列表请参照资料自行配置。

```
➜  ~ cat ~/Library/KeyBindings/DefaultKeyBinding.dict
{
    "\UF729"  = moveToBeginningOfParagraph:;  // home
    "\UF72B"  = moveToEndOfParagraph:;  // end
    "$\UF729" = moveToBeginningOfParagraphAndModifySelection:;  // shift-home
    "$\UF72B" = moveToEndOfParagraphAndModifySelection:;  // shift-end
    "^\UF729" = moveToBeginningOfDocument:;  // ctrl-home
    "^\UF72B" = moveToEndOfDocument:;  // ctrl-end
    "^$\UF729" = moveToBeginningOfDocumentAndModifySelection:;  // ctrl-shift-home
    "^$\UF72B" = moveToEndOfDocumentAndModifySelection:;  // ctrl-shift-end
}
```

如此，又可以用我的键盘愉快的啪啪啪了，貌似我敲键盘的声音会比较大一些，对我就是故意的😄😄😄😄😄
