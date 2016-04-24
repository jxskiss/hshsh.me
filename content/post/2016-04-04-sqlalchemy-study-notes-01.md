+++
Categories = ["Python"]
Description = ""
Tags = ["sqlalchemy", "python"]
date = "2016-04-04T19:18:09+08:00"
menu = "main"
title = "SQLAlchemy学习笔记（一）"

+++

这篇笔记部分内容来自网络[^fn-copyright]，部分来自对《Essential SQLAlchemy》的学习和使用经验。

[^fn-copyright]: 出处已不可考，如有侵权请联系我。

----

[SQLAlchemy](http://www.sqlalchemy.org/)是 Python 编程语言下的一款开源软件。提供了SQL工具包及对象关系映射（ORM）工具，使用MIT许可证发行。

SQLAlchemy“采用简单的Python语言，为高效和高性能的数据库访问设计，实现了完整的企业级持久模型”。

SQLAlchemy的理念是，SQL数据库的量级和性能重要于对象集合；而对象集合的抽象又重要于表和行。因此，SQLAlchmey 采用了类似于Java里 Hibernate 的数据映射模型，而不是其他ORM框架采用的 Active Record 模型。不过，Elixir 和 declarative 等可选插件可以让用户使用声明语法。

SQLAlchemy首次发行于2006年2月，并迅速地在Python社区中最广泛使用的ORM工具之一，不亚于Django的ORM框架。

以上摘自[维基百科](https://zh.wikipedia.org/wiki/SQLAlchemy)。

----

使用`SQLAlchemy`有三种方式：

- 使用 Raw SQL
- 使用 SQL Expression
- 使用 ORM

前两种方式可以统称为 core 方式。

对于绝大多数应用，推荐使用 `SQLAlchemy`，即使是使用 Raw SQL，也可以带来如下好处。

1. 内建数据库连接池。**注意：**如果是 SQLAlchemy + cx_oracle 的话，需要禁用 Connection Pool，否则会有异常。方法是设置`sqlalchemy.poolclass`为`sqlalchemy.pool.NullPool`
2. 强大的日志功能（log）
3. 数据库无关的写法，包括：SQL参数写法、LIMIT语法等
4. 特别提一下，WHERE 条件的 `== value` 写法，如果`value`等于`None`，真正的SQL会转为 `IS NULL`

SQLAlchemy 的 Raw SQL 和 SQL Expression 比较：

1. SQL Expression 的写法是纯 Python 代码，阅读性更好，尤其是在使用 `insert()` 方法时，字段名和取值成对出现。
2. Raw SQL 比 SQL Expression 更灵活，如果 SQL/DDL 很复杂，Raw SQL 就更有优势了。

## 常用数据库连接字符串


```python
import sqlalchemy
from sqlalchemy import create_engine

# file database
# sqlite = create_engine('sqlite:////absolute/path/to/database.db')
# in-memory database, two ways
# sqlite = create_engine('sqlite://')
sqlite = create_engine('sqlite:///:memory:')
# postgresql
pgsql = create_engine('postgres://user:passwd@host:port/database')
# mysql
mysql = create_engine('mysql://user:passwd@host:port/database')
# oracle
oracle = create_engine('oracle://user:passwd@host:port/sidname')
# oracle via TNS name
oracle_tns = create_engine('oracle://user:passwd@tnsname')
# ms sql server using ODBC datasource names.
PyODBC is the default driver
# mssql = create_engine('mssql://mydsn')
mssql = create_engine('mssql://user:passwd@mydsn')
# firebird
firebird = create_engine('firebird://user:passwd@host/some.gdm')
```

## Connection less 执行和 Connection 执行

直接使用 `engine` 执行SQL的方式，叫做 connection less 执行。

先使用 `engine.connect()` 获取连接对象 `conn`，然后通过 `conn` 执行SQL的方式，叫做 connection 执行。

如果要在 transaction 模式下执行，推荐使用 connection 方式；如果不涉及 transaction，两种方法效果是一样的。

## 使用`text()`函数封装SQL字符串

使用 `text()` 函数有很多好处：

1). 不同数据库，可以使用统一的SQL参数传递写法，参数需以“冒号”引出，在调用 `execute()` 的时候，使用 dict 结构将实参传进去。


```python
from sqlalchemy import text

result = db.execute(
   text('select * from table where id < :id and typeName = :type'),
   {'id': 2, 'type': 'USER_TABLE'})
```

2). 如果不指定参数的类型，默认为字符串类型；如果要传递日期参数，需要使用 `text()` 的 `bindparams` 参数来声明。


```python
from datetime import datetime, timedelta
from sqlalchemy import DateTime, bindparam

# ten days ago
date_param = datetime.today() + timedelta(days=-1*10)
sql = 'delete from caw_job_alarm_log where alarm_time < :alarm_time_param'
t = text(sql, bindparams=[
        bindparam('alarm_time_param', type_=DateTime, required=True)])
db.execute(t, {'alarm_time_param': date_param})
```

> 参数 `bindparam` 可以使用 `type_` 来制定参数的类型，也可以使用 initial 值来指定参数的类型。

    bindparam('alart_time_param', type_=DateTime)  # or
    bindparam('alart_time_param', DateTime())

3). 如果要转换查询结果中的数据类型，可以通过 `text()` 的参数 `typemap` 参数指定。这点比 mybatis 还灵活：


```python
from sqlalchemy import Integer, Unicode

t = text('select id, name from users',
         typemap={'id': Integer, 'name': Unicode})
```

4). 其他好处，详见 sqlalchemy/sql/expression.py 中的 docstring。

## SQLAlchemy 访问数据库

`create_engine` 函数返回一个 `Engine` 对象。通过 `Engine` 对象的 `execute` 方法可以执行数据库操作。

`execute` 方法返回一个 `ResultProxy` 对象，`ResultProxy` 类是对 `Cursor` 类的封装，其中的 `cursor` 属性对应原来的 `cursor`，这个类有很多方法对应着 `Cursor` 类的方法，另外又扩展了一些属性和方法。

对 `ResultProxy` 对象进行遍历时，得到的每一行都是一个 `RowProxy` 对象，获取字段的方法非常灵活，索引、字段名，甚至属性都行。

    row_proxy[0] == row_proxy['id'] == row_proxy.id

看得出来，`RowProxy` 跟Java的 POJO 类有相似的特性。


```python
from sqlalchemy import create_engine

db = create_engine('sqlite:///:memory:', echo=True)

# DDL
db.execute('create table users(userid char(10), username char(50))')

# DML
result = db.execute(
    "insert into users (userid, username) values ('user1', 'tony')")
# get rows affected by an UPDATE or DELETE statement,
# it is not intended to provide the number of rows present from SELECT
result.rowcount
# True if this ResultProxy returns rows.
result.returns_rows

# Query
result = db.execute("select * from users")
result.scalar()  # 可以返回一个标量查询的值
result.fetchall()   # 取回所有的行
result.fetchmany()  # 取回多行
result.fetchone()   # 取回一行，并判断有且只有一行，若超出一行则报错
result.first()      # 取回第一行
result.close()  # result 用完之后，需要关闭
```

SQLAlchemy 支持事务，甚至可以嵌套事务。

缺省情况下事务自动提交，即执行一条SQL就自动提交。

如果要更精准的控制事务，最简单的方法是使用 `connection`，然后通过 `connection` 获取 `transaction` 对象。


```python
# transaction
connection = db.connect()
trans = connection.begin()
try:
    do_something_with(connection)
    trans.commit()
except:
    trans.rollback()
```

还有一种方式是在创建 `engine` 对象时指定 `strategy='threadlocal'` 参数，这样会自动创建一个线程局部的连接，对于后续的无连接的执行都会自动使用这个连接，这样在处理事务时，只要使用 `engine` 对象来操作事务就行了。

例如：


```python
db = create_engine(connection, strategy='threadlocal')
db.begin()
try:
    do_something()
except:
    db.rollback()
else:
    db.commit()
```

如果希望手动提交事务，也可以在 `connection` 和 `statement` 上通过 `execute_options()` 方法修改为手动提交模式。

    conn.execute_options(autocommit=False)

设置为手动提交模式后，要提交事务，需要调用 `conn.commit()` 方法。

## 数据库连接池

SQLAlchemy 默认的连接池算法选用规则为：

1. 连接内存中的 SQLite，默认的连接池算法为 `SingletonThreadPool` 类，即两个线程允许一个连接；
2. 连接基于文件的 SQLite，默认的i连接池算法为 `NullPool` 类，即不使用连接池；
3. 对于其他情况，默认的连接池算法为 `QueuePool` 类。

我们也可以实现自己的连接池算法：

    db = create_engine('sqlite:///file.db', poolclass=YourPoolClass)

`create_engine()` 函数和连接池相关的参数有：

- pool_recycle: 默认为-1，推荐设置为7200，即如果 `connection` 空闲了 7200秒 = 2小时，自动重新获取，以防止 `connection` 被数据库服务器关闭；
- pool_size: 保持连接数，默认为5，正式环境下该数值偏小，需根据实际情况调整；
- max_overflow: 超出 `pool_size` 后允许的最大连接数，默认为10，这10个连接在使用过后，不放在连接池中，而是被真正关闭的。
- pool_timeout: 获取连接的超时阀值，默认为30秒。

国内的云服务平台 [SAE](http://sae.sina.com.cn) 中的共享型 MySQL 服务不支持连接池，如果在其上部署应用，需要禁用连接池，也就是使用 `NullPool` 类，否则会报 '(2006, MySQL server has gone away)' 错误。

## 日志输出

SQLAlchemy 默认输出日志到 `sys.stdout`。

如果要输出到文件，log 文件不具备 rotate 功能，不推荐在生产环境中使用。

    import logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

调用 `create_engine()` 函数时，可选传递一个参数 `echo=True` 来打开详细信息输出，这个功能信息量非常大，只适合调试使用，不建议生产环境中使用。

## 最佳实践与使用心得

使用 ORM 方式构建复杂查询比较困难，使用 Raw SQL 和 SQL Expression 会比较合适一些。

`declarative` 是 SQLAlchemy 的一个新的扩展功能 ，只能用在 ORM 方式中，不适用在 Raw SQL 和 SQL Expression 方式。

如果使用 ORM 方式，表必须有主键，使用 Raw SQL 和 SQL Express 方式没有这个约束。

查询有简单的也有复杂的，使用 Raw SQL 会比较方便。

增、删、改，多是单表操作，使用 SQL Expression 就足够了。具体讲，比如一个 `User` 类，**可以包含一个固定的 `_table` 成员**，增删改直接使用 `_table` 对象来完成。

    _table = Table('users', metadata, autoload=True)

批量的 insert/update/delete 操作，可以将每行数据组成一个 dict，在将这些 dict 组成一个 list，和 _table.insert()/update()/delete() 一起作为参数传给 `conn.execute()'。


```python
from sqlalchemy import Table

# _table member object
_table = Table('users', metadata, autoload=True)
# insert
_table.insert().values(f1=value1, f2=value2)
# update
_table.update().values(f1=new_value1, f2=new_value2).where(
    _table.c.f1 == value1).where(_table.c.f2 == value2)
# delete
_table.delete().where(_table.c.f1 == value1).where(
    _table.c.f2 == value2)

# batch opration
conn.execute(_table.insert(), [
        {'user_id': 1, 'email_address': 'jack@yahoo.com'},
        {'user_id': 1, 'email_address': 'jack@msn.com'},
        {'user_id': 2, 'email_address': 'susan@example.com'},
        {'user_id': 2, 'email_address': 'susan@example.org'}
    ])
```

SQL Expression 也可以像 Raw SQL 的 `text()` 函数一样使用 `bindparam`，方法是在调用 insert()/update()/delete() 时声明参数，然后在 `conn.execute()` 执行时候，将参数传递进去。


```python
d = _table.delete().where(_table.c.hire_date <= bindparam(
    'hire_day', DateTime(), required=True))
conn.execute(d, {'hire_day': datetime.today()})
```

`where()` 和 ORM 中的 `filter()` 接受一样的参数，各种SQL条件都支持：


```python
# equals, not equals
where(_table.c.name == 'ed')
where(_table.c.name != 'ed')
# like
where(_table.c.name.like('%ed%'))
# in, not in
where(_table.c.name.in_(['ed', 'wendy', 'jack']))
where(~_table.c.name.in_(['ed', 'wendy', 'jack']))
# is null, is not null
where(_table.c.name == None)
where(_table.c.name != None)

# and, or
from sqlalchemy import and_, or_
where(and_(_table.c.name == 'ed', _table.c.fullname == 'Ed Jones'))
where(or_(_table.c.name == 'ed', _table.c.name == 'wendy'))
# and can also be written with multiple where clause
where(_table.c.name == 'ed').where(_table.c.fullname == 'Ed Jones')

# match: contents of the match parameter are database backend specific
where(_table.c.name.match('wendy'))
```

