module.exports ={
  publicPath: process.env.NODE_ENV === 'production' ? '/static' : '/',
  lintOnSave: process.env.NODE_ENV !== 'production',
  transpileDependencies: [
    'vuetify'
  ],
  chainWebpack: (config) => {
    const svgRule = config.module.rule('svg');
    svgRule.uses.clear();
    svgRule
      .use('babel-loader')
      .loader('babel-loader')
      .end()
      .test(/(\?.*)?\.(svg)(\?.*)?$/)
      .use('vue-svg-loader')
      .loader('vue-svg-loader');
  }
}