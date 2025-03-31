
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { fileURLToPath, URL } from 'node:url'
const pathResolve = (dir) => {
  return resolve(__dirname, ".", dir)
}


/** 
 * @description-en vite document address
 * @description-cn vite官网
 * https://vitejs.cn/config/ */
export default ({ command }) => {
  const prodMock = true;
  return {
    base: './',
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      }
    },
    /* 配置启动端口 */
    server: {
      host: "localhost",
      port: 3888,
      open: true,  // 启动后是否自动打开网页
      // 设置代理
      proxy: {
        '/api': {
          target: 'http://localhost:3008/', // 生产环境下需要根据实际情况修改
          ws: true,        //如果要代理 websockets，配置这个参数
          changeOrigin: true,  //是否跨域
          rewrite: (path) => path.replace(/^\/api/, ""),
        }
      }
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'echarts': ['echarts']
          }
        }
      }
    },
    plugins: [
      vue(),
    ],
    css: {
      postcss: {
        plugins: [
          {
            postcssPlugin: 'internal:charset-removal',
            AtRule: {
              charset: (atRule) => {
                if (atRule.name === 'charset') {
                  atRule.remove();
                }
              }
            }
          }
        ],
      },
    }
  };
}
