+++
Categories = ["Programming", "Frontend"]
Description = "Single file vue webpack config."
Tags = ["programming", "frontend", "vuejs", "webpack"]
date = "2017-10-22T16:30:00+08:00"
menu = "main"
title = "单文件 Vue Webpack 配置"

+++

在今年的工作中接触到了前端框架 Vue.js 和构建工具 Webpack。虽然没写了几行前端界面代码，
不过对 Webpack 配置倒是花了一些时间学习，整理了一个针对 Vue.js 的单文件 Webpack 配置。
本文通过对配置文件的注释解析分享 Webpack 配置的一些要点。

本文中配置已经整理为一个糅合了 Django、Tornado、Vue.js、Webpack 的 [Django 项目模板](https://github.com/jxskiss/nice-pyvue-template)，主要作为学习记录用途。不过在 Django、Tornado 和 Webpack
的工程配置方面都有一些巧妙地处理，作为前后端分离的工程项目模板也是一个很好的开始（我就是这么用的）。欢迎 Star。

## 配置目标

1. 版本：Vue 2.0+、Webpack 2.0+
1. 支持单页面应用和多页面应用
1. 多页面应用，每个应用入口可选指定自己的HTML模板
1. 多页面应用，可以通过环境变量或命令行选项支持构建指定页面
1. 支持本地 devServer，可指定运行端口，指定开发页面
1. 支持 TypeScript，`.ts` 文件和 Vue.js 单文件组件

## 项目说明

### 目录结构

该配置是结合后端 Django 开发做的，因此前端文件放在 `frontend` 子目录中，
同时为了方便使用 `apidocjs` 编译API文档，`package.json`、`tsconfig.json`、
`webpack.config.js` 等前端配置文件放在项目根目录下。

对 Django 有所了解的同学，看到 `apps/` 子目录可能会感到奇怪，这里通过修改 `manage.py` 文件对
`startapp` 命令打了一个补丁，把所有新建 app 都放置在 `apps/` 子目录中以维持目录结构清晰。

```text
├── frontend/
│   ├── dist/  # 打包发布目录
│   ├── src/
│   │   ├── assets/  # 静态资源
│   │   │   ├── css/
│   │   │   └── images/
│   │   ├── components/  # 页面组件
│   │   │   └── Hello.vue
│   │   ├── pages/  # 页面代码
│   │   │   ├── demoapp/
│   │   │   │   ├── App.vue
│   │   │   │   ├── index.html  # 应用 HTML 模板文件
│   │   │   │   └── index.js
│   │   │   ├── App.vue
│   │   │   ├── index.html  # 缺省 HTML 模板文件
│   │   │   └── index.ts
│   │   ├── plugins/  # 封装插件
│   │   └── utils/  # 通用 Util 代码
│   └── static  # 发布时需要拷贝到 dist 目录的静态文件
├── node_modules/
├── package.json
├── tsconfig.json  # TypeScript 配置
├── webpack.config.js  # Webpack 单文件配置
├── manage.py
├── apps/  # 后端 Django 应用代码
│   ├── app1/
│   └── app2/
└── project_name/  # 后端 Django 项目配置
```

### NPM包依赖

1. Vue.js 2.5+，Vue 2.5 开始改善了和 TypeScript 的集成应用
2. TypeScript 2.5+，理由同上

## 配置解析

```javascript
/* 
 * 配置文件用到的外部工具
 */
const fs = require('fs')
const glob = require('glob')
const path = require('path')
const webpack = require('webpack')
const ExtractTextPlugin = require('extract-text-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin')
const OptimizeCSSPlugin = require('optimize-css-assets-webpack-plugin')

/*
 * 配置选项，对应 vue-cli webpack 工程的 config 目录
 * 1. common 是开发和生产环境公用配置
 * 2. build 是生产配置，dev 是开发配置，当重名时，build 和 dev 覆盖 common 配置
 * 3. extraPlugins 针对生产和开发环境配置单独启用的 webpack 插件
 * 4. outputFilename 针对生产和开发环境配置输出文件命名规则
 * 5. get 工具函数针对 NODE_ENV 环境变量从 build 或者 dev 中查询配置，
 *    如果找不到，则从 common 中查询配置
 * 6. 与 vue-cli webpack 工程不同，这里不使用 *.env.js 配置环境变量，
 *    而是在 module.exports 中通过命令行环境变量或命令行选项设置环境变量，
 *    因此把配置写成一个函数确保拿到正确的环境变量 process.env.VAR
 */
function makeBuildConfigs (options) {
  return {
    // build or dev settings take priority over common settings
    // see the "get" method for details
    common: {
      assetsRoot: path.resolve(__dirname, './frontend/dist'),
      assetsSubDirectory: 'static',
      assetsPublicPath: '/'
    },
    build: {
      cssMinimize: true,
      cssSourceMap: true,
      cssExtract: true,
      // 生产环境启用对调试工具友好的 #source-map，设置为 false 禁用 source-map
      devtool: '#source-map',
      // Gzip off by default as many popular static hosts already gzip
      // all static assets for you. Before setting to true, make sure to:
      // `npm install --save-dev compression-webpack-plugin`
      productionGzip: false,
      productionGzipExtensions: ['js', 'css'],
      // 生产环境单独启用的插件
      extraPlugins: [
        // 压缩JS文件
        new webpack.optimize.UglifyJsPlugin({
          compress: {warnings: false},
          sourceMap: true
        }),
        // 合并压缩提取出的CSS文件
        new OptimizeCSSPlugin({cssProcessorOptions: {safe: true}})
      ],
      outputFilename: (ext) => ext === 'ext'
        ? `[name].[chunkhash:8].[ext]` : `[name].[chunkhash:8].${ext}`
    },
    dev: {
      cssMinimize: false,
      cssSourceMap: false,
      cssExtract: true,
      // 开发环境使用常规的 #cheap-modulel-eval-source-map，编译速度较快
      devtool: '#cheap-module-eval-source-map',
      // 使用环境变量指定的开发服务端口，默认 8080
      port: process.env.PORT || 8080,
      // 如果有需要，可以配置后端API代理
      // https://webpack.github.io/docs/webpack-dev-server.html#proxy
      proxy: {},
      // 开发环境单独启用的插件
      extraPlugins: [
        // 自动重载开发页面
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoEmitOnErrorsPlugin(),
        new FriendlyErrorsPlugin()
      ],
      // 开发环境编译输出文件不加 hash
      outputFilename: (ext) => ext === 'ext' ? `[name].[ext]` : `[name].${ext}`
    },
    // _path: 如果配置有嵌套，使用以 "." 分割的对象路径
    get: function (_path, options = {}) {
      let config = process.env.NODE_ENV === 'production' ? this.build : this.dev
      let properties = _path.split('.')
      let search = (root) => {
        let value = null
        for (let idx in properties) {
          let parent = value || root
          if (!parent.hasOwnProperty(properties[idx])) {
            break
          } else {
            value = parent[properties[idx]]
          }
        }
        return value
      }
      let value = search(config)
      if (value === null) value = search(this.common)
      return value
    }
  }
}

/*
 * 从 vue-cli webpack 工程中抄来的 style loaders 配置
 */
function cssLoaders (options) {
  options = options || {}

  let cssLoader = {
    loader: 'css-loader',
    options: {
      minimize: options.minimize,
      sourceMap: options.sourceMap
    }
  }

  // generate loader string to be used with extract text plugin
  function generateLoaders (loader, loaderOptions) {
    let loaders = [cssLoader]
    if (loader) {
      loaders.push({
        loader: loader + '-loader',
        options: Object.assign({}, loaderOptions, {
          sourceMap: options.sourceMap
        })
      })
    }

    // Extract CSS when that option is specified
    // (which is the case during production build)
    if (options.extract) {
      return ExtractTextPlugin.extract({
        use: loaders,
        fallback: 'vue-style-loader'
      })
    } else {
      return ['vue-style-loader'].concat(loaders)
    }
  }

  // http://vuejs.github.io/vue-loader/configurations/extract-css.html
  return {
    css: generateLoaders(),
    postcss: generateLoaders(),
    less: generateLoaders('less'),
    sass: generateLoaders('sass', {indentedSyntax: true}),
    scss: generateLoaders('scss'),
    stylus: generateLoaders('stylus'),
    styl: generateLoaders('stylus')
  }
}

// Generate loaders for standalone style files (outside of .vue)
function styleLoaders (options) {
  let output = []
  let loaders = cssLoaders(options)
  for (let extension in loaders) {
    let loader = loaders[extension]
    output.push({
      test: new RegExp('\\.' + extension + '$'),
      use: loader
    })
  }
  return output
}

/*
 * 获取页面列表
 * 1. 根据指定 PAGE 过滤列表，如果有指定则输出指定页面，否则输出全部页面，
 *    src/pages 目录下的根页面，使用文件 basename 过滤，子目录页面使用子目录名称过滤；
 * 2. 返回不包含 "frontend/src/pages/" 和文件后缀的页面列表；
 */

function getPageEntries (globPath) {
  let targetPage = process.env.PAGE
  let entries = {}, paths, basename, pathname, pageIndex
  glob.sync(globPath).forEach(entry => {
    basename = path.basename(entry, path.extname(entry))
    // node-glob uses forward-slashes only in glob expressions, even on windows
    paths = entry.split('/')
    pageIndex = paths.indexOf('pages') + 1
    if (targetPage) {  // partially build
      if (paths.length === pageIndex + 1) {  // root pages
        if (basename !== targetPage) {
          return
        }
      } else if (paths[pageIndex] !== targetPage) {
        return
      }
    }
    pathname = paths.slice(pageIndex, -1).concat([basename]).join('/')
    entries[pathname] = entry
  })
  return entries
}

// 解析前端文件路径，类似 vue-cli webpack 工程中 resolve 函数。
// 若未传入 target 参数，返回 frontend 目录路径
function resolveFrontend (target) {
  return path.join(__dirname, 'frontend', target || '')
}

// 检查是否 node_modules 模块
function isNodeModule (module) {
  return (
    module.resource &&
    /\.js$/.test(module.resource) &&
    module.resource.indexOf(
      path.join(__dirname, 'node_modules')
    ) === 0
  )
}

/*
 * Webpack 导出配置，通过使用导出函数，环境变量可以通过命令行参数传入:
 * https://webpack.js.org/api/cli/#environment-options
 */

module.exports = (options = {}) => {
  // 该配置文件不使用 *.env.js 文件，环境变量使用命令行环境变量或命令行选项传入，
  // Windows 平台不支持 "VAR=value command" 这样的调用方式，
  // 网上多见到使用 cross_env 解决这个问题的，个人以为使用命令行选项更简单优雅
  // --env.production
  if (typeof options.production === 'boolean' && options.production) {
    process.env.NODE_ENV = 'production'
  } else {
    process.env.NODE_ENV = 'development'
  }
  if (options.port) process.env.PORT = options.port  // --env.port=PORT
  if (options.page) process.env.PAGE = options.page  // --env.page=PAGE

  // 环境变量配置完成，生成配置选项
  const buildConfigs = makeBuildConfigs(options)
  // 针对配置选项的工具函数
  const getConfig = (_path) => buildConfigs.get(_path, options)
  const assetsPath = (_path) => path.posix.join(getConfig('assetsSubDirectory'), _path)
  const outputFilename = (ext) => getConfig('outputFilename')(ext)

  // 导出内容
  let exports = {
    context: path.resolve(__dirname),
    // 获取 frontend/src/pages/ 目录下的所有 .js, .ts 入口文件列表
    entry: getPageEntries(resolveFrontend('src/pages/**/*.[jt]s')),
    output: {
      path: getConfig('assetsRoot'),
      // 输出到 $assetsPath/js/ 目录，使用配置选项中的 outputFilename 计算输出文件名
      filename: assetsPath(`js/${outputFilename('js')}`),
      publicPath: getConfig('assetsPublicPath')
    },

    resolve: {
      modules: [resolveFrontend('src'), 'node_modules'],
      // 解析所有 js/typescript/vue/json/css/scss/less 文件
      extensions: ['.js', '.ts', '.vue', '.json', '.css', '.scss', '.less'],
      // 引用别名，方便代码里引入，如："import Hello from '@/components/Hello'"
      alias: {
        'vue$': 'vue/dist/vue.esm.js',
        '@': resolveFrontend('src'),
        'assets': resolveFrontend('src/assets'),
        'components': resolveFrontend('src/components'),
        'plugins': resolveFrontend('src/plugins'),
        'utils': resolveFrontend('src/utils')
      }
    },

    module: {
      rules: [
        {  // eslint
          test: /\.(js|vue)$/,
          loader: 'eslint-loader',
          enforce: 'pre',
          include: [resolveFrontend('src'), resolveFrontend('test')],
          exclude: /node_modules/,
          options: {
            formatter: require('eslint-friendly-formatter')
          }
        },
        {
          test: /\.vue$/,
          loader: 'vue-loader',
          options: {
            loaders: cssLoaders({
              minimize: getConfig('cssMinimize') || false,
              sourceMap: getConfig('cssSourceMap') || false,
              extract: getConfig('cssExtract') || false
            }),
            // 在模版编译过程中，编译器可以将某些属性，如 src 路径，转换为 require 调用，
            // 以便目标资源可以由 Webpack 处理。
            // 转为 require 调用可以增加构建的灵活性，并减少开发环境和生产环境路径配置不一致可能导致的问题
            transformToRequire: {
              video: 'src',
              source: 'src',
              img: 'src',
              image: 'xlink:href'
            }
          }
        },
        {
          // typescript
          // 注意：如果在 Vue 单文件组件中使用 typescript，entry 文件必须以 .ts 作为后缀
          test: /\.tsx?$/,
          loader: 'ts-loader',
          include: [resolveFrontend('src'), resolveFrontend('test')],
          options: {
            appendTsSuffixTo: [/\.vue$/],
            // set to false to get benefits from static type checking
            // https://www.npmjs.com/package/ts-loader#transpileonly-boolean-defaultfalse
            transpileOnly: true
          }
        },
        {
          test: /\.js$/,
          loader: 'babel-loader',
          include: [resolveFrontend('src'), resolveFrontend('test')],
          exclude: /node_modules/
        },
        {
          test: /\.json$/,
          loader: 'json-loader'
        },
        {
          test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
          loader: 'url-loader',
          options: {
            limit: 10000,
            name: assetsPath(`img/${outputFilename('ext')}`)
            // a lot of other options can be customized
          }
        },
        {
          test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
          loader: 'url-loader',
          options: {
            limit: 10000,
            name: assetsPath(`fonts/${outputFilename('ext')}`)
          }
        }
      ].concat(styleLoaders({
        minimize: getConfig('cssMinimize') || false,
        sourceMap: getConfig('cssSourceMap') || false,
        extract: getConfig('cssExtract') || false
      }))
    },

    // 可选在 HTML 文件中从CDN引入JS库，可以加入 externals 列表减小打包体积
    externals: {},

    // dev 和 build 通用的 webpack 插件
    plugins: [
      // 提取每个页面的样式表到独立的CSS文件
      new ExtractTextPlugin({
        filename: assetsPath(`css/${outputFilename('css')}`)
      }),
      // any required modules inside node_modules are extracted to vendor
      new webpack.optimize.CommonsChunkPlugin({
        name: 'vendor',
        minChunks: function (module, count) {
          return isNodeModule(module)
        }
      }),
      // extract webpack runtime and module manifest to its own file in order to
      // prevent vendor hash from being updated whenever app bundle is updated
      new webpack.optimize.CommonsChunkPlugin({
        name: 'manifest',
        chunks: ['vendor']
      }),
      // 从 frontend/static/ 目录复制文件到构建目录
      new CopyWebpackPlugin([
        {
          from: resolveFrontend('static'),
          to: getConfig('assetsSubDirectory'),
          ignore: ['.*', 'README.*']
        }
      ])
    ].concat(getConfig('extraPlugins') || []),

    devtool: getConfig('devtool') || '#cheap-module-eval-source-map',

    // development server
    devServer: {
      contentBase: resolveFrontend('dist'),
      compress: true,
      historyApiFallback: true,
      hot: true,
      port: buildConfigs.dev.port,
      proxy: buildConfigs.dev.proxy
    }
  }

  /*
   * 为每个 index/main entry 配置 HtmlWebpackPlugin
   * 1. entry 文件使用 index.js, index.ts, main.js, main.ts 为文件名
   * 2. 输出总是以 index.html 作为文件名，保持和源文件对应的目录结构，例如：
   *    src/pages/index.ts => dist/index.html
   *    src/pages/main.js => dist/index.html
   *    src/pages/demoapp/index.js => dist/demoapp/index.html
   * 3. 如果存在，则使用与 entry 文件对应的同名HTML模板文件，否则使用 src/pages/index.html
   */
  for (let pathname in getPageEntries(resolveFrontend('src/pages/**/@(index|main).[jt]s'))) {
    let conf = {
      filename: ((pn) => {
        // always use index.html as output filename for main or index entry
        if (pn === 'main') return 'index.html'
        if (pn.endsWith('/main')) return `${pn.slice(0, -5)}/index.html`
        return pn + '.html'
      })(pathname),
      template: ((pn) => {
        // use root index.html as template if page html not exists
        let htmlPath = resolveFrontend(`src/pages/${pn}.html`)
        if (fs.existsSync(htmlPath)) {
          return htmlPath
        }
        return resolveFrontend('src/pages/index.html')
      })(pathname),
      chunks: [pathname, 'vendor', 'manifest'],
      inject: true,   // inject js file
      minify: {       // minify the html file
        removeComments: true,
        collapseWhitespace: true,
        removeAttributeQuotes: true,
        // necessary to consistently work with multiple chunks via CommonsChunkPlugin
        chunksSortMode: 'dependency'
        // more options:
        // https://github.com/kangax/html-minifier#options-quick-reference
      }
    }
    exports.plugins.push(new HtmlWebpackPlugin(conf))
  }

  /*
   * 为独立HTML页面配置 HtmlWebpackPlugin
   * 1. HTML文件不以 index.html, main.html 为文件名
   * 2. 如果存在同名的 js/ts 文件，则注入HTML文件，无则省略
   */
  for (let pathname in getPageEntries(resolveFrontend('src/pages/**/!(index|main).html'))) {
    let conf = {
      filename: pathname + '.html',
      template: resolveFrontend(`src/pages/${pathname}.html`),
      chunks: [pathname, 'vendor', 'manifest'],
      inject: true,
      minify: {
        removeComments: true,
        collapseWhitespace: true,
        removeAttributeQuotes: true,
        chunksSortMode: 'dependency'
      }
    }
    exports.plugins.push(new HtmlWebpackPlugin(conf))
  }

  // 可选项，大部分生产环境的 Web server 都提供了 gzip 压缩的功能，
  // 通常不会在编译阶段执行 gzip 压缩
  if (getConfig('productionGzip')) {
    let extensions = getConfig('productionGzipExtensions')
    if (extensions && extensions.length > 0) {
      const CompressionWebpackPlugin = require('compression-webpack-plugin')
      let conf = {
        asset: '[path].gz[query]',
        algorithm: 'gzip',
        test: new RegExp(`\\.(${extensions.join('|')})$`),
        threshold: 10240,
        minRatio: 0.8
      }
      exports.plugins.push(new CompressionWebpackPlugin(conf))
    }
  }

  /*
   * 如果在命令行指定 --env.report 参数，则在构建结束后查看打包分析报告：
   * `npm run build -- --env.report`
   */
  if (options.report) {
    const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
    exports.plugins.push(new BundleAnalyzerPlugin())
  }

  return exports
}
```

### 配合使用的 package.json

```jsom
{
  "name": "project_name",
  "version": "0.0.1",
  "description": "The Awesome Project",
  "author": "",
  "private": true,
  "scripts": {
    "apidoc": "apidoc -o staticfiles/apidoc -f \".*\\\\.py\"",
    "clean": "rm -rf ./frontend/dist/*",
    "dev": "webpack-dev-server -d",
    "watch": "webpack -d -w",
    "build": "npm run clean && webpack -p --progress --env.production"
  },
  "dependencies": {
    "axios": "^0.16.2",
    "lodash": "^4.17.4",
    "moment": "^2.19.0",
    "vue": "^2.5.2",
    "vue-router": "^3.0.1"
  },
  "devDependencies": {
    "apidoc": "^0.17.6",
    "autoprefixer": "^7.1.5",
    "babel-core": "^6.26.0",
    "babel-eslint": "^8.0.1",
    "babel-loader": "^7.1.2",
    "babel-plugin-transform-runtime": "^6.22.0",
    "babel-preset-env": "^1.3.2",
    "babel-preset-stage-2": "^6.22.0",
    "babel-register": "^6.22.0",
    "chalk": "^2.1.0",
    "connect-history-api-fallback": "^1.3.0",
    "copy-webpack-plugin": "^4.0.1",
    "css-loader": "^0.28.0",
    "eslint": "^4.8.0",
    "eslint-config-standard": "^10.2.1",
    "eslint-friendly-formatter": "^3.0.0",
    "eslint-loader": "^1.7.1",
    "eslint-plugin-html": "^3.0.0",
    "eslint-plugin-import": "^2.7.0",
    "eslint-plugin-node": "^5.2.0",
    "eslint-plugin-promise": "^3.4.0",
    "eslint-plugin-standard": "^3.0.1",
    "eventsource-polyfill": "^0.9.6",
    "express": "^4.16.2",
    "extract-text-webpack-plugin": "^3.0.1",
    "file-loader": "^1.1.5",
    "friendly-errors-webpack-plugin": "^1.6.1",
    "html-webpack-plugin": "^2.30.1",
    "http-proxy-middleware": "^0.17.4",
    "opn": "^5.1.0",
    "optimize-css-assets-webpack-plugin": "^3.2.0",
    "ora": "^1.2.0",
    "rimraf": "^2.6.0",
    "semver": "^5.3.0",
    "shelljs": "^0.7.6",
    "ts-loader": "^3.0.5",
    "typescript": "^2.5.3",
    "url-loader": "^0.6.2",
    "vue-loader": "^13.3.0",
    "vue-style-loader": "^3.0.3",
    "vue-template-compiler": "^2.5.2",
    "webpack": "^3.6.0",
    "webpack-bundle-analyzer": "^2.9.0",
    "webpack-dev-middleware": "^1.12.0",
    "webpack-dev-server": "^2.9.1",
    "webpack-hot-middleware": "^2.19.1",
    "webpack-merge": "^4.1.0"
  },
  "engines": {
    "node": ">= 4.0.0",
    "npm": ">= 3.0.0"
  },
  "browserslist": [
    "> 1%",
    "last 2 versions",
    "not ie <= 8"
  ],
  "apidoc": {
    "title": "The API Documentation",
    "url": "http://project.example.com/api",
    "sampleUrl": "http://localhost:8080/api"
  }
}
```