+++
Categories = ["Python"]
Description = ""
Tags = ["python", "design pattern"]
date = "2016-04-10T23:30:00+08:00"
menu = "main"
title = "Python代理类两例"

+++

最近遇到MySQL的连接断开，MySQLdb报'(2006, MySQL server has gone away.)'错误的问题。

问题发生的环境是，客户端使用了长连接，程序启动的时候使用MySQLdb模块的connect方法建立一个数据库连接，程序运行期间一直使用这个连接。对于请求比较多的服务程序来说，这个方法不会出现问题，因为MySQL默认连接超时的时间设定是8小时，所以连接不会超时断开，也就不会报这个错误了。但是作为一个调试服务，请求频率可能低于8小时，就导致错误了。

由于不想修改很多具体实现的代码，所以使用**代理类**的方法对这个程序打了个补丁解决问题。

另外 SQLAlchemy 中的 `scoped_session` 也是一个代理类，实现也很有意思，这里一起分享一下这两个代理类。

## MySQLdb Connection 代理类

先看看出问题的代码：

```python
import MySQLdb
conn = MySQLdb.connect(host='host', port='port',
                       user='user', passwd='passwd', db='db')

def use_mysql():
    cursor = conn.cursor()
    cursor.execute('do something with mysql database;')
    cursor.close()
```

`MySQLdb.connect`函数返回的是一个`Connection`对象，当操作频率大于8个小时的时候，MySQL服务器就会关闭连接，然后下一次执行 `cursor = conn.cursor()` 的时候，就会报连接丢失的错误。为了既使用长连接，又能避免这个错误，我们可以封装一个`Connection`类的代理类，重载 `cursor` 方法，当有新的请求的时候，先检查连接是否还在，如果连接丢失的话，就重新连接数据库，然后再调用 `Connection` 类的 `cursor` 方法并返回结果：

```python
import MySQLdb
from MySQLdb.connections import Connection

class ProxyConnection(Connection):
    def __init__(self, *args, **kwargs):
        # 保存数据库连接参数以备丢失时候重新连接
        self.args = args
        self.kwargs = kwargs
        super(ProxyConnection, self).__init__(*args, **kwargs)

    def cursor(self, cursorclass=None):
        try:
            self.ping()
        except MySQLdb.OperationalError:
            super(ProxyConnection, self).__init__(*self.args, **self.kwargs)
        return super(ProxyConnection, self).cursor(cursorclass)

conn = ProxyConnection(host='host', port='port',
                       user='user', passwd='passwd', db='db')

def use_mysql():
    cursor = conn.cursor()
    cursor.execute('do something with mysql database;')
    cursor.close()
```

这个代理类，只重载 `cursor()` 这一个方法，其他方法直接继承自父类 `Connection`。

这样就解决了MySQL数据库连接丢失的问题。但是这个方法并不是完美的，主要的缺点是每次处理新的请求时，都要 `ping()` 一下，当请求比较多的时候，会增加不必要的开支。不过如果真的请求多的话，也就不会出现这个问题了。作为低请求频次服务的解决方法，这个代理类用起来还是很方便的。

相对于这种粗糙的方法，SQLAlchemy中 `scoped_session` 类对 Session 类的代理实现就精巧的多了，而且它并没有从被代理的 `session` 类继承，而是一个完全独立的类（实际上`scoped_session`是一种 [Registry 设计模式](http://martinfowler.com/eaaCatalog/registry.html)，实现了一些高级功能，不过这里暂时只看它的代理作用）。


## SQLAlchemy 代理类 `scoped_session`

SQLAlchemy 的 Session 类是 SQLAlchemy ORM 模型对数据库操作的主要接口，定义了`query`, `execute`, `flush`, `commit`, `rollback`, `refresh`, `close`, `remove`等方法。

```pyhton
# file: sqlalchemy/orm/session.py

class Session(_SessionClassMethods):
    """Manages persistence operations for ORM-mapped objects.

    The Session's usage paradigm is described at :doc:`/orm/session`.
    """

    public_methods = (
        '__contains__', '__iter__', 'add', 'add_all', 'begin', 'begin_nested',
        'close', 'commit', 'connection', 'delete', 'execute', 'expire',
        'expire_all', 'expunge', 'expunge_all', 'flush', 'get_bind',
        'is_modified', 'bulk_save_objects', 'bulk_insert_mappings',
        'bulk_update_mappings',
        'merge', 'query', 'refresh', 'rollback',
        'scalar')

    # def __init__(...):
    #     ...
```

Session类的对象可以通过 `sessionmaker(bind=engine)()` 建立，由使用数据库的模块建立、使用，并自行管理。`scoped_session` 类给 Session 对象提供了一层透明代理，既可以像使用 Session 对象一样使用，又可以对 Session 对象进行统一管理。

`scoped_session` 类的实现代码并不复杂，而且相当的精巧，下面是全部代码（为方便阅读，已删除文档字符串）：

```
# file: sqlalchemy/orm/scoping.py

class scoped_session(object):
    session_factory = None

    def __init__(self, session_factory, scopefunc=None):
        self.session_factory = session_factory
        if scopefunc:
            self.registry = ScopedRegistry(session_factory, scopefunc)
        else:
            self.registry = ThreadLocalRegistry(session_factory)

    def __call__(self, **kw):
        if kw:
            scope = kw.pop('scope', False)
            if scope is not None:
                if self.registry.has():
                    raise sa_exc.InvalidRequestError(
                        "Scoped session is already present; "
                        "no new arguments may be specified.")
                else:
                    sess = self.session_factory(**kw)
                    self.registry.set(sess)
                    return sess
            else:
                return self.session_factory(**kw)
        else:
            return self.registry()

    def remove(self):
        if self.registry.has():
            self.registry().close()
        self.registry.clear()

    def configure(self, **kwargs):
        if self.registry.has():
            warn('At least one scoped session is already present. '
                 ' configure() can not affect sessions that have '
                 'already been created.')

        self.session_factory.configure(**kwargs)

    def query_property(self, query_cls=None):
        class query(object):
            def __get__(s, instance, owner):
                try:
                    mapper = class_mapper(owner)
                    if mapper:
                        if query_cls:
                            # custom query class
                            return query_cls(mapper, session=self.registry())
                        else:
                            # session's configured query class
                            return self.registry().query(mapper)
                except orm_exc.UnmappedClassError:
                    return None
        return query()

"""Old name for backwards compatibility."""
ScopedSession = scoped_session


def instrument(name):
    def do(self, *args, **kwargs):
        return getattr(self.registry(), name)(*args, **kwargs)
    return do

for meth in Session.public_methods:
    setattr(scoped_session, meth, instrument(meth))


def makeprop(name):
    def set(self, attr):
        setattr(self.registry(), name, attr)

    def get(self):
        return getattr(self.registry(), name)

    return property(get, set)

for prop in ('bind', 'dirty', 'deleted', 'new', 'identity_map',
             'is_active', 'autoflush', 'no_autoflush', 'info'):
    setattr(scoped_session, prop, makeprop(prop))


def clslevel(name):
    def do(cls, *args, **kwargs):
        return getattr(Session, name)(*args, **kwargs)
    return classmethod(do)

for prop in ('close_all', 'object_session', 'identity_key'):
    setattr(scoped_session, prop, clslevel(prop))
```

撇开复杂的部分不说，暂时之看这个类的透明代理性质：

1. 当程序需要连接数据库的时候，可以使用 `scoped_session`，像使用`Session`类一样，`Session`支持的方法都支持；
2. **`scoped_session` 类通过 `instrument`, `makeprop`, `clslevel` 这几个函数把 `Session` 类的方法属性“挂接”到自己身上，实现了对 `Session` 类的透明代理**；
3. `scoped_session` 类通过维护 Registry 来实现程序的不同部分可以共用 Session，既节省资源，又方便不同部分共享数据（不知道这样理解对不对？）；
4. `scoped_session` 对象的作用域是线程局部的，类内部通过以 `threading.local()` 作为 Registry 的键值，来区分不同线程中的对象，不同的线程不共享Session对象，这样就实现了线程安全，写程序的时候只需要使用 `scoped_session` 来操作就好了，而不需要再关注线程相关的东西了。

----

有时候，代理类用着还是很方便的。我是一个初学者，如果本文中有谬误，请不吝指正。

