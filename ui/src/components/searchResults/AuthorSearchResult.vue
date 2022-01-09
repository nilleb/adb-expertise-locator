<template>
  <div>
    <div class="search-result-textual">
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
      <span @click="signalEdit(result.uid)" class="action">✏️</span>
      <span @click="signalDelete(result.uid)" class="action">❌</span>
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
export default {
  name: "AuthorSearchResult",
  props: {
    result: Object,
  },
  data: function () {
    return {
      isVisible: false,
    };
  },
  methods: {
    signalEdit(uid) {
      let what = prompt("What's wrong with this result?", "Something is wrong with this result..")
      console.log(`edit ${uid}: ${what}`);
    },
    signalDelete(uid) {
      console.log(`delete ${uid}`);
    },
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
