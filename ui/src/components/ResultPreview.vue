<template>
  <div id="resultsPreview">
    <h1>Result preview : {{ uid }}</h1>
    <pre><span v-html="content"></span></pre>
  </div>
</template>

<script>
import KnowledgeService from "../services/KnowledgeService";

function syntaxHighlight(json) {
  if (typeof json != "string") {
    json = JSON.stringify(json, undefined, 2);
  }
  json = json
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return json.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g,
    function (match) {
      var cls = "number";
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = "key";
        } else {
          cls = "string";
        }
      } else if (/true|false/.test(match)) {
        cls = "boolean";
      } else if (/null/.test(match)) {
        cls = "null";
      }
      return '<span class="' + cls + '">' + match + "</span>";
    }
  );
}

export default {
  name: "ResultPreview",
  components: {},
  data() {
    return {
      uid: "test",
      content: {},
    };
  },
  methods: {
    getItem(uid) {
      KnowledgeService.getDocument(uid).then((response) => {
        const source = JSON.parse(response.source);
        this.content = syntaxHighlight(JSON.stringify(source, undefined, 2));
      });
    },
  },
  mounted() {
    console.log(this.$route.query);
    if (this.$route.query.uid) {
      this.$data.uid = this.$route.query.uid;
    }
    this.getItem(this.$route.query.uid);
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
#resultsPreview >>> pre {
  /*outline: 1px solid #ccc;*/
  padding: 5px;
  margin: 5px;
}
#resultsPreview >>> .string {
  color: green;
}
#resultsPreview >>> .number {
  color: darkorange;
}
#resultsPreview >>> .boolean {
  color: blue;
}
#resultsPreview >>> .null {
  color: magenta;
}
#resultsPreview >>> .key {
  color: red;
}
</style>