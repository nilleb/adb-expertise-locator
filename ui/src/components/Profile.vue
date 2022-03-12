<template>
  <div>
    <avatar
      background="lightgray"
      color="black"
      class="topright"
      :name="`${user.firstName} ${user.lastName}`"
    ></avatar>
    <h1>Hey, {{ user.firstName }}!</h1>

    <h2>Your skills</h2>
    <vue-tags-input
      v-model="tag"
      :tags="tags"
      :autocomplete-items="autocompleteItems"
      @tags-changed="update"
      @before-adding-tag="pushTag"
      @before-deleting-tag="removeTag"
      v-debounce="600"
      placeholder="Add a skill name - press enter when complete."
    />
    <h2>What do we know about you?</h2>
    <table>
      <tr>
        <th>fullname</th>
        <td>{{ user.fullname }}</td>
      </tr>
      <tr>
        <th>email</th>
        <td>{{ user.email }}</td>
      </tr>
      <tr>
        <th>phone</th>
        <td>{{ user.telephoneNumber }}</td>
      </tr>
      <tr>
        <th>role</th>
        <td>{{ user.role }}</td>
      </tr>
      <tr>
        <th>dept</th>
        <td>{{ user.organization }}</td>
      </tr>
    </table>
    <h3>Documents you have worked on</h3>
    <span v-for="document in user.documents" :key="document.path">
      <a :href="document.url">{{ document.title }}</a> 💠
    </span>
    <h3>Keywords</h3>
    <span v-for="keyword in user.keywords" :key="keyword.keyword">
      <i>{{ keyword.keyword }}</i> ({{ keyword.count }}),
    </span>
    <h3>Feedback</h3>
    <a :href="'/edit?' + uid">signal an error</a>
  </div>
</template>

<script>
import VueTagsInput from "@sipec/vue3-tags-input";
import KnowledgeService from "../services/KnowledgeService";
import Avatar from "vue3-avatar";

export default {
  components: {
    VueTagsInput,
    Avatar,
  },
  data() {
    return {
      tag: "",
      tags: [],
      autocompleteItems: [],
      uid: "ivo-bellin-salarin",
      user: {
        email: "ivo@nilleb.com",
        firstName: "Ivo",
        lastName: "Bellin Salarin",
      },
    };
  },
  watch: {
    tag: "initItems",
  },
  methods: {
    pushTag(params) {
      console.log(params.addTag);
      console.log(params.tag);
      if (!params.tag.tiClasses.includes(["ti-invalid"])) {
        KnowledgeService.addSkill(this.userEmail, params.tag.text);
      }
      params.addTag();
    },
    removeTag(params) {
      console.log(params.deleteTag);
      console.log(params.tag);
      if (!params.tag.tiClasses.includes(["ti-invalid"])) {
        KnowledgeService.removeSkill(this.userEmail, params.tag.text);
      }
      params.deleteTag();
    },
    update(newTags) {
      this.autocompleteItems = [];
      this.tags = newTags;
      console.log(newTags);
    },
    initItems() {
      if (this.tag.length < 2) return;

      KnowledgeService.autocompleteSkill(this.tag).then((response) => {
        this.autocompleteItems = response.suggestions;
        /* expects: list of items with a .text property */
      });
    },
    getItem(uid) {
      KnowledgeService.getDocument(uid).then((response) => {
        const source = JSON.parse(response.source);
        this.user = source;
        this.user.firstName = source.fullname.split(" ")[0];
        this.user.lastName = source.fullname.split(" ")[-1];
        this.tags = [{ text: "tag1" }, { text: "tag2" }];
      });
    },
  },
  mounted() {
    if (this.$route.query.uid) {
      this.$data.uid = this.$route.query.uid;
    }
    if (this.$data.uid) {
      this.getItem(this.$data.uid);
    }
  },
};
</script>

<style scoped>
.topright {
  float: right;
}
</style>