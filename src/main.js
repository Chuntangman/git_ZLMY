// main.js

import { createApp } from 'vue'
import App from './App.vue'
import mitt from 'mitt'
import axios from 'axios'

// Cesium imports
import * as Cesium from 'cesium'

// Import Cesium CSS
import 'cesium/Build/Cesium/Widgets/widgets.css'

import './assets/styles/global.css' // 添加全局样式

// 初始化 Cesium
window.CESIUM_BASE_URL = '/cesium/' // 必须与 public/cesium 目录对应
Cesium.Ion.defaultAccessToken = import.meta.env.VITE_CESIUM_TOKEN

const app = createApp(App)
// 全局注册Cesium
app.config.globalProperties.$Cesium = Cesium
// 全局注册axios
app.config.globalProperties.$axios = axios

// 挂载应用
app.mount('#app')

function handleModelPathChanged(newPath) {
  if (newPath && newPath !== this.modelPath) {
    this.loadModel(newPath);
  }
}

async function loadModel(modelUrl) {
  // ... 使用传入的 modelUrl 而不是固定路径
}