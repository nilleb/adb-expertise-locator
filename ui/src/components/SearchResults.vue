<template>
  <div>
    <div class="search-results">
      <ul id="search-results-list">
        <li v-for="item in searchResults" :key="item.uid">
          <div class="search-result-container">
            <component
              :is="getComponent(item.kind)"
              :class="'search-result'"
              :result="item"
            ></component>
          </div>
        </li>
      </ul>
    </div>
    <div class="search-results-list-footer" v-if="searchResults">
      Photos by <a href="https://generated.photos/">Generated Photos</a>
    </div>
  </div>
</template>

<script>
import DefaultSearchResult from './searchResults/DefaultSearchResult.vue';
import AuthorSearchResult from './searchResults/AuthorSearchResult.vue';

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

const debug = false;

export default {
  props: {
    searchResults: Array,
  },
  components: {
      DefaultSearchResult,
      AuthorSearchResult,
  },
  methods: {
      getComponent(kind) {
          const validComponents = ['author'];
          if (debug) {
              return 'DefaultSearchResult';
          }
          if (validComponents.includes(kind)) {
              return `${capitalizeFirstLetter(kind)}SearchResult`;
          }
          return 'DefaultSearchResult';
      },
  }
};
</script>