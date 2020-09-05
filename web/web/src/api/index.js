import Vue from 'vue'
const endpoint = 'http://localhost:5000'

export default {
  getConnectedClients() {
    return Vue.http.get(`${endpoint}/clients`)
  },
}
