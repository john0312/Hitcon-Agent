<!-- Copyright (c) 2020 HITCON Agent Contributors
See CONTRIBUTORS file for the list of HITCON Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. -->

<template>
  <v-card>
    <v-divider />
    <v-card-text>
      <Tab />
    </v-card-text>
  </v-card>
</template>

<script>
import Tab from '@/components/Tab'
import { createNamespacedHelpers } from 'vuex'
const { mapState, mapGetters, mapActions } = createNamespacedHelpers('game')

export default {
  components: {
    Tab,
  },
  computed: {
    ...mapState(['nameList']),
    ...mapGetters(['getNameList']),
  },
  methods: {
    ...mapActions(['setScoresMap', 'setNameList', 'updateScoresMap', 'setCurrentName']),
  },
  mounted() {
    this.$socket.on('SGl0Y29uMjAyMA==', data => {
      this.setNameList(data.gameList)
      this.setScoresMap(data.scoresMap)
      if (this.nameList.length > 0) {
        this.setCurrentName(this.nameList[0])
      }
    })
    this.$socket.on('scoreList', data => {
      let d = JSON.parse(data)
      if (d.message.reply.error === 'ERROR_NONE') {
        this.updateScoresMap([d.gameName, d.message.scores])
      }
    })
  },
}
</script>
