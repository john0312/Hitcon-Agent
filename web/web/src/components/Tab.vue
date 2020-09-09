<template>
    <v-card>
        <v-tabs
            background-color="deep-purple accent-4"
            centered
            dark
            icons-and-text
        >
            <v-tabs-slider></v-tabs-slider>
            <v-tab v-for="(name, index) of nameList" :key="index" :href="'/#/'+name" @click="tabClickEvent(name)">
             {{name}}
            </v-tab>
        </v-tabs>
        <v-tabs-items>
            <v-tab-item v-for="(name, index) of nameList" :key="index" :value="'/#/'+name">
                <ScoreList />
            </v-tab-item>
        </v-tabs-items>
    </v-card>
</template>

<script>
import ScoreList from '@/components/ScoreList'
import { createNamespacedHelpers } from 'vuex'
const { mapState, mapGetters, mapActions } = createNamespacedHelpers('game')

export default {
  computed: {
    ...mapState(['nameList']),
    ...mapGetters(['getNameList']),
  },
  methods: {
    ...mapActions(['setCurrentName']),
    tabClickEvent(name) {
      this.setCurrentName(name)
    },
  },
  components: {
    ScoreList,
  },
}
</script>
