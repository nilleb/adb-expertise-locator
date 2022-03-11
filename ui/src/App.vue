<template>
  <div id="app">
    <div id="nav" style="float: right;">
      <router-link to="/profile">Profile</router-link> |
      <router-link to="/">Search</router-link>
    </div>
    <router-view />
  </div>
</template>

<script>
export default {
  components: {},
  created() {},
};
</script>

<style scoped>
#app { font-family: Avenir, Helvetica, Arial, sans-serif; }
</style>
