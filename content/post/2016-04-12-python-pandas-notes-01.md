+++
Categories = ["Pandas", "Python"]
Description = ""
Tags = ["pandas", "python"]
date = "2016-04-12T18:52:25+08:00"
menu = "main"
title = "Pandas学习笔记（一）：CSV数据加载保存"

+++


## 加载CSV数据

很多数据都存储在CSV文件中，Pandas 为读取提供了一个强大的 `read_csv` 函数，这个函数接受很多可选参数，通过参数控制数据加载的方式，以及一些基本的清理工作。

```python
pd.read_csv(filepath_or_buffer, sep=',', delimiter=None, header='infer', names=None,
    index_col=None, usecols=None, squeeze=False, prefix=None, mangle_dupe_cols=True,
    dtype=None, engine=None, converters=None, true_values=None, false_values=None,
    skipinitialspace=False, skiprows=None, skipfooter=None, nrows=None, na_values=None,
    keep_default_na=True, na_filter=True, verbose=False, skip_blank_lines=True,
    parse_dates=False, infer_datetime_format=False, keep_date_col=False,
    date_parser=None, dayfirst=False, iterator=False, chunksize=None, compression='infer',
    thousands=None, decimal='.', lineterminator=None, quotechar='"', quoting=0,
    escapechar=None, comment=None, encoding=None, dialect=None, tupleize_cols=False,
    error_bad_lines=True, warn_bad_lines=True, skip_footer=0, doublequote=True,
    delim_whitespace=False, as_recarray=False, compact_ints=False, use_unsigned=False,
    low_memory=True, buffer_lines=None, memory_map=False, float_precision=None)

Returns
    result : DataFrame or TextParser
```

很多参数都是非常有用的，简要记录一下（详细文档请参考 `help(pd.read_csv)` 及官方文档）：

1. `filepath_or_buffer`：参数名字本身反映了功能
    * 这里可以接受一个文件名，或者一个URL，
    * 也可以接受一个打开的文件句柄，
    * 或者其他任何提供了`read`方法的对象，
    * 举个栗子：某个URL输出CSV，但是需要验证密码，那么就没法让 `read_csv` 直接读取URL，但是可以使用 `urlopen` 发送附带了验证信息的Request，并把返回的 Response 对象传给 `read_csv` 函数，进而通过 Response 对象的 `read` 方法加载数据；
2. `sep` 和 `delimiter`：这两个参数是一个意思，`delimiter`是`sep`的别名；如果指定为 `\t`（制表符）的话，就可以实现 `read_table` 的默认功能；支持使用正则表达式来匹配某些不标准的CSV文件；
3. `header` 和 `names`：配合使用指定加载后的列名；
4. `parse_dates`：boolean or list of ints or names or list of lists or dict, default False. 这个参数指定对CSV文件中日期序列的处理方式：
    * 默认为False，原样加载，不解析日期时间，
    * 可以为True，尝试解析日期索引，
    * 可以为数字或 `names` 的列表，解析指定的列为时间序列，
    * 可以为以列表为元素的列表，解析每个子列表中的字段组合为时间序列，
    * 可以为值为列表的字典，解析每个列表中的字段组合为时间序列，并命名为字典中对应的键值；
5. `date_parser`：可以指定一个自定义函数解析日期；
6. `keep_date_col`：解析出日期序列后，是否保留原来的列；
7. `dayfirst`：boolean, default False, DD/MM format dates, international and European format；
8. `iterator`：boolean, default False，Return TextFileReader object for iteration or getting chunks with `get_chunk()`；
9. `encoding`：指定读取或写入CSV文件时使用的字符集，支持 [codecs 包中的标准字符集](https://docs.python.org/3/library/codecs.html#standard-encodings)；
10. `index_col`：数字、列名或列表，数字或列名指定某一列作为索引，列表制定某几列作为 DataFrame 的层次索引；
11. 可以使用`skip_initialspace`, `skiprows`, `skipfooter`, `comment`, `float_precision`等参数做一些基本的清理动作。

下面举个例子来简单演示一下 `parse_dates` 和 `data_parser` 的使用：


```python
import pandas as pd
from tempfile import TemporaryFile

mycsv = ["date,hour,A1,A2,A3,A4,A5,A6,date2,hour2",
    "20150102,1,117,85,109,132,166,113,20160102,2",
    "20150102,2,88,34,82,100,126,85,20160102,3",
    "20150102,3,48,54,38,50,55,46,20160102,4",
    "20150102,4,141,120,154,148,175,114,20160102,5",
    "20150102,5,91,64,74,71,84,70,20160102,6",
    "20150102,6,45,10,46,20,68,44,20160102,7"]

tmp_csv_file = TemporaryFile()
tmp_csv_file.write('\n'.join(mycsv))
tmp_csv_file.flush()
```


```python
tmp_csv_file.seek(0)
df = pd.read_csv(tmp_csv_file)
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>hour</th>
      <th>A1</th>
      <th>A2</th>
      <th>A3</th>
      <th>A4</th>
      <th>A5</th>
      <th>A6</th>
      <th>date2</th>
      <th>hour2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20150102</td>
      <td>1</td>
      <td>117</td>
      <td>85</td>
      <td>109</td>
      <td>132</td>
      <td>166</td>
      <td>113</td>
      <td>20160102</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>20150102</td>
      <td>2</td>
      <td>88</td>
      <td>34</td>
      <td>82</td>
      <td>100</td>
      <td>126</td>
      <td>85</td>
      <td>20160102</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>20150102</td>
      <td>3</td>
      <td>48</td>
      <td>54</td>
      <td>38</td>
      <td>50</td>
      <td>55</td>
      <td>46</td>
      <td>20160102</td>
      <td>4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>20150102</td>
      <td>4</td>
      <td>141</td>
      <td>120</td>
      <td>154</td>
      <td>148</td>
      <td>175</td>
      <td>114</td>
      <td>20160102</td>
      <td>5</td>
    </tr>
    <tr>
      <th>4</th>
      <td>20150102</td>
      <td>5</td>
      <td>91</td>
      <td>64</td>
      <td>74</td>
      <td>71</td>
      <td>84</td>
      <td>70</td>
      <td>20160102</td>
      <td>6</td>
    </tr>
    <tr>
      <th>5</th>
      <td>20150102</td>
      <td>6</td>
      <td>45</td>
      <td>10</td>
      <td>46</td>
      <td>20</td>
      <td>68</td>
      <td>44</td>
      <td>20160102</td>
      <td>7</td>
    </tr>
  </tbody>
</table>
</div>



从上面的示例中，可以看到使用默认参数时，`read_csv` 函数不会尝试解析日期，这样可以提高文件的加载速度。

但是第一列日期和第二列小时构成了我们需要的时间戳，加载了CSV后我们需要进行处理，那能不能在加载CSV的时候就直接解析出来呢？我们可以试一试 `parse_dates` 参数，把第一列和第二列的索引组成一个列表传给 `parse_dates` 参数：


```python
tmp_csv_file.seek(0)
df = pd.read_csv(tmp_csv_file, parse_dates=[0, 1])
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>hour</th>
      <th>A1</th>
      <th>A2</th>
      <th>A3</th>
      <th>A4</th>
      <th>A5</th>
      <th>A6</th>
      <th>date2</th>
      <th>hour2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2015-01-02</td>
      <td>1</td>
      <td>117</td>
      <td>85</td>
      <td>109</td>
      <td>132</td>
      <td>166</td>
      <td>113</td>
      <td>20160102</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2015-01-02</td>
      <td>2</td>
      <td>88</td>
      <td>34</td>
      <td>82</td>
      <td>100</td>
      <td>126</td>
      <td>85</td>
      <td>20160102</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2015-01-02</td>
      <td>3</td>
      <td>48</td>
      <td>54</td>
      <td>38</td>
      <td>50</td>
      <td>55</td>
      <td>46</td>
      <td>20160102</td>
      <td>4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2015-01-02</td>
      <td>4</td>
      <td>141</td>
      <td>120</td>
      <td>154</td>
      <td>148</td>
      <td>175</td>
      <td>114</td>
      <td>20160102</td>
      <td>5</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2015-01-02</td>
      <td>5</td>
      <td>91</td>
      <td>64</td>
      <td>74</td>
      <td>71</td>
      <td>84</td>
      <td>70</td>
      <td>20160102</td>
      <td>6</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2015-01-02</td>
      <td>6</td>
      <td>45</td>
      <td>10</td>
      <td>46</td>
      <td>20</td>
      <td>68</td>
      <td>44</td>
      <td>20160102</td>
      <td>7</td>
    </tr>
  </tbody>
</table>
</div>



我们看到第一列被成功的解析成了日期数据，但是并没有按照我们想象的那样把第一列和第二列一起解析成一个日期时间对象。

这是因为我们**传递参数的姿势不对**，正确的应该是这样：`parse_dates=[[0, 1]]`，再试一下：


```python
tmp_csv_file.seek(0)
df = pd.read_csv(tmp_csv_file, parse_dates=[[0, 1]])
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date_hour</th>
      <th>A1</th>
      <th>A2</th>
      <th>A3</th>
      <th>A4</th>
      <th>A5</th>
      <th>A6</th>
      <th>date2</th>
      <th>hour2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20150102 1</td>
      <td>117</td>
      <td>85</td>
      <td>109</td>
      <td>132</td>
      <td>166</td>
      <td>113</td>
      <td>20160102</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>20150102 2</td>
      <td>88</td>
      <td>34</td>
      <td>82</td>
      <td>100</td>
      <td>126</td>
      <td>85</td>
      <td>20160102</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>20150102 3</td>
      <td>48</td>
      <td>54</td>
      <td>38</td>
      <td>50</td>
      <td>55</td>
      <td>46</td>
      <td>20160102</td>
      <td>4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>20150102 4</td>
      <td>141</td>
      <td>120</td>
      <td>154</td>
      <td>148</td>
      <td>175</td>
      <td>114</td>
      <td>20160102</td>
      <td>5</td>
    </tr>
    <tr>
      <th>4</th>
      <td>20150102 5</td>
      <td>91</td>
      <td>64</td>
      <td>74</td>
      <td>71</td>
      <td>84</td>
      <td>70</td>
      <td>20160102</td>
      <td>6</td>
    </tr>
    <tr>
      <th>5</th>
      <td>20150102 6</td>
      <td>45</td>
      <td>10</td>
      <td>46</td>
      <td>20</td>
      <td>68</td>
      <td>44</td>
      <td>20160102</td>
      <td>7</td>
    </tr>
  </tbody>
</table>
</div>



Opps！虽然第一列和第二列合并到一起了，但是并没有成功的解析成日期时间对象。因为这个格式真的没人看得懂是一个日期时间对象啊！！！

那就没有办法在加载CSV的时候就解析时间序列的方法了吗？

答案是有的。`read_csv` 还有一个参数：`date_parser`，我们可以自己写一个日期时间对象解析函数。


```python
from datetime import datetime

def my_date_parser(dt, hour):
    return datetime(int(dt[0:4]), int(dt[4:6]), int(dt[6:8]), int(hour))

tmp_csv_file.seek(0)
df = pd.read_csv(tmp_csv_file, date_parser=my_date_parser,
                 parse_dates={'time': [0, 1], 'time2': ['date2', 'hour2']}, index_col='time')
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time2</th>
      <th>A1</th>
      <th>A2</th>
      <th>A3</th>
      <th>A4</th>
      <th>A5</th>
      <th>A6</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2015-01-02 01:00:00</th>
      <td>2016-01-02 02:00:00</td>
      <td>117</td>
      <td>85</td>
      <td>109</td>
      <td>132</td>
      <td>166</td>
      <td>113</td>
    </tr>
    <tr>
      <th>2015-01-02 02:00:00</th>
      <td>2016-01-02 03:00:00</td>
      <td>88</td>
      <td>34</td>
      <td>82</td>
      <td>100</td>
      <td>126</td>
      <td>85</td>
    </tr>
    <tr>
      <th>2015-01-02 03:00:00</th>
      <td>2016-01-02 04:00:00</td>
      <td>48</td>
      <td>54</td>
      <td>38</td>
      <td>50</td>
      <td>55</td>
      <td>46</td>
    </tr>
    <tr>
      <th>2015-01-02 04:00:00</th>
      <td>2016-01-02 05:00:00</td>
      <td>141</td>
      <td>120</td>
      <td>154</td>
      <td>148</td>
      <td>175</td>
      <td>114</td>
    </tr>
    <tr>
      <th>2015-01-02 05:00:00</th>
      <td>2016-01-02 06:00:00</td>
      <td>91</td>
      <td>64</td>
      <td>74</td>
      <td>71</td>
      <td>84</td>
      <td>70</td>
    </tr>
    <tr>
      <th>2015-01-02 06:00:00</th>
      <td>2016-01-02 07:00:00</td>
      <td>45</td>
      <td>10</td>
      <td>46</td>
      <td>20</td>
      <td>68</td>
      <td>44</td>
    </tr>
  </tbody>
</table>
</div>



Bingo！是不是搞定了。这样加载并解析时间序列的效率也比加载后使用循环或列表解析处理的效率高的多了。

上面这段示例代码中，还演示了解析多列时间序列，可以按照列的索引指定要解析的列，也可以按照列名来制定要解析的列，另外，还演示了使用 `index_col` 参数指定 DataFrame 索引的用法。

## 保存CSV数据

除了加载CSV数据很方便之外，Pandas 的 DataFrame 类一个很方便的 `to_csv` 方法，可以把数据保存到CSV文件中。

```python
pd.DataFrame.to_csv(self, path_or_buf=None, sep=',', na_rep='', float_format=None,
    columns=None, header=True, index=True, index_label=None, mode='w',
    encoding=None, compression=None, quoting=None, quotechar='"', 
    line_terminator='\n', chunksize=None, tupleize_cols=False, date_format=None,
    doublequote=True, escapechar=None, decimal='.', **kwds)
    
unbound pandas.core.frame.DataFrame method:
    Write DataFrame to a comma-separated values (csv) file
```

嗯，默认输出就是标准的逗号分割的CSV文件，跟 `read_csv` 函数一样，这个函数同样有很多可选参数控制输出。

除了输出到CSV外，DataFrame 还有很多输出到其他格式的方法：


```python
[meth for meth in dir(pd.DataFrame) if meth.startswith('to_')]
```




    ['to_clipboard',
     'to_csv',
     'to_dense',
     'to_dict',
     'to_excel',
     'to_gbq',
     'to_hdf',
     'to_html',
     'to_json',
     'to_latex',
     'to_msgpack',
     'to_panel',
     'to_period',
     'to_pickle',
     'to_records',
     'to_sparse',
     'to_sql',
     'to_stata',
     'to_string',
     'to_timestamp',
     'to_wide',
     'to_xarray']



路漫漫其修远兮～～我将慢慢去求索～～

