import context from '@/store/modules/context'
import departmentEditSession from '@/store/modules/department-edit-session'
import listManagementSession from '@/store/modules/list-management-session'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    context,
    departmentEditSession,
    listManagementSession
  },
  strict: process.env.NODE_ENV !== 'production'
})