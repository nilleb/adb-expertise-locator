<template>
  <div>
    <div style="display: flex">
      <div class="search-result-textual" @keypress="onKeypress">
        <h2 style="display: inline">
          <a
            :href="`view?uid=${result.uid}`"
            class="tiptext"
            @mouseover="isVisible = true"
            @mouseout="isVisible = false"
            @click="signalClick(result.uid)"
            >{{ result.title }}
            <iframe
              v-if="isVisible"
              class="description"
              :src="`view?uid=${result.uid}`"
            ></iframe
          ></a>
        </h2>
        <span v-if="displayActions">({{ result.score }})</span>
        <span
          @click="signalEdit(result.uid)"
          v-if="displayActions"
          class="action"
          >✏️</span
        >
        <span
          @click="signalDelete(result.uid)"
          v-if="displayActions"
          class="action"
          >❌</span
        >
        <span
          @click="signalHide(result.uid)"
          v-if="displayActions"
          class="action"
          >🙈</span
        >
        <span
          @click="signalBoost(result.uid)"
          v-if="displayActions"
          class="action"
          >➕</span
        >
        <p v-if="result.source.role || result.source.organization">
          🎩
          <span v-if="result.source.role">{{ result.source.role }}</span>,
          <span v-if="result.source.organization">{{
            result.source.organization
          }}</span>
        </p>
        <p>
          📞
          <a :href="'tel:' + result.source.telephoneNumber">{{
            result.source.telephoneNumber
          }}</a>
          📧
          <a :href="'mailto:' + result.source.email">{{
            result.source.email
          }}</a>
        </p>
        <p v-html="result.highlight"></p>
        <tags :tags="result.source.tags?.map((kw) => `${kw.text}` + (kw.count ? `(${kw.count})` : '') )" />
        🔑
        <span v-for="keyword in result.source.keywords" :key="keyword.keyword">
          <i>{{ keyword.keyword }}</i> ({{ keyword.count }}),
        </span>
        <br />
        📚
        <span v-for="document in result.source.documents" :key="document.path">
          <a :href="document.url">{{ document.title }}</a
          > 💠
        </span>
        <br />
      </div>
      <div class="search-result-preview">
        <img :src="result.previewImage" height="150" />
      </div>
    </div>
    <p>&nbsp;</p>
  </div>
</template>

<script>
import KnowledgeService from "@/services/KnowledgeService";
import emitter from "@/services/eventbus.js";
import Tags from "@/components/Tags.vue";

export default {
  name: "AuthorSearchResult",
  props: {
    result: Object,
  },
  data: function () {
    return {
      isVisible: false,
      displayActions: false,
    };
  },
  methods: {
    signalEdit(uid) {
      let what = prompt("What's wrong with this result?", "...");
      let query = this.$route.query.q;
      console.log(`edit ${uid}: ${what} ${query}`);
      KnowledgeService.signal("edit", uid, query, what);
    },
    signalDelete(uid) {
      console.log(`delete ${uid}`);
      KnowledgeService.signal("delete", uid);
    },
    signalHide(uid) {
      let query = this.$route.query.q;
      console.log(`hide ${uid} ${query}`);
      KnowledgeService.signal("hide", uid, query);
    },
    signalBoost(uid) {
      let query = this.$route.query.q;
      console.log(`boost ${uid} "${query}"`);
      KnowledgeService.signal("boost", uid, query);
    },
    signalClick(uid) {
      let query = this.$route.query.q;
      console.log(`click ${uid} ${query}`);
      KnowledgeService.signal("click", uid, query);
    },
  },
  mounted() {
    if (localStorage.displayActions === "true") {
      this.$data.displayActions = true;
    }
    const that = this;
    emitter.on("displayActions", (displayActions) => {
      console.log(displayActions);
      that.$data.displayActions = displayActions;
    });
  },
  components: {Tags},
};
</script>

<style scoped>
.tiptext {
  color: #069;
  cursor: pointer;
}
.description {
  position: absolute;
  border: 1px solid #000;
  width: 400px;
  height: 400px;
}
.action {
  cursor: pointer;
}
.search-result-preview {
  margin-left: auto;
}
img {
  border-radius: 50%;
}
</style>
