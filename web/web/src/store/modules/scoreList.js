/**
 * Copyright (c) 2020 HITCON Agent Contributors
 * See CONTRIBUTORS file for the list of HITCON Agent Contributors

 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:

 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.

 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import api from '../../api'
import * as mutation from '../mutation-types'

const state = {
  scoreList: [],
  loading: false,
}

const getters = {
  scoreList: (state) => state.scoreList,
}

const mutations = {
  [mutation.SET_SCORE_LIST](state, payload) {
    state.scoreList = payload
  },
  [mutation.IS_LOADING_SCORE_LIST](state, payload) {
    state.loading = payload
  },
}

const actions = {
  getScoreList: ({ commit }) => new Promise((resolve, reject) => {
    const onSuccess = (response) => {
      commit(mutation.SET_SCORE_LIST, response.body)
      commit(mutation.IS_LOADING_SCORE_LIST, false)

      resolve(response)
    }

    const onError = (error) => {
      commit(mutation.SET_SCORE_LIST, [])
      commit(mutation.IS_LOADING_SCORE_LIST, false)
      reject(error)
    }

    commit(mutation.IS_LOADING_SCORE_LIST, true)

    api.getScoreList().then(onSuccess).catch(onError)
  }),
}

export default {
  state,
  actions,
  getters,
  mutations,
}
