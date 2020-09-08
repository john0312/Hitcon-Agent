<template>
    <v-card>
        <v-tabs
            background-color="deep-purple accent-4"
            centered
            dark
            icons-and-text
        >
            <v-tabs-slider></v-tabs-slider>
            <v-tab v-for="tab of tabs" :key="tab.id" :href="tab.href" @click="tabClickEvent(tab.id, tab.name)">
             {{tab.name}}
            </v-tab>
        </v-tabs>
        <v-tabs-items>
            <v-tab-item v-for="tabItem of tabItems" :key="tabItem.id" :value="tabItem.value">
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
    ...mapActions(['setCurrentTabIndex', 'setCurrentName']),
    tabClickEvent(index, name) {
      this.setCurrentTabIndex(index)
      this.setCurrentName(name)
    },
  },
  data() {
    return {
      tabs: [],
      tabItems: [],
    }
  },
  mounted() {
    this.tabs = []
    this.tabItems = []
    this.nameList.forEach((item, index) => {
      this.tabs.push({id: index, name: item, href: `#${item}`})
      this.tabItems.push({id: index, value: `#${item}`})
    })
    console.log(this.tabs.length)
    if (this.tabs.length > 0) {
      this.setCurrentTabIndex(this.tabs[0].id)
      this.setCurrentName(this.tabs[0].name)
    }
  },
  components: {
    ScoreList,
  },
}
</script>
