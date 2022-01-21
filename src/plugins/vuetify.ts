import '@mdi/font/css/materialdesignicons.css'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'

Vue.use(Vuetify)

export default new Vuetify({
  icons: {
    iconfont: 'mdi'
  },
  theme: {
    themes: {
      light: {
        primary: '#125074',
        'primary-lighten': '#DAF0FD',
        secondary: '#378DC5',
        tertiary: '#0F8934',
        'tertiary-lighten': '#F2FFF6',
        accent: '#F04A00',
        error: '#FF1744',
        background: '#fff',
        body: '#212529',
        'body-lighten': '#9e9e9e'
      }
    }
  }
})