+++
Categories = ["Programming", "OPS"]
Description = "Consistent hashing."
Tags = ["ops", "nginx", "openresty"]
date = "2017-10-28T23:00:00+08:00"
menu = "main"
title = "静态编译OpenResty"

+++

有时候会需要静态编译OpenResty。

参考资料：<http://www.codingblog.cn/blog/9579.html>。

当前使用的编译脚本。Ubuntu 16.04 测试通过，需要 `build-essential` 包，使用 `sudo apt-get install build-essential` 安装。


```bash
#!/bin/bash

set -e

OPENRESTY_VER=1.11.2.5
LUAJIT_BUNDLE_VER="2.1-20170808"
wget https://openresty.org/download/openresty-${OPENRESTY_VER}.tar.gz
tar -xzf openresty-${OPENRESTY_VER}.tar.gz

cd openresty-${OPENRESTY_VER}

cd bundle/LuaJIT-${LUAJIT_BUNDLE_VER}

make -j8
make install PREFIX=`pwd`
LUAROOT=`pwd`
rm -rf lib/*.so*
cd ../..

mkdir -p extra-libs
cd extra-libs

PCRE_VER=8.39
rm -rf pcre-*
echo -n "downloading pcre-$PCRE_VER..."
wget -O pcre-$PCRE_VER.tar.bz2 "http://downloads.sourceforge.net/project/pcre/pcre/$PCRE_VER/pcre-$PCRE_VER.tar.bz2"
echo "ok"
tar -xjf pcre-$PCRE_VER.tar.bz2

ZLIB_VER=1.2.11
echo -n "downloading zlib-$ZLIB_VER..."
wget -O zlib-$ZLIB_VER.tar.gz http://zlib.net/zlib-$ZLIB_VER.tar.gz
echo "ok"
tar -xzf zlib-$ZLIB_VER.tar.gz

rm -rf openssl-*
rm -rf OpenSSL_1_0_1t*
echo -n "downloading OpenSSL_1_0_1t..."
wget https://github.com/openssl/openssl/archive/OpenSSL_1_0_1t.tar.gz
echo "ok"
tar -xzf OpenSSL_1_0_1t.tar.gz

cd ..

OPENRESTY_PREFIX=/opt/openresty
NGINX_TEMP_PREFIX=$OPENRESTY_PREFIX/temp
./configure -j8 \
    --prefix=$OPENRESTY_PREFIX \
    --http-client-body-temp-path=$NGINX_TEMP_PREFIX/client_body \
    --http-proxy-temp-path=$NGINX_TEMP_PREFIX/proxy \
    --http-fastcgi-temp-path=$NGINX_TEMP_PREFIX/fastcgi \
    --http-uwsgi-temp-path=$NGINX_TEMP_PREFIX/uwsgi \
    --http-scgi-temp-path=$NGINX_TEMP_PREFIX/scgi \
    --with-luajit=$LUAROOT \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_auth_request_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_slice_module \
    --with-http_stub_status_module \
    --with-http_v2_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-stream \
    --with-stream_ssl_module \
    --with-ipv6 \
    --with-pcre-jit \
    --with-pcre=./extra-libs/pcre-$PCRE_VER \
    --with-zlib=./extra-libs/zlib-$ZLIB_VER \
    --with-openssl=./extra-libs/openssl-OpenSSL_1_0_1t

make -j8

cp build/nginx-1.11.2/objs/nginx ./openresty
# make install
```