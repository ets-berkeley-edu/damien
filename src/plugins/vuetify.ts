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
        accent: '#F04A00',
        anchor: '#F04A00',
        background: '#FFF',
        error: '#FF1744',
        muted: '#9E9E9E',
        primary: '#125074',
        'primary-contrast': '#DAF0FD',
        secondary: '#378DC5',
        success: '#00C853',
        tertiary: '#0F8934',
        'tertiary-contrast': '#F2FFF6'
      },
      dark: {
        accent: '#F04A00',
        anchor: '#F04A00',
        background: '#0d202c',
        error: '#FF1744',
        muted: '#BDBDBD',
        primary: '#104361',
        'primary-contrast': '#DAF0FD',
        secondary: '#2E74A3',
        success: '#00C853',
        tertiary: '#0F8934',
        'tertiary-contrast': '#F2FFF6'
      }
    }
  }
})