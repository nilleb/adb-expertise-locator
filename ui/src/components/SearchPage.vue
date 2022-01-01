<template>
  <div id="searchPage">
    <h1>Portable Search Engine</h1>
    <div>
      <SimpleTypeahead
					:items="suggestions"
					:placeholder="options.placeholder"
					@selectItem="selectItem"
					@onInput="onInput"
					@onBlur="onBlur"
					:minInputLength="options.minInputLength"
					:itemProjection="
						(item) => {
							return item.title || item;
						}
					"
				/>
      <!--Autocomplete
        :debounce=200
        placeholder="Type anything..."
        @input="getItems"
        :results="suggestions"
        style="width: 80%; margin: 0 auto;"
      ></Autocomplete-->
    </div>
    <SearchResults :searchResults="searchResults" />
  </div>
</template>

<script>
import SimpleTypeahead from 'vue3-simple-typeahead';
import 'vue3-simple-typeahead/dist/vue3-simple-typeahead.css'; //Optional default CSS
import KnowledgeService from "../services/KnowledgeService";
import SearchResults from "./SearchResults.vue";

export default {
  name: "SearchPage",
  components: {
    SimpleTypeahead,
    SearchResults,
  },
  props: {
    msg: String,
  },
  data() {
    return {
			options: {
				placeholder: 'Type anything...',
				minInputLength: 1,
			},
      query: "",
      suggestions: [],
      searchResults: [],
      data: {
				input: '',
				selection: null,
			},
    };
  },
  methods: {
    selectItem(item) {
      console.log(event);
			this.data.selection = item;
		},
		onInput(event) {
			this.data.selection = null;
			this.data.input = event.input;
      this.getItems(event.input);
			this.listFiltered = event.items;
		},
		onBlur(event) {
			this.data.input = event.input;
			this.listFiltered = event.items;
		},
    getItems(string) {
      KnowledgeService.search(string).then((response) => {
        this.suggestions = response.suggestions;
        this.searchResults = response.results;
        console.log(response);
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
.demo:deep() .simple-typeahead-list {
	max-height: 200px !important;
}
</style>