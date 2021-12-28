<template>
  <div>
    <div class="top-line">
      <h2>
        <strong class='tooltip'>
          {{ getTypeEmoji(result?.source?.type) }}
          <strong class="tooltiptext">type: {{result?.source?.type || 'unknown'}}&nbsp;</strong>
        </strong>
        <strong class="tooltip">
          {{ getPriorityEmoji(result?.source?.priority) }}
          <strong class="tooltiptext">P{{result?.source?.priority || 'unknown'}}&nbsp;</strong>
        </strong>
        <a :href="result.url">[{{ result.uid }}]</a>
        {{ result.title }}
      </h2>
    </div>
    <div>
      <p v-html="result.highlight"></p>
    </div>
    <div class="bottom-line">
      <p style="width: 120px;">👥 {{ result?.source?.squad }}</p>
      &nbsp;
      <p style="width: 80px;">🔥 {{ result?.source?.transitions_count }}</p>
      <p>🧭 {{ result?.source?.state }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "LinearSearchResult",
  props: {
    result: Object,
  },
  components: {},
  methods: {
    getTypeEmoji(type) {
      switch (type) {
        case "bug":
          return "🐛";
        case "feature":
          return "⛲";
        case "question":
          return "❓";
        default:
          return "🤷";
      }
    },
    getPriorityEmoji(priority) {
      switch (priority) {
        case 1: return '🔴';
        case 2: return '🟠';
        case 3: return '🟡';
        case 4: return '🟢';
        default: return '⚪';
      }
    }
  },
};
</script>

<style scoped>
.tooltip {
  border-bottom: 1px dotted black;
}
.tooltip .tooltiptext {
  display: none;
}
.tooltip:hover .tooltiptext {
  display: inline;
}
.bottom-line {
    display: flex;
}
</style>