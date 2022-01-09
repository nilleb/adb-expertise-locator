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
      <p v-html="result.highlight"></p>
      <span v-for="keyword in result.source.keywords" :key="keyword.keyword">
        {{ keyword.keyword }} ({{ keyword.count }}),
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
  name: "DefaultSearchResult",
  props: {
    result: Object,
  },
  data: function () {
    return {
      isVisible: false,
    };
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
</style>
