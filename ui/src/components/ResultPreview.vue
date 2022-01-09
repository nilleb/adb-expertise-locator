<template>
  <div id="resultsPreview">
    <h1>Result preview : {{ uid }}</h1>
  </div>
</template>

<script>
import KnowledgeService from "../services/KnowledgeService";

export default {
  name: "ResultPreview",
  components: {
  },
  data() {
    return {
      uid: "test",
      content: {}
    };
  },
  methods: {
    getItem(uid) {
      KnowledgeService.retrieve(uid).then((response) => {
        this.content = response.result;
        console.log(response);
      });
    },
  },
  mounted() {
    if (this.$route.query.q) {
      this.$refs.typeahead.inputValue = this.$route.query.q;
    }
    this.getItem(this.$route.query.q);
  },
};
</script>

<style scoped>
h1 {
  text-align: center;
}
#resultsPreview {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
  margin-top: 60px;
}
</style>