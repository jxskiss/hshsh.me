+++
Categories = ["Programming", "OPS"]
Description = "Consistent hashing."
Tags = ["ops", "nginx", "openresty", "tricks"]
date = "2017-10-29T01:40:00+08:00"
menu = "main"
title = "用OpenResty构建动态代理服务"

+++

最近的项目使用了前后端分离的开发模式，前后端都在同一台机器上开发，需要对前后端开发配置联调服务。解决这个问题方法很多，Nginx/OpenResty 是其中一种。

后来又有其他项目的前端后端同学也在这台服务器上做开发。

后来，这台服务器绑定了多个域名，要对多个域名、多个端口做解析。

再后来，其中一个项目的后端开始以微服务的方式开发，对不同路径要代理到不同的后端开发端口上去。

既然已经走了这么远，索性再扩展一下，除了支持代理到端口，再加上指定文件夹静态文件服务呗，于是有了下面的配置。

功能列表：

1. 一个端口支持多域名，访问不同域名可以转发到不同上游服务
2. 一个域名下，可以按照项目分组，不同项目可以配置不同后端服务
3. 一个项目可以根据路由配置多个对应后端服务
4. 支持不带后端路由的直接转发
5. 支持指定文件夹静态文件服务
6. 上述一切都可以通过接口在线配置，不需要修改 Nginx/OpenResty 配置文件，并且自带接口文档

依赖：OpenResty，安装请参考[官方文档](https://openresty.org/cn/installation.html)。


```conf
# #### OpenResty dynamic upstreams ####

# 配置表，key 有三种格式
#   1. example.domain.name:port_number
#      value 有三种格式：
#      - upstream_ip:port
#      - upstream_ip:port,project
#      - /absolute/path/to/document/root
#   2. example.domain.name:project_name
#      value JSON格式的路由表
#   2. kv:runtime_variable_name
#      value 所有请求共享的运行时变量
lua_shared_dict dyn_registry 1m;

server {
    # 把可以配置的端口全部注册在这里，一行一个，比如 9000 - 9009
    listen       9000;
    listen       9001;
    # listen     ...
    listen       9008;
    listen       9009;

    # 接受请求的域名，全部写在一行，用空格分开
    # 上面注册的端口对所有域名都可用
    server_name  dyn1.hshsh.me dyn2.hshsh.me;

    access_log   /path/to/access_or_dynamic.log main;
    error_log    /path/to/error_or_dynamic.log notice;

    default_type  application/json;

    set $dyn_conf_file "/path/to/or-dynamic.json";

    # 无论是配置请求，还是代理请求，第一个请求都需要触发配置加载，
    # 因此这两个 set 指令需要放在 server 块中，所有 location 都会继承
    set $upstream "";
    set_by_lua_block $docroot {
        local cjson = require "cjson"
        local registry = ngx.shared.dyn_registry

        -- 配置成请求触发加载可以不用写全局的 init_by_lua* 指令，
        -- 方便与其他 OpenResty 服务集成
        if not registry:get("kv:loaded") then
            local file, err = io.open(ngx.var.dyn_conf_file, "rb")
            if not file then
                ngx.log(ngx.ERR, "error opening config file: ", err)
            else
                local contents = file:read("*all")
                file:close()
                local suc, config = pcall(cjson.decode, contents)
                if not suc then
                    ngx.log(ngx.ERR, "error decoding config file")
                else
                    for k, v in pairs(config) do
                        -- 第一种 key, domain:port
                        if k:match(":%d+$") then
                            registry:set(k, v)
                        -- 第二种 key, domain:project
                        else
                            registry:set(k, cjson.encode(v))
                        end
                    end
                end
            end
            registry:set("kv:loaded", "true")
        end

        -- 对于配置请求不需要查配置表，配置接口可以在所有域名和端口上访问
        if ngx.re.match(ngx.var.uri, "^/or-dynamic/") then
            return ""
        end

        -- 根据域名和端口查配置，如果查不到则是没有注册，直接返回
        -- set 指令中不能响应请求，在 / location 中会返回 404
        local http_host = ngx.var.http_host
        local upstream = registry:get(http_host)
        if not upstream then
            return ""
        end

        -- upstream_ip:port, 项目无关，没有后端路由的直接代理
        if upstream:match(":%d+$") then
            ngx.var.upstream = upstream
            return ""
        end

        -- 没有逗号，文档根目录路径，所以不支持配置带有逗号的路径
        if not upstream:match(",") then
            return upstream
        end

        -- upstream_ip:port,project, 项目前端配置
        -- 根据路由表确定是否需要转发后端服务
        local proj, routes, uri, dest, m, err
        m, err = ngx.re.match(upstream, [=[([^,]+),([^,]+)]=])
        upstream, proj = m[1], m[2]
        routes = cjson.decode(registry:get(ngx.var.host .. ":" .. proj))
        for uri, dest in pairs(routes) do
            if dest and ngx.re.match(ngx.var.uri, uri) then
                upstream = dest
                break
            end
        end
        ngx.var.upstream = upstream
        return ""
    }

    # 方便开发调试，给每个请求加上 upstream 和 docroot 的响应头
    header_filter_by_lua_block {
        ngx.header["OR-Dyn-Upstream"] = ngx.var.upstream
        ngx.header["OR-Dyn-Docroot"] = ngx.var.docroot
    }

    location / {
        proxy_set_header Host $Host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;

        # upstream 需要在处理 docroot 之前处理, if is evil
        # https://www.nginx.com/resources/wiki/start/topics/depth/ifisevil/
        if ($upstream != "") {
            proxy_pass http://$upstream;
            break;
        }

        # upstream 没有命中，docroot 也没有命中，则没有注册，可以洗洗睡了
        if ($docroot = "") {
            return 404;
        }

        root $docroot;
        index index.html index.htm;

        # 对于静态文件服务，如果需要支持 history 模式路由的前端单页面应用，取消注释下面这一行
        # try_files $uri $uri/ /index.html =404;

        error_page   500 502 503 504  @5xx;
    }

    # 方便开发调试，把抛 5xx 错误的 upstream 直接显示在页面上
    location @5xx {
        default_type text/plain;
        content_by_lua_block {
            ngx.say("oops: " .. ngx.var.upstream)
        }
    }

    # 当前配置查询接口
    location = /or-dynamic/ {
        content_by_lua_block {
            local cjson = require "cjson"
            local registry = ngx.shared.dyn_registry

            -- 自包含的接口文档
            local config = {
                help = {
                    [ "parameters" ] = {
                        host = "域名, eg: example.domain.name",
                        port = "端口号, eg: 9001",
                        upstream = "上游服务, eg: 127.0.0.1:6666",
                        docroot = "静态文件根目录, eg: /absolute/path/to/document/root",
                        uri = "后端服务路由，支持PCRE, eg: ^/api/v1/"
                    },
                    -- 配置项目无关的直接代理
                    [ "direct proxy" ] = {
                        set = "/or-dynamic/set?host=&port=&upstream=",
                        del = "/or-dynamic/del?host=&port="
                    },
                    -- 配置静态文件服务根目录
                    [ "document root" ] = {
                        set = "/or-dynamic/set?host=&port=&docroot=",
                        del = "/or-dynamic/del?host=&port="
                    },
                    -- 配置项目前端代理
                    [ "project frontend" ] = {
                        set = "/or-dynamic/set?host=&proj=&port=&upstream=",
                        del = "/or-dynamic/del?host=&port="
                    },
                    -- 配置项目后端路由
                    [ "project backend" ] = {
                        set = "/or-dynamic/set?host=&proj=&uri=&upstream=",
                        del = "/or-dynamic/del?host=&proj=&uri="
                    }
                }
            }

            # 按照域名和项目分组
            for _, k in ipairs(registry:get_keys()) do
                if not k:match("^kv:") then
                    local v = registry:get(k)
                    local req_type, host, proj, port, upstream, docroot, routes, m, err
                    m, err = ngx.re.match(k, [=[^([^:]+):(\d+)$]=])
                    if m then  -- host:port
                        host, port = m[1], m[2]
                        if v:match(":%d+$") then  -- direct proxy
                            req_type = "proxy"
                            upstream = v
                        elseif not v:match(",") then  -- document root
                            req_type = "docroot"
                            docroot = v
                        else  -- project frontend
                            req_type = "frontend"
                            m, err = ngx.re.match(v, [=[^([^,]+),([^,]+)$]=])
                            upstream, proj = m[1], m[2]
                        end
                    else  -- project backend routes
                        req_type = "backend"
                        m, err = ngx.re.match(k, [=[([^:]+):([^:]+)]=])
                        host, proj = m[1], m[2]
                    end

                    if not config[host] then
                        config[host] = {}
                    end
                    if req_type == "docroot" then
                        config[host][port] = docroot
                    elseif req_type == "proxy" then
                        config[host][port] = upstream
                    else  -- project frontend or backend
                        if not config[host][proj] then
                            config[host][proj] = {}
                        end
                        if req_type == "frontend" then
                            config[host][proj][port] = upstream
                        else
                            config[host][proj]["routes"] = cjson.decode(v)
                        end
                    end
                end
            end
            ngx.say(cjson.encode(config))
        }
    }

    # 新增、修改配置接口
    location = /or-dynamic/set {
        content_by_lua_block {
            local cjson = require "cjson"
            local registry = ngx.shared.dyn_registry
            local args = ngx.req.get_uri_args()
            local is_valid = true
            local req_type, r_key, r_value, err

            -- host is required for requests of any type
            if not args or not args.host or args.host:len() == 0 then
                is_valid = false
                err = "parameter host required"
            end

            -- project frontend: host, proj, port, upstream
            -- project backend: host, proj, uri, upstream
            -- direct proxy: host, port, upstream
            -- document root: host, port, docroot
            if is_valid and (not req_type) and args.port and args.port:len() > 0 then
                r_key = args.host .. ":" .. args.port
                if args.upstream and args.upstream:len() > 0 then
                    if args.proj and args.proj:len() > 0 then
                        req_type = "frontend"
                        r_value = args.upstream .. "," .. args.proj
                    else
                        req_type = "proxy"
                        r_value = args.upstream
                    end
                elseif args.docroot and args.docroot:len() > 0 then
                    req_type = "docroot"
                    r_value = args.docroot
                end
            end
            if is_valid and (not req_type) and args.uri and args.uri:len() > 0 and
                    args.upstream and args.upstream:len() > 0 and
                    args.proj and args.proj:len() > 0 then
                req_type = "backend"
                r_key = args.host .. ":" .. args.proj
                local routes = cjson.decode(registry:get(routes_key) or "{}")
                routes[args.uri] = args.upstream
                r_value = cjson.encode(routes)
            end

            if req_type then
                registry:set(r_key, r_value)
                local res = ngx.location.capture("/or-dynamic/_save")
                if res.status ~= ngx.HTTP_OK then
                    err = "failed writing config file"
                else
                    ngx.redirect("/or-dynamic/")
                end
            end
            ngx.say(cjson.encode({error = err or "invalid or missing parameters"}))
        }
    }

    # 删除配置接口
    location = /or-dynamic/del {
        content_by_lua_block {
            local cjson = require "cjson"
            local args = ngx.req.get_uri_args()
            if (not args or not args.host or args.host:len() == 0 or
                    ((not args.port or args.port:len() == 0) and
                     (not args.proj or args.proj:len() == 0 or
                      not args.uri or args.uri:len() == 0))
                ) then
                ngx.say(cjson.encode({error = "missing parameters"}))
                return
            end

            local registry = ngx.shared.dyn_registry
            if args.port and args.port:len() > 0 then
                registry:delete(args.host .. ":" .. args.port)
            else
                local routes_key = args.host .. ":" .. args.proj
                local routes = cjson.decode(registry:get(routes_key) or "{}")
                local new = {}
                for uri, dest in pairs(routes) do
                    if dest and uri ~= args.uri then
                        new[uri] = dest
                    end
                end
                registry:set(routes_key, cjson.encode(new))
            end

            local res = ngx.location.capture("/or-dynamic/_save")
            if res.status ~= ngx.HTTP_OK then
                ngx.say(cjson.encode({error = "failed writing config file"}))
            else
                ngx.redirect("/or-dynamic/")
            end
        }
    }

    # 保存当前配置表到配置文件
    # internal 类型的 location 专门用于内部请求逻辑，外部访问不到
    location = /or-dynamic/_save {
        internal;
        content_by_lua_block {
            local cjson = require "cjson"
            local registry = ngx.shared.dyn_registry
            local config = {}

            for _, k in ipairs(registry:get_keys()) do
                -- 不保存运行时变量，只保存配置内容
                if not k:match("^kv:") then
                    local v = registry:get(k)
                    if ngx.re.match(k, [=[\:\d+$]=]) then  -- host:port
                        config[k] = v
                    else
                        config[k] = cjson.decode(v)
                    end
                end
            end

            -- assume we don't need lock to access config file
            local file, err = io.open(ngx.var.dyn_conf_file, "w")
            if file then
                file:write(cjson.encode(config))
                file:close()
                ngx.print("ok")
            else
                ngx.status = ngx.HTTP_INTERNAL_SERVER_ERROR
                ngx.log(ngx.ERR, "failed to save config: ", err)
                ngx.say(err)
            end
        }
    }

}
```