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

import * as mutation from '../mutation-types'

const state = {
  currentTabIndex: 1,
  currentName: '',
  scoresMap: {},
  nameList: [],
}

const getters = {
  getCurrentTabIndex: (state) => state.currentTabIndex,
  getCurrentName: (state) => state.currentName,
  getNameList: (state) => state.nameList,
  getScoresMap: (state) => state.scoresMap,
}

const mutations = {
  [mutation.SET_CURRENT_GAME_TAB_INDEX](state, index) {
    state.currentTabIndex = index
  },
  [mutation.SET_CURRENT_GAME_NAME](state, name) {
    state.currentName = name
  },
  [mutation.SET_GAME_SCORE_MAP](state, map) {
    state.scoresMap = map
  },
  [mutation.SET_GAME_NAME_LIST](state, list) {
    state.nameList = list
  },
  [mutation.INSERT_GAME_SCORE_MAP](state, gameName, scores) {
    state.scoresMap[gameName] = scores
  },
}

const actions = {
  setCurrentTabIndex: ({commit}, index) => {
    commit(mutation.SET_CURRENT_GAME_TAB_INDEX, index)
  },
  setCurrentName: ({commit}, name) => {
    commit(mutation.SET_CURRENT_GAME_NAME, name)
  },
  setScoresMap: ({commit}, map) => {
    commit(mutation.SET_GAME_SCORE_MAP, map)
  },
  setNameList: ({commit}, list) => {
    commit(mutation.SET_GAME_NAME_LIST, list)
  },
  insertScoresMap: ({commit}, gameName, scores) => {
    commit(mutation.INSERT_GAME_SCORE_MAP, gameName, scores)
  },
}

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations,
}
