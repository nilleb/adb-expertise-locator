<template>
  <div id="searchPage">
    <h1>{{ title }}</h1>
    <p>&nbsp;</p>
    <div class="container">
      <div style="flex: 1"><!-- empty space --></div>
      <div style="flex: 8">
        <input
          type="text"
          style="width: 100%"
          v-model.lazy="query"
          v-debounce="400"
        />
      </div>
      <div style="flex: 1"><!-- empty space --></div>
    </div>
    <div class="container">
      <div style="flex: 1"><!-- empty space --></div>
      <div style="flex: 8">
        <span v-if="suggestions.length">You could also try:</span>
        <span v-for="suggestion in suggestions" :key="suggestion"
          >{{ suggestion }},
        </span>
      </div>
      <div style="flex: 1"><!-- empty space --></div>
    </div>
    <p>&nbsp;</p>
    <SearchResults :searchResults="searchResults" />
  </div>
</template>

<script>
import KnowledgeService from "../services/KnowledgeService";
import SearchResults from "./SearchResults.vue";

export default {
  name: "SearchPage",
  components: {
    SearchResults,
  },
  props: {
    title: { type: String, default: "Portable Search Engine" },
  },
  data() {
    return {
      query: "",
      suggestions: [],
      searchResults: [],
    };
  },
  methods: {
    getItems(string) {
      KnowledgeService.search(string).then((response) => {
        this.suggestions = response.suggestions;
        this.searchResults = response.results;
        console.log(response);
      });
    },
  },
  watch: {
    query(string) {
      let toBeSearched = string;
      if (!toBeSearched) {
        if (this.$router.query !== undefined) {
          toBeSearched = this.$router.query.q;
        }
      } else {
        this.$router
          .push({ name: "Search", query: { q: toBeSearched } })
          .catch(() => {});
      }
      this.getItems(toBeSearched);
    },
  },
  mounted() {
    if (this.$route.query.q) {
      this.$data.query = this.$route.query.q;
    }
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1 {
  text-align: center;
}
#searchPage {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
  margin-top: 60px;
}
.demo:deep() .simple-typeahead-list {
  max-height: 200px !important;
}
.container {
  display: flex;
}
</style>