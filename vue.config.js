module.exports ={
  publicPath: process.env.NODE_ENV === 'production' ? '/static' : '/',
  lintOnSave: process.env.NODE_ENV !== 'production',
  transpileDependencies: [
    'vuetify'
  ],
  chainWebpack: (config) => {
    config.module.rules.delete('svg')
  },
  configureWebpack: {
    module: {
      rules: [
        {
          test: /\.svg$/, 
          loader: 'vue-svg-loader', 
        },
      ],
    }      
  }
}