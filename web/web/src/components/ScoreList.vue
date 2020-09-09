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
    <v-card-title>
      <h1>Ranking List</h1>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="scoresMap[currentName]"
      :search="search"
      :rows-per-page-items="[15, 30, 50, 100]"
      :pagination.sync="pagination"
    >
      <template v-slot:items="props">
        <td>{{ props.item.playerName }}</td>
        <td>{{ props.item.pidUptime }}</td>
        <td>{{ props.item.portUptime }}</td>
        <td>{{ props.item.score }}</td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'
const { mapState, mapGetters } = createNamespacedHelpers('game')

export default {
  computed: {
    ...mapState(['currentName', 'scoresMap']),
    ...mapGetters(['getCurrentName', 'getScoresMap']),
  },
  data() {
    return {
      search: '',
      pagination: {
        sortBy: 'score',
        descending: true,
        rowsPerPage: 15,
      },
      headers: [
        {
          text: 'Player Name',
          align: 'left',
          sortable: false,
          value: 'playerName',
        },
        { text: 'Pid Up Time', value: 'pidUptime' },
        { text: 'Port Up Time', value: 'portUptime' },
        { text: 'Score', value: 'score' },
      ],
    }
  },
}
</script>
