<template>
  <div>
    <div class="search-result-textual">
      <h2><a :href="result.url">[{{ result.uid }}]</a> ({{result.score}}) {{ result.title }}</h2>
      <p v-html="result.highlight"></p>
      <span v-for="label in result.labels" :key="label.label">
        {{ label.label }}
      </span>
      <br />
    </div>
    <div class="search-result-preview">
      <img :src="result.previewImage" />
    </div>
    <pre>
        {{ result }}
    </pre>
  </div>
</template>

<script>
//import VueHighlightJS from "vue-highlight.js";
// import json from "highlight.js/lib/languages/json";
//import "highlight.js/styles/default.css";

// Vue.use(VueHighlightJS, { languages: { json } });

export default {
  name: "DefaultSearchResult",
  props: {
    result: Object,
  },
  components: {
    //VueHighlightJS,
  },
};
</script>
