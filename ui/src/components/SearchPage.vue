<template>
  <div id="searchPage">
    <h1>Portable Search Engine</h1>
    <div>
      <Autocomplete
        :debounce=200
        placeholder="Type anything..."
        @input="getItems"
        :results="suggestions"
        style="width: 80%; margin: 0 auto;"
      ></Autocomplete>
    </div>
    <SearchResults :searchResults="searchResults" />
  </div>
</template>

<script>
import Autocomplete from "vue3-autocomplete";
import "vue3-autocomplete/dist/vue3-autocomplete.css";
import KnowledgeService from "../services/KnowledgeService";
import SearchResults from "./SearchResults.vue";

export default {
  name: "SearchPage",
  components: {
    Autocomplete,
    SearchResults,
  },
  props: {
    msg: String,
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
        console.log(this.searchResults);
      });
    },
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
</style>
