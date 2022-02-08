import context from '@/store/modules/context'
import departmentEditSession from '@/store/modules/department-edit-session'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    context,
    departmentEditSession
  },
  strict: process.env.NODE_ENV !== 'production'
})