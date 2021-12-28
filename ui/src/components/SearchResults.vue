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
  </div>
</template>

<script>
import DefaultSearchResult from './searchResults/DefaultSearchResult.vue';
import LinearSearchResult from './searchResults/LinearSearchResult.vue';

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
      LinearSearchResult,
  },
  methods: {
      getComponent(kind) {
          const validComponents = ["linear"];
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