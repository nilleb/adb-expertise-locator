import { createApp } from "vue";
import App from "./App";
import router from "@/router";
import debounce from './directives/debounce';

const app = createApp(App);
app.directive('debounce', (el,binding) => debounce(el,binding));
app.use(router).mount("#app");
