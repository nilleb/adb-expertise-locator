<template>
  <div id="searchPage">
    <h1 style="margin-bottom: 40px;">{{ title }} <span @click="enableActions" class="action">🖐</span></h1>
    <div class="container" style="justify-content: center; margin-bottom: 40px">
      <div>
        disclaimer: all the personal data (telephone, email, photos, ...) on
        this page is fake
      </div>
    </div>
    <div class="container" style="margin-bottom: 10px">
      <div style="flex: 1"><!-- empty space --></div>
      <div style="flex: 9">
        <input
          placeholder="Type anything here..."
          type="text"
          class="search-bar"
          v-model.lazy="query"
          v-debounce="400"
        />
      </div>
      <div style="flex: 1"><!-- empty space --></div>
    </div>
    <div class="container" style="justify-content: center; margin-bottom: 20px">
      <span>{{ total }} results found.&nbsp;</span>
      <span v-if="suggestions.length"
        >You could also try: {{ suggestions.join(", ") }}.</span
      >
    </div>
    <div
      class="container"
      style="justify-content: center; margin-top: 5px; margin-bottom: 5px"
    >
      <span>Drill down the search results&nbsp;</span>
    </div>
    <div v-if="facets" class="container">
      <div style="flex: 2" />
      <Multiselect
        style="flex: 3; margin-left: 20px; margin-right: 20px"
        v-model="selected[facet.name]"
        v-for="facet in facets"
        :key="facet.name"
        :placeholder="facet.name"
        mode="multiple"
        :close-on-select="false"
        :options="
          Object.assign(
            {},
            ...facet.buckets.map((b) => ({
              [b.key]: `${b.key} (${b.doc_count})`,
            }))
          )
        "
      />
      <div style="flex: 2" />
    </div>
    <p>&nbsp;</p>
    <SearchResults :searchResults="searchResults" />
  </div>
</template>

<script>
import KnowledgeService from "../services/KnowledgeService";
import SearchResults from "./SearchResults.vue";
import emitter from "@/services/eventbus.js";
import Multiselect from "@vueform/multiselect";

export default {
  name: "SearchPage",
  components: {
    SearchResults,
    Multiselect,
  },
  props: {
    title: { type: String, default: "Portable Search Engine" },
  },
  data() {
    return {
      query: "",
      suggestions: [],
      searchResults: [],
      total: 0,
      facets: [],
      selected: {},
    };
  },
  methods: {
    enableActions() {
      let displayActions = true;
      if (localStorage.displayActions === "true") {
        displayActions = false;
      }
      localStorage.displayActions = displayActions;
      emitter.emit("displayActions", displayActions);
    },
    toFacets(){
      let that = this;
      return Object.keys(that.selected).map(key => ({name: key, values: that.selected[key]}));
    },
    getItems(string) {
      let rf = this.toFacets();
      KnowledgeService.search(string, rf).then((response) => {
        this.suggestions = response.suggestions;
        this.searchResults = response.results;
        this.total = response.total;
        this.facets = response.facets;
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
        // FIXME serialize also the facets
        this.$router
          .push({ name: "Search", query: { q: toBeSearched } })
          .catch(() => {});
      }
      this.getItems(toBeSearched);
    },
    // FIXME watch also the selected facets/buckets
  },
  mounted() {
    if (this.$route.query.q) {
      this.$data.query = this.$route.query.q;
    }
  },
};
</script>

<style src="@vueform/multiselect/themes/default.css"></style>

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
.search-bar {
  width: 100%;
  padding: 2px 7px 2px;
  line-height: 28px;
  font-size: 16px;
}
.action {
  cursor: pointer;
}
</style>