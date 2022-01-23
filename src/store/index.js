import { createStore } from 'vuex'
//import { db } from '../firebase';
export default createStore({
  state: {
    subjects: []
  },
  mutations: {
    setSubjects(state, payload) {
      state.subjects = payload
    }
  },
  actions: {
  },
  modules: {
  }
})
