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
        error: '#B71C1C',
        'evaluation-row-confirmed': '#EEE',
        'evaluation-row-ignore': '#DDD',
        'evaluation-row-review': '#F2FFF6',
        'evaluation-row-xlisting': '#FFFFDD',
        hovered: '#EEE',
        inactive: '#EEE',
        'inactive-contrast': '#666',
        muted: '#999',
        primary: '#125074',
        'primary-contrast': '#DAF0FD',
        secondary: '#378DC5',
        success: '#00C853',
        tertiary: '#378DC5',
      },
      dark: {
        accent: '#F04A00',
        anchor: '#F04A00',
        background: '#0d202c',
        error: '#D50000',
        'evaluation-row-confirmed': '#2D2D2D',
        'evaluation-row-ignore': '#555',
        'evaluation-row-review': '#0E1D0F',
        'evaluation-row-xlisting': '#2D2901',
        hovered: '#616161',
        inactive: '#AAA',
        'inactive-contrast': '#333',
        muted: '#BDBDBD',
        primary: '#0C354D',
        'primary-contrast': '#94A8B3',
        secondary: '#1C4F72',
        success: '#00953E',
        tertiary: '#80BAE0',
      }
    }
  }
})