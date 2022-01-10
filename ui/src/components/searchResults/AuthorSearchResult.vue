<template>
  <div>
    <div class="search-result-textual" @keypress="onKeypress">
      <h2 style="display: inline">
        <a
          :href="`view?${result.uid}`"
          class="tiptext"
          @mouseover="isVisible = true"
          @mouseout="isVisible = false"
          >{{ result.title }}
          <iframe
            v-if="isVisible"
            class="description"
            :src="`view?uid=${result.uid}`"
          ></iframe
        ></a>
      </h2>
      ({{ result.score }})
      <span @click="signalEdit(result.uid)" v-if="displayActions" class="action"
        >✏️</span
      >
      <span
        @click="signalDelete(result.uid)"
        v-if="displayActions"
        class="action"
        >❌</span
      >
      <span @click="signalHide(result.uid)" v-if="displayActions" class="action"
        >🙈</span
      >
      <span @click="signalBoost(result.uid)" v-if="displayActions" class="action"
        >➕</span
      >
      <p v-html="result.highlight"></p>
      <span v-for="keyword in result.source.keywords" :key="keyword.keyword">
        <i>{{ keyword.keyword }}</i> ({{ keyword.count }}),
      </span>
      <br />
    </div>
    <div class="search-result-preview">
      <img :src="result.previewImage" />
    </div>
    <!--pre>
        {{ result }}
    </pre-->
  </div>
</template>

<script>
import KnowledgeService from '../../services/KnowledgeService';
export default {
  name: "AuthorSearchResult",
  props: {
    result: Object,
  },
  data: function () {
    return {
      isVisible: false,
      displayActions: false,
    };
  },
  methods: {
    signalEdit(uid) {
      let what = prompt("What's wrong with this result?", "...");
      let query = this.$route.query.q;
      console.log(`edit ${uid}: ${what} ${query}`);
      KnowledgeService.signal('edit', uid, query, what);
    },
    signalDelete(uid) {
      console.log(`delete ${uid}`);
      KnowledgeService.signal('delete', uid);
    },
    signalHide(uid) {
      let query = this.$route.query.q;
      console.log(`hide ${uid} ${query}`);
      KnowledgeService.signal('hide', uid, query);
    },
    signalBoost(uid) {
      let query = this.$route.query.q;
      console.log(`boost ${uid} ${query}`);
      KnowledgeService.signal('boost', uid, query);
    },
  },
  mounted() {
    if (localStorage.displayActions === "true") {
      this.$data.displayActions = true;
    }
  },
  components: {},
};
</script>

<style scoped>
.tiptext {
  color: #069;
  cursor: pointer;
}
.description {
  position: absolute;
  border: 1px solid #000;
  width: 400px;
  height: 400px;
}
.action {
  cursor: pointer;
}
</style>
