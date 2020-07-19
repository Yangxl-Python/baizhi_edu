// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

// axios配置
import axios from "axios";

//element-ui
import Element from "element-ui"
import 'element-ui/lib/theme-chalk/index.css'

import settings from "./settings";

import '../static/css/global.css'

import '../static/js/gt'

require('video.js/dist/video-js.css');
require('vue-video-player/src/custom-theme.css');
import VideoPlayer from 'vue-video-player'

import store from "./store/index";

Vue.use(VideoPlayer);

Vue.prototype.$axios = axios;

Vue.use(Element);

Vue.prototype.$settings = settings;

Vue.config.productionTip = false;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
});
