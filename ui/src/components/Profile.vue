<template>
  <div>
    <h1>Hey, {{ firstName }}!</h1>

    <h2>Your skills</h2>
    <vue-tags-input
      v-model="tag"
      :tags="tags"
      :autocomplete-items="autocompleteItems"
      @tags-changed="update"
      @before-adding-tag="pushTag"
      @before-deleting-tag="removeTag"
      v-debounce="600"
    />
  </div>
</template>

<script>
import VueTagsInput from "@sipec/vue3-tags-input";
import KnowledgeService from "../services/KnowledgeService";

export default {
  components: {
    VueTagsInput,
  },
  data() {
    return {
      tag: "",
      tags: [],
      autocompleteItems: [],
      userEmail: "ivo@nilleb.com",
      firstName: "Ivo",
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
  },
};
</script>
