+++
Categories = ["Programming", "Python"]
Description = "Django admin customization ticks."
Tags = ["programming", "python", "django", "ticks"]
date = "2017-06-13T23:00:00+08:00"
menu = "main"
title = "Django Admin 定制开发技巧"

+++

## 过滤器（Filters）

### 下拉列表式过滤器

模版文件：

```html
{% load i18n %}
<script type="text/javascript">var go_from_select = function(opt) { window.location = window.location.pathname + opt };</script>
<h3>{% blocktrans with filter_title=title %} By {{ filter_title }} {% endblocktrans %}</h3>
<ul class="admin-filter-{{ title|cut:' ' }}">
{% if choices|slice:"4:" %}
    <li>
    <select style="width: 95%;"
        onchange="go_from_select(this.options[this.selectedIndex].value)">
    {% for choice in choices %}
        <option{% if choice.selected %} selected="selected"{% endif %}
         value="{{ choice.query_string|iriencode }}">{{ choice.display }}</option>
    {% endfor %}
    </select>
    </li>
{% else %}
    {% for choice in choices %}
        <li{% if choice.selected %} class="selected"{% endif %}>
        <a href="{{ choice.query_string|iriencode }}">{{ choice.display }}</a></li>
    {% endfor %}
{% endif %}
</ul>
```

Admin代码：

```python
from django.contrib.admin.filters import (
    AllValuesFieldListFilter, RelatedFieldListFilter, ChoicesFieldListFilter)


class DropdownFilter(AllValuesFieldListFilter):
    template = 'app/admin/dropdown_filter.html'
    

class RelatedDropdownFilter(RelatedFieldListFilter):
    template = 'app/admin/dropdown_filter.html'


class ChoicesDropdownFilter(ChoicesFieldListFilter):
    template = 'app/admin/dropdown_filter.html'
```


### 三级分类级联过滤器

```python
from django.db import models
from django.contrib import admin


class Category(models.Model):
    code = models.CharField(verbose_name='分类代码', max_length=6)
    name = models.CharField(verbose_name='分类名', max_length=255)
    level = models.SmallIntegerField(verbose_name='级别')
    lv1_code = models.CharField(verbose_name='一级代码', max_length=2, default='', blank=True)
    lv1_name = models.CharField(verbose_name='一级分类', max_length=255, default='', blank=True)
    lv2_code = models.CharField(verbose_name='二级代码', max_length=4, default='', blank=True)
    lv2_name = models.CharField(verbose_name='二级分类', max_length=255, default='', blank=True)


class Item(models.Model):
    name = models.CharField(verbose_name='商品名', max_length=255)
    category = models.ForeignKey(Category, verbose_name='商品分类', null=True, blank=True)
    cover_img = models.CharField(verbose_name='封面图片', max_length=255, null=True, blank=True)


class CategoryLv1Filter(admin.SimpleListFilter):
    title = '一级分类'
    parameter_name = 'cat_lv1_code__exact'
    template = 'app/admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        cat_lv1 = Category.objects.filter(level=1)
        return [
            (cat.code, cat.name)
            for cat in cat_lv1
        ]

    def queryset(self, request, queryset):
        cat_lv1 = self.value()
        if cat_lv1:
            queryset = queryset.filter(category__lv1_code=cat_lv1)
        return queryset


class CategoryLv2Filter(admin.SimpleListFilter):
    title = '二级分类'
    parameter_name = 'cat_lv2_code__exact'
    template = 'app/admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        cat_lv1 = request.GET.get('cat_lv1_code__exact')
        if cat_lv1:
            cat_lv2 = Category.objects.filter(level=2, lv1_code=cat_lv1)
        else:
            cat_lv2 = []
        return [
            (cat.code, cat.name)
            for cat in cat_lv2
        ]

    def queryset(self, request, queryset):
        cat_lv2 = self.value()
        if cat_lv2:
            queryset = queryset.filter(category__lv2_code=cat_lv2)
        return queryset


class CategoryLv3Filter(admin.SimpleListFilter):
    title = '三级分类'
    parameter_name = 'cat_lv3_code__exact'
    template = 'app/admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        cat_lv1 = request.GET.get('cat_lv1_code__exact')
        cat_lv2 = request.GET.get('cat_lv2_code__exact')
        if cat_lv1 and cat_lv2:
            cat_lv3 = Category.objects.filter(level=3, lv2_code=cat_lv2)
        else:
            cat_lv3 = []
        return [
            (cat.code, cat.name)
            for cat in cat_lv3
        ]

    def queryset(self, request, queryset):
        cat_lv3 = self.value()
        if cat_lv3:
            queryset = queryset.filter(category__code=cat_lv3)
        return queryset


class ItemAdmin(admin.ModelAdmin):
    # ...
    list_filter = [CategoryLv1Filter, CategoryLv2Filter, CategoryLv3Filter]
```


## 对象表单（ChangeList）

### 列表中显示图片、链接

```python
from django.contrib import admin

_default_image = '/static/images/common/Bmr_160.png'


# define as a standalone function
def cover_img_html(obj):
    img_url = obj.cover_img or _default_image
    return '<img src="{}" style="width:100px;height:100px;" />'.format(img_url)
cover_img_html.allow_tags = True
cover_img_html.short_description = '封面图片'


class ItemAdmin(admin.ModelAdmin):
    list_display = [cover_img_html, 'category_link']

    # define as a method
    def category_link(self, obj):
        if not obj.category:
            return '--'
        return ('<a href="/admin/app/category/{}" target="_blank">{}</a>'
                .format(obj.category.id, obj.category.name))
    category_link.allow_tags = True
    category_link.short_description = '商品分类'
    category_link.admin_order_field = 'category_id'
```


### 减小外键关联下拉列表选项数量

```python
from django.db import models
from django.forms import ModelForm
from django.contrib import admin


class Category(models.Model):
    code = models.CharField(verbose_name='分类代码', max_length=6)
    name = models.CharField(verbose_name='分类名', max_length=255)
    level = models.SmallIntegerField(verbose_name='级别')
    lv1_code = models.CharField(verbose_name='一级代码', max_length=2, default='', blank=True)
    lv1_name = models.CharField(verbose_name='一级分类', max_length=255, default='', blank=True)
    lv2_code = models.CharField(verbose_name='二级代码', max_length=4, default='', blank=True)
    lv2_name = models.CharField(verbose_name='二级分类', max_length=255, default='', blank=True)
    
    
class Vendor(models.Model):
    brand = models.CharField(verbose_name='品牌', max_length=255)
    city = models.CharField(verbose_name='城市', max_length=255)
    address = models.CharField(verbose_name='地址', max_length=255)


class Item(models.Model):
    name = models.CharField(verbose_name='商品名', max_length=255)
    brand = models.CharField(verbose_name='品牌', max_length=255)
    vendor = models.ForeignKey(Vendor, verbose_name='生产厂家', null=True, blank=True)
    category = models.ForeignKey(Category, verbose_name='商品分类', null=True, blank=True)
    cover_img = models.CharField(verbose_name='封面图片', max_length=255, null=True, blank=True)


class ItemModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ItemModelForm, self).__init__(*args, **kwargs)
        if self.instance:
            inst_brand = self.instance.brand
            self.fields['vendor'].queryset = Vendor.objects.filter(brand=inst_brand)


class ItemAdmin(admin.ModelAdmin):
    # ...
    form = ItemModelForm
```


## 批量操作（Actions）

### 禁用批量删除动作

```python
from django.contrib import admin


class ItemAdmin(admin.ModelAdmin):
    # ...

    def get_actions(self, request):
        actions = super(ItemAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
```


### 批量执行动作

```python
from django.contrib import messages, admin


def batch_remove_category(model_admin, request, queryset):
    # batch at database level
    queryset.update(category_id=None)

    # # or one by one at orm level
    # for obj in queryset:
    #     obj.category = None
    #     obj.save()

    # messages can be send to the admin page
    messages.success(request, '操作成功！')
batch_remove_category.short_description = '批量删除分类'

    
class ItemAdmin(admin.ModelAdmin):
    # ...
    actions = [batch_remove_category, ]
```


### 需要参数的批量执行动作

```python
from django.forms import CharField
from django.contrib import admin, messages
from django.contrib.admin import helpers, actions


class ChangeBrandActionForm(helpers.ActionForm):
    brand = CharField(max_length=255, required=False)


def batch_change_brand(model_admin, request, queryset):
    brand = request.POST.get('brand')
    if not brand:
        messages.error(request, '请填写非空的品牌名称！')
        return
    queryset.update(brand=brand)
    messages.success(request, '修改成功！')
batch_change_brand.short_description = '批量修改品牌'


class ItemAdmin(admin.ModelAdmin):
    # ...
    actions = [batch_change_brand, ]
    action_form = ChangeBrandActionForm
```


### 动态创建批量动作

```python
from django.db import models
from django.contrib import admin, messages


class ItemABCType(object):
    A = 'A'
    B = 'B'
    C = 'C'
    CHOICES = [
        (A, 'A类商品'),
        (B, 'B类商品'),
        (C, 'C类商品')
    ]


class Item(models.Model):
    abc_type = models.CharField(
        verbose_name='商品评级', max_length=1,
        choices=ItemABCType.CHOICES, null=True, blank=True)


def _make_mark_action(typ, name):
    def mark_action_func(model_admin, request, queryset):
        queryset.update(type=typ)
        messages.success(request, '操作成功！')

    action_name = 'mark_action_func_{}'.format(typ)
    mark_action_func.func_name = action_name
    mark_action_func.short_description = '商品评级：{}'.format(name)
    return mark_action_func


class ItemAdmin(admin.ModelAdmin):
    # ...
    actions = [_make_mark_action(typ, name) for typ, name in ItemABCType.CHOICES]
```


### 对所有行执行指定操作

其他适用场景：批量／全量下载文件，跨库同步。

```python
from django.db import models
from django.contrib import admin, messages


class Category(models.Model):
    pinyin = models.TextField(verbose_name='拼音', default='', blank=True)

    def update_pinyin(self):
        pinyin = ''
        self.pinyin = pinyin
        self.save()


def batch_update_pinyin(model_admin, request, queryset):
    count = queryset.count()
    for cat in queryset:
        cat.update_pinyin()
    messages.success(request, '成功更新%d条拼音！' % count)
batch_update_pinyin.short_description = '批量更新分类拼音'


class CategoryAdmin(admin.ModelAdmin):
    # ...
    actions = [batch_update_pinyin, ]
    
    def changelist_view(self, request, extra_context=None):
        """
        Override to allow action on all records without selection.
        """
        if (request.POST.get('action') == 'batch_update_pinyin' and
                not request.POST.getlist(admin.ACTION_CHECKBOX_NAME)):
            post = request.POST.copy()
            for cat in Category.objects.all():
                post.update({admin.ACTION_CHECKBOX_NAME: str(cat.id)})
            request._set_post(post)
        return super(CategoryAdmin, self).changelist_view(request, extra_context)
```


## 页面交互

### 对象编辑页面添加特殊字段

```python
from django.forms import ModelForm, CharField
from django.contrib import admin


class ItemAdminForm(ModelForm):

    upload_img_url = CharField(max_length=255, required=False)

    def save(self, commit=True):
        upload_img_url = self.cleaned_data.get('upload_img_url')
        if upload_img_url:
            self.upload_image(upload_img_url)
        return super(ItemAdminForm, self).save(commit)

    def upload_image(self, image_url):
        pass


class ItemAdmin(admin.ModelAdmin):
    # ...
    form = ItemAdminForm
```


### 用JS定制复杂交互功能

模版文件：

```html
{% extends "admin/change_list.html" %}

{% block extrahead %}
{{ block.super }}
<link href="//cdn.bootcss.com/semantic-ui/2.2.10/semantic.min.css" rel="stylesheet">
<script src="//cdn.bootcss.com/jquery/3.1.0/jquery.min.js"></script>
<script src="//cdn.bootcss.com/semantic-ui/2.2.10/semantic.min.js"></script>
<script src="//cdn.bootcss.com/lodash.js/4.17.4/lodash.min.js"></script>
<script>
$(function () {
  var extraStyles = ' \
        <style type="text/css"> \
        /* .actions {position: fixed;} */ \
        .field-name input {width: 10em;} \
        .field-brand input, .field-spec input, .field-price input {width: 4em;} \
        input[type=checkbox] {transform: scale(1.4);} \
        .hover-image { \
            display: none; padding: 30px; \
            position: fixed; top: 50%; left: 50%; \
            transform: translate(-50%, -50%); z-index: 1; \
            width: 400px; height: 400px; \
            border: 1px solid #cecece; background: #fff; \
        } \
        </style>'
  $(extraStyles).appendTo($('head'))
})

window.onload = function () {
  var categoryHTML = ' \
        <div class="wrap"> \
        <input name="action_category" type="text" class="search"> \
        <div class="menu"></div> \
        </div>'
  $('.actions input[name="action_category"]'.replaceWith(categoryHTML))

  var hoverImageHTML = '<img src="" class="hover-image"/>'
  $(hoverImageHTML).appendTo($('body'))

  // show image when mouse move over image links
  $('tbody').on({
    mouseenter: function () {
      var href = $(this).attr('href')
      $('.hover-image').attr('src', href).show()
      return false
    },
    mouseleave: function () {
      $('.hover-image').hide()
      return false
    }
  }, 'a.images')

  // disable editing when item has already been verified
  $('.link-actions.reset').each(function () {
    var parent = $(this).parent().parent()
    parent.find('input, select').attr('disabled', 'disabled').css('background', '#efeeee')
    parent.find('a.change-related, a.add-related').hide()
  })

  // the disabled lines should be enabled before saving request
  // to avoid form validation errors
  $('input[type=submit][value=Save]').on('click', function () {
    $('tr input:not([type="checkbox"]):disabled').removeAttr('disabled')
  })

  // ajax request for removing barcode/tmall_id/jd_id/yhd_id
  $('td').on('click', '.ui.mini.button.inline', function () {
    var that = $(this)
    // get desired parameters

    $.ajax({
      url: '/api/path/to/remove/relation',
      type: 'POST',
      data: {
        // parameters
      },
      success: function (status) {
        console.log(status)
      },
      error: function (XMLHttpRequest, textStatus, errorThrown) {
        console.log(XMLHttpRequest.responseText)
      }
    })
  })

  // ajax requests for item operation actions
  $('.link-actions').click(function () {
    var that = $(this)
    // get desired parameters

    $.ajax({
      // pass
    })
  })

  // searching for categories using ajax requests
  $('input.search[name="action_category"]').on('input', _.debounce(function () {
    var keyword = $(this).val();
    var regular = /^[0-9A-Za-z\u4e00-\u9fa5]{3,}$/
    if (keyword === String(keyword.match(regular))) {
      $.ajax({
        url: '/api/path/to/category/search?keyword=' + keyword,
        type: 'GET',
        success: function (data) {
          if (data.code === 0) {
            $('.menu').children().remove()
            for (var i = 0; i < data.results.length; i++) {
              var item = '<div class="item" data-value=' + data.results[i].code + '>'
                + data.results[i].name + '</div>'
              $('.menu').append(item)
            }
            $('.menu').show()
          } else {
            alert(data)
          }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
          alert(XMLHttpRequest.responseText)
        }
      })
    }
  }, 800))

  // category selection items click events
  $('.menu').on('click', '.item', function (e) {
    e.stopPropagation()
    $('input.search').val($(this).data('value'))
    $('.menu').hide()
  })
}
</script>
{% endblock %}

<!-- show pagination on both top and bottom -->
{% block result_list %}
    {% block pagination %} {{ block.super }} {% endblock %}
    {{ block.super }}
{% endblock %}
```

Admin代码：

```python
from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField


class StdItemStatus(object):
    NEW = 'new'
    PENDING_REVIEW = 'pending_review'
    HALF_REVIEW = 'half_review'
    HUMAN_VERIFIED = 'human_verified'
    AUTO_VERIFIED = 'auto_verified'
    DELETED = 'deleted'
    NA = 'na'

    CHOICES = [
        (NEW, '新增标品'),
        (PENDING_REVIEW, '待审核'),
        (HALF_REVIEW, '半审核'),
        (HUMAN_VERIFIED, '已通过人工审核'),
        (AUTO_VERIFIED, '已通过自动审核'),
        (DELETED, '已删除'),
        (NA, '不处理'),
    ]
    


class Item(models.Model):
    # ...
    barcodes = ArrayField(
    models.TextField(), verbose_name='商品条码', null=True, blank=True)
    status = models.CharField(
        verbose_name='状态', max_length=20,
        default=StdItemStatus.NEW, choices=StdItemStatus.CHOICES)

    @property
    def is_verified(self):
        return self.status in (
            StdItemStatus.HUMAN_VERIFIED, StdItemStatus.AUTO_VERIFIED,
            StdItemStatus.DELETED, StdItemStatus.NA,
        )


def images_html(item_obj):
    from os.path import basename
    images = item_obj.images or []
    html = '<br>'.join(map(
        lambda url:
            '<a class="images" href="{url}" target="_blank">{name}</a>'
            .format(url=url, name=basename(url)[:8]),
        images
    ))
    return html or '--'


def barcodes_html(item_obj):
    barcodes = item_obj.barcodes or []
    if item_obj.is_verified:
        html = '<br>'.join(map(
            lambda bc: '<span>{}</span>'.format(bc),
            barcodes
        ))
    else:
        html = '<br>'.join(map(
            lambda bc: '<span>{}</span><span class="mini ui button inline">X</span>',
            barcodes
        ))
        html += '<br><span class="tiny ui button">添加</span>'
    return html or '--'
barcodes_html.allow_tags = True
barcodes_html.short_description = '商品条码'


def operation_links(item_obj):
    if not item_obj.is_verified:
        edit = '<a href="/admin/app/item/{id}" target="_blank">修改</a>'.format(id=item_obj.id)
        verify = '<a class="link-actions verify" data-action="verify" href="javascript:">通过</a>'
        remove = '<a class="link-actions remove" data-action="delete" href="javascript:">删除</a>'
        return '<br>'.join([edit, verify, remove])
    else:
        reset = '<a class="link-actions reset" data-action="reset" href="javascript:">重置状态</a>'
        return reset
operation_links.allow_tags = True
operation_links.short_description = '审核操作'


class ItemAdmin(admin.ModelAdmin):
    # ...
    list_display = [images_html, barcodes_html, operation_links, ]
    list_display_links = None
    list_per_page = 5

    change_list_template = 'app/admin/item_change_list.html'
```


## 其他技巧

### 事务控制

其他适用场景：订单相关操作，运营操作日志。

```python
from django.db import models, transaction
from django.contrib.postgres.fields import ArrayField


class Item(models.Model):
    barcodes = ArrayField(
        models.TextField(), verbose_name='国际条码', null=True, blank=True)
    tmall_ids = ArrayField(
        models.TextField(), verbose_name='天猫IDs', null=True, blank=True)
    jd_ids = ArrayField(
        models.TextField(), verbose_name='京东IDs', null=True, blank=True)
    yhd_ids = ArrayField(
        models.TextField(), verbose_name='一号店IDs', null=True, blank=True)

    def fix_m2m_conflict(self, conflict_fields):
        # fix conflicts between different items
        # in case of un-fixable errors, raise exceptions
        pass

    def save_relations(self, related_fields):
        # the related barcode, tmall/jd/yhd items should be saved
        # together with the item
        pass

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # ...
        conflict_fields = []
        related_fields = []

        try:
            # all success or all fail
            with transaction.atomic():
                self.fix_m2m_conflict(conflict_fields)
                self.save_relations(related_fields)
                super(Item, self).save(force_insert, force_update, using, update_fields)
        except Exception as err:
            # NOTE: exceptions should be handled outside the transaction context
            pass
```


### 自动注册Admin类

```python
from django.contrib import admin

from .models import *

# ModelAdmin classes definitions

# register all admin models which end with "Admin"
_locals = locals()
_obj_name = _obj = _m = None
for _obj_name, _obj in _locals.items():
    if (_obj_name.endswith('Admin') and
            issubclass(_obj, admin.ModelAdmin) and
            _obj is not admin.ModelAdmin):
        _m = _locals[_obj_name.replace('Admin', '')]
        admin.site.register(_m, _obj)
del _locals, _obj_name, _obj, _m
```


### 在后台界面查看操作日志

```python
from django.contrib import admin
from django.contrib.admin.models import LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    """
    Admin of the history/log table for view only purpose.
    """
    list_display = [
        'action_time', 'user', 'content_type', 'object_id', 'object_repr',
        'action_flag', 'change_message']
    readonly_fields = [
        'user', 'content_type', 'object_id', 'object_repr', 'action_flag',
        'change_message']
    list_filter = ['action_time', 'user', 'content_type']
    ordering = ['-action_time']
    list_display_links = None
    actions = None

    # We don't want people changing this historical record

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        from django.core.exceptions import SuspiciousOperation
        raise SuspiciousOperation('log entry should not be changed')


admin.site.register(LogEntry, LogEntryAdmin)
```
