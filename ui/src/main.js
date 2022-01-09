import { createApp, h } from "vue";
import SearchPage from './components/SearchPage.vue'
import ResultPreview from './components/ResultPreview.vue'

const NotFoundComponent = { template: "<p>Page not found</p>" };

const routes = {
  "/": SearchPage,
  "/view": ResultPreview,
};

const SimpleRouter = {
  data: () => ({
    currentRoute: window.location.pathname,
  }),

  computed: {
    CurrentComponent() {
      return routes[this.currentRoute] || NotFoundComponent;
    },
  },

  render() {
    return h(this.CurrentComponent);
  },
};

createApp(SimpleRouter).mount("#app");
