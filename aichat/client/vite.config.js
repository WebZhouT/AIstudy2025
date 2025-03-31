import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
/* 全局引入vant组件 */
import AutoImport from 'unplugin-auto-import/vite';
import { VantResolver } from '@vant/auto-import-resolver'
import Components from 'unplugin-vue-components/vite'
import px2rem from 'postcss-px2rem-exclude'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  /* 配置启动端口 */
  server: {
    host: "localhost",
    port: 8080,
    open: true,  // 启动后是否自动打开网页
    // 设置代理
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:3000/', // 生产环境下需要根据实际情况修改
        ws: true,        //如果要代理 websockets，配置这个参数
        changeOrigin: true,  //是否跨域
        rewrite: (path) => path.replace(/^\/api/, ""),
      }
    }
  },
  plugins: [
    vue(),
    AutoImport({
      resolvers: [VantResolver()],
    }),
    Components({
      resolvers: [VantResolver()],
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  base: './'/* 配置项目打包目录 */,
  css: {
    // css预处理器(全局配置公共变量)
    preprocessorOptions: {
      less: {
        charset: false,
      },
    },
    postcss: {
      plugins: [
        px2rem({
          remUnit: 37.5,  // rem基准值
          // exclude: /node_modules/i,  // 排除node_modules目录
          // exclude: /node_modules|vant.*?css/i,  // 排除node_modules目录
          exclude: /(node_modules)/, // 排除 node_modules 和 Vant ES 目录下的 CSS 文件
          mediaQuery: false, //（布尔值）允许在媒体查询中转换px
          minPixelValue: 0,  //设置要替换的最小像素值(3px会被转rem)。 默认 0
          unitPrecision: 2, //允许REM单位增长到的十进制数字，其实就是精度控制
        }),
      ]
    }
  }
})
