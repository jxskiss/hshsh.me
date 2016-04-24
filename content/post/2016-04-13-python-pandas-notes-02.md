+++
Categories = ["Pandas", "Python"]
Description = ""
Tags = ["pandas", "python"]
date = "2016-04-13T18:02:04+08:00"
menu = "main"
title = "Pandas学习笔记（二）：基本数据结构"

+++

Pandas的开发者是：[Wes McKinney](http://wesmckinney.com)，这位大牛工作的时候没有顺手的工具，就决定自己顺手写一个出来。

Pandas具有但不限于一下特点：

1. 具备按轴自动或显式数据对齐功能的数据结构，这可以防止许多由于数据没有对齐以及来自不同数据源（索引方式不同）的数据而导致的常见错误；
2. 集成时间序列功能；
3. 既能处理时间序列数据也能处理非时间序列数据的数据结构；
4. 数学运算和约简（比如对某个轴求和）可以根据不同的元数据（轴编号）执行；
5. 可以灵活处理缺失数据；
6. 合并及其他出现在常见数据库（例如基于SQL的）中的关系型运算。

Pandas的导入约定：


```python
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
```

## Series

Series可以使用列表初始化，初始化时还可以指定索引名称。

Series可以被看成时一个定长的有序字典，因为它时索引值到数据值的一个映射，它可以用在许多原本需要字典参数的函数中。

如果数据被存放在一个Python字典中，也可以直接通过这个字典来创建Series。通过指定 `index` 可以只选择需要的对象，缺失值使用NaN自动填充。


```python
obj = Series([4, 7, -5, 3])
obj, obj.values, obj.index

obj = Series([4, 7, -5, 3], index=['d', 'b', 'a', 'c'])

obj[obj > 0]
obj * 2
np.exp(obj)

'b' in obj

sdata = {'Ohio': 35000, 'Texas': 71000, 'Oregon': 16000, 'Utah': 5000}
sdata = Series(sdata)
sdata
```




    Ohio      35000
    Oregon    16000
    Texas     71000
    Utah       5000
    dtype: int64




```python
states = ['California', 'Ohio', 'Oregon', 'Texas']
obj = Series(sdata, index=states)
obj
```




    California        NaN
    Ohio          35000.0
    Oregon        16000.0
    Texas         71000.0
    dtype: float64



对很多应用而言，Series最重要的一个功能是：在算数运算中会自动对齐不同索引的数据。

Series对象本身及其索引都有一个 `name` 属性，该属性跟Pandas其他的关键功能关系非常密切。

Series的索引可以通过赋值的方式就地修改。


```python
sdata + obj
```




    California         NaN
    Ohio           70000.0
    Oregon         32000.0
    Texas         142000.0
    Utah               NaN
    dtype: float64




```python
obj.name = 'population'
obj.index.name = 'state'
obj
```




    state
    California        NaN
    Ohio          35000.0
    Oregon        16000.0
    Texas         71000.0
    Name: population, dtype: float64




```python
obj.index = ['Tibet', 'Beijing', 'Tianjin', 'Henan']
obj
```




    Tibet          NaN
    Beijing    35000.0
    Tianjin    16000.0
    Henan      71000.0
    Name: population, dtype: float64



## DataFrame

DataFrame是一个表格型的数据结构，含有一组有序的列，每列可以时不同的值类型（数值、字符串、布尔值等）。

DataFrame既有行索引也有列索引，它可以被看成由Series组成的字典（共用同一个索引）。

跟其他类似的数据结构相比（如R的 `data.frame`），DataFrame中面向行和面向列的操作基本上时平衡的。

构建DataFrame的办法有很多种，最常用的一种是直接传入一个由等长列表或NumPy数组组成的字典，DataFrame会自动加上索引，且所有列会被有序排列：


```python
data = {'state': ['Ohio', 'Ohio', 'Ohio', 'Nevada', 'Nevada'],
            'year': [2000, 2001, 2002, 2001, 2002],
            'pop': [1.5, 1.7, 3.6, 2.4, 2.9]}
frame = DataFrame(data)
frame
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>pop</th>
      <th>state</th>
      <th>year</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1.5</td>
      <td>Ohio</td>
      <td>2000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1.7</td>
      <td>Ohio</td>
      <td>2001</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3.6</td>
      <td>Ohio</td>
      <td>2002</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2.4</td>
      <td>Nevada</td>
      <td>2001</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2.9</td>
      <td>Nevada</td>
      <td>2002</td>
    </tr>
  </tbody>
</table>
</div>



如果指定了列序列，则DataFrame的列就会按照指定顺序进行排列，如果传入的列在数据中找不到，则会产生NaN值。

除了指定列序列，还可以指定行索引序列，而不是使用默认的数字索引。


```python
frame2 = DataFrame(data, columns=['year', 'state', 'pop', 'debt'],
                   index=['one', 'two', 'three', 'four', 'five'])
frame2
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>state</th>
      <th>pop</th>
      <th>debt</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>one</th>
      <td>2000</td>
      <td>Ohio</td>
      <td>1.5</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>two</th>
      <td>2001</td>
      <td>Ohio</td>
      <td>1.7</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>three</th>
      <td>2002</td>
      <td>Ohio</td>
      <td>3.6</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>four</th>
      <td>2001</td>
      <td>Nevada</td>
      <td>2.4</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>five</th>
      <td>2002</td>
      <td>Nevada</td>
      <td>2.9</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



通过类似字典标记的方式或属性的方式，可以将DataFrame的列获取为一个Series。

返回的Series拥有原DataFrame相同的索引，而且其 `name` 属性也已经被相应的设置好狼（抽取的列名）。


```python
frame2['state']  # or frame2.state
```


    one        Ohio
    two        Ohio
    three      Ohio
    four     Nevada
    five     Nevada
    Name: state, dtype: object



行也可以通过位置或名称的方式进行获取，比如用索引字段 `ix` 获取：


```python
frame2.ix['three']  # or frame2.ix[2]
```




    year     2002
    state    Ohio
    pop       3.6
    debt      NaN
    Name: three, dtype: object



列可以通过赋值的方式进行修改：

* 使用标量赋值会赋值给整列；
* 使用列表或数组给某个列赋值时，其长度必须跟DataFrame的长度相匹配（如果不匹配，会抛出ValueError异常）；
* 如果赋值的是一个Series，会精确匹配DataFrame的索引，所有空位都将被填上缺失值 `NaN`；
* 为不存在的列赋值会创建出一个新列；
* 关键字 `del` 用于删除列。

需要注意的是：通过索引方式返回的列只是相应数据的视图而已，并不是副本。因此，任何对返回的Series的就地修改全部会反应到源DataFrame上。通过Series的 `copy` 方法可以显式的复制列。

除了接受由数组组成的字典外，DataFrame还可以接受其他很多中数据输入：

1. 嵌套字典，如：{'Nevada': {2001: 2.4, 2002: 2.9}, 'Ohio': {2000: 1.5, 2001: 1.7, 2002: 3.6}}
2. 二维ndarray：数据矩阵，还可以传入行标和列标
3. 由数组、列表或元组组成的字典：每个序列会变成DataFrame的一列，所有序列的长度必须相同
4. NumPy的结构化／记录数组：类似于“由数组组成的字典”
5. 由Series组成的字典：每个Series会成为一列，如果没有显式指定索引，则各Series的索引会被合并成结果的行索引
6. 字典或Series的列表：各项将会成为DataFrame的一行，字典键或Series索引的并集将会成为DataFrame的列标
7. 由列表或元组组成的列表：类似于“二维ndarray“
8. 另一个DataFrame：该DataFrame的索引将会被沿用，除非显式的指定列其他索引
9. NumPy的MaskedArray：类似于“二维ndarray”的情况，只是掩码值在结果DataFrame中会变成NA/缺失值

## 索引对象

Index对象是Pandas数据模型的重要组成部分。

Pandas的索引对象负责管理轴标签和其他元数据（比如轴名称等）。构建Series或DataFrame时，所用到的任何数组或其他序列的标签都会被转换成一个Index对象。

Index对象是不可修改的（immutable），因此用户不能对其进行修改。Index对象的不可修改性非常重要，因为这样才能使Index对象在多个数据结构之间安全共享。

Pandas库中内置了一些常用的Index类：

* Index：最泛化的Index对象，将轴标签表示为一个由Python对象组成的NumPy数组，
* Int64Index：针对整数的特殊Index，
* MultiIndex：“层次化”索引对象，表示单个轴上的多层索引，可以看作由元组组成的数组，
* DatetimeIndex：存储纳秒级的时间戳（用NumPy的 `datetime64` 类型表示），
* PeriodIndex：针对Period数据（时间间隔）的特殊Index

除了这些常用的Index类型，Index甚至还可以被继承从而实现特别的轴索引功能。

Index对象长得很像数组，功能也很类似一个固定大小的集合。


```python
frame2.index.name = 'number'
frame2
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>state</th>
      <th>pop</th>
      <th>debt</th>
    </tr>
    <tr>
      <th>number</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>one</th>
      <td>2000</td>
      <td>Ohio</td>
      <td>1.5</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>two</th>
      <td>2001</td>
      <td>Ohio</td>
      <td>1.7</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>three</th>
      <td>2002</td>
      <td>Ohio</td>
      <td>3.6</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>four</th>
      <td>2001</td>
      <td>Nevada</td>
      <td>2.4</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>five</th>
      <td>2002</td>
      <td>Nevada</td>
      <td>2.9</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




```python
'state' in frame2.columns or 'one' in frame2.index
```




    True



每个索引都有一些方法和属性，它们可用于设置逻辑并回答有关该索引所包含的数据的常见问题。下面是一些比较常用的函数：

- append：连接另一个Index对象，产生一个新的 Index
- diff：计算差集，并得到一个新的 Index
- intersection：计算交集
- union：计算并集
- isin：计算一个指示各值是否都包含在参数集合中的布尔型数组
- delete：删除指定索引处的元素，并得到新的 Index
- drop：删除传入的值，并得到新的 Index
- insert：将元素插入到索引处，并得到新的 Index
- is_monotonic：当各元素均大于等于前一个元素时，返回 True
- is_unique：当Index没有重复值时，返回 True
- unique：计算Index中唯一值的数组

