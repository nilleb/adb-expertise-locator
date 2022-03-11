<template>
  <div>
    <ul class="tags">
        <li class=tag v-for="tag in tags" :key=tag>{{tag}}</li>
    </ul>
  </div>
</template>

<script>

export default {
    props: {
        tags: { type: Array, },
    }
}
</script>

<style scoped>
.tags {
  margin: 0px;
  padding: 0px;
  list-style-type: none;
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  line-height: 1em;
}
.tag {
  background-color: #5c6bc0;
  color: #fff;
  border-radius: 2px;
  display: flex;
  padding: 3px 5px;
  margin: 2px;
  font-size: 0.85em;
}
</style>
