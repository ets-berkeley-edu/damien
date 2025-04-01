import viteCompression from 'vite-plugin-compression'
import vue from '@vitejs/plugin-vue'
import vuetify, {transformAssetUrls} from 'vite-plugin-vuetify'
import {defineConfig} from 'vite'
import {fileURLToPath, URL} from 'node:url'
import {type Plugin} from 'vite'
import postcss, {Root} from 'postcss'


function vuetifyRemPlugin(): Plugin {
  return {
    name: 'vite-vuetify-to-rem',
    transform(css: string, id: string) {

      // Only process Vuetify .sass files
      if (!id.startsWith('virtual:plugin-vuetify:components') && !id.includes('.sass')) return

      return postcss([
        (root: Root) => {
          root.walkAtRules('media', rule => {
            if (rule.params.includes('px')) {
              rule.params = convertPxToRem(rule.params)
              rule.walkDecls(decl => {
                decl.value = convertPxToRem(decl.value)
              })
            }
          })
        },
      ])
        .process(css, {from: id})
        .then((result) => {
          return {
            code: result.css,
            // map: result.map, // Optional: if you want to include source maps
          }
        })
    },
  }
}

// Function to convert px to rem
function convertPxToRem(value: string): string {
  return value.replace(/(\d*\.?\d+)px/g, (match, p1) => {
    const remValue = (parseFloat(p1) / 16).toFixed(3) // Convert px to rem
    return `${remValue}rem`
  })
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    viteCompression(),
    vue({
      template: {transformAssetUrls}
    }),
    vuetify({
      styles: {
        configFile: 'src/assets/styles/settings.scss'
      }
    }),
    vuetifyRemPlugin()
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
    extensions: [
      '.js',
      '.json',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue'
    ]
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern'
      }
    }
  },
  server: {
    port: 8080
  }
})
