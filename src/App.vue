<template>
  <div id="app">
    <SideBar @sidebar-collapse="handleSidebarToggle" />
    <cesium-viewer ref="cesiumViewer" @click-blank="handleClickBlank" @viewer-ready="handleViewerReady"/>
    <GeoJsonLoader v-if="viewer" :viewer="viewer" @feature-selected="handleFeatureSelected" />
    <info-move-loader v-if="viewer" :viewer="viewer" />
    
    <div class="drawer-container" :class="{ 'drawer-container-open': drawerOpen }">
      <!-- 控制抽屉的按钮 -->
      <button class="drawer-toggle-button" @click="toggleDrawer">
        {{ drawerOpen ? '关闭抽屉' : '打开抽屉' }}
      </button>
      <!-- 抽屉 -->
      <RightDrawer :isOpen="drawerOpen" :selectedFeature="selectedFeature" />
    </div>

    <!-- 左侧岩石查找窗口 - 只有 rockSearchInitialized 为 true 时才渲染 -->
    <SlideOutWindow 
      v-if="rockSearchInitialized"
      :isOpen="rockSearchOpen" 
      :sidebarCollapsed="sidebarCollapsed"
      @toggle-window="toggleRockSearch"/>

      <feature-click-info />

    <HelpButton 
      :isOpen="helpModalOpen"
      :type="helpModalType"
      @close="closeHelpModal"
    />
    <RightDrawer_lutou />
    <AI />
    <EnvironmentalSetup 
      v-if="viewer"
      :isOpen="environmentalSetupOpen"
      :viewer="viewer"
    />
  </div>
</template>

<script>
import CesiumViewer from './components/CesiumViewer.vue';
import SideBar from './components/SideBar.vue';
import RightDrawer from './components/RightDrawer.vue';
import GeoJsonLoader from './components/GeoJsonLoader.vue';
import emitter from './eventBus';
import SlideOutWindow from './components/SlideOutWindow.vue';
import FeatureClickInfo from './components/FeatureClickInfo.vue';
import HelpButton from './components/HelpButton.vue';
import InfoMoveLoader from './components/InfoMoveLoader.vue';
import RightDrawer_lutou from './components/RightDrawer_lutou.vue';
import AI from './components/AI.vue';
import EnvironmentalSetup from './components/Environmental_setup.vue';

export default {
  name: 'App',
  components: {
    CesiumViewer,
    SideBar,
    RightDrawer,
    GeoJsonLoader,
    SlideOutWindow,
    FeatureClickInfo,
    HelpButton,
    InfoMoveLoader,
    RightDrawer_lutou,
    AI,
    EnvironmentalSetup
  },
  data() {
    return {
      viewer: null,
      drawerOpen: false,
      selectedFeature: null,
      rockSearchInitialized: false,
      rockSearchOpen: false,
      sidebarCollapsed: true,
      helpModalOpen: false,
      helpModalType: 'settings',
      environmentalSetupOpen: false
    };
  },
  methods: {
    handleFeatureSelected(feature) {
      // 更新右侧抽屉的内容
      this.selectedFeature = feature;
      this.drawerOpen = true; // 打开抽屉
    },
    handleClickBlank() {
      if (this.drawerOpen) {
        this.drawerOpen = false; // 点击空白处时关闭抽屉
      }
      if (this.rockSearchOpen) {
        this.rockSearchOpen = false;
      }
      if (this.helpModalOpen) {
        this.helpModalOpen = false;
      }
    },
    toggleDrawer() {
      this.drawerOpen = !this.drawerOpen; // 切换抽屉状态
    },
    handleViewerReady(viewer) {
      console.log('viewer-ready 事件触发，viewer:', viewer); // 调试信息
      this.viewer = viewer; // 将 viewer 存储到 App.vue 的 data 中
  },
   // 切换岩石搜索窗口
   toggleRockSearch() {
      if (!this.rockSearchInitialized) {
        this.rockSearchInitialized = true;
      }
      this.rockSearchOpen = !this.rockSearchOpen;
    },
    handleSidebarToggle(collapsed){
    this.sidebarCollapsed=collapsed;
    console.log('Sidebar 切换状态：', collapsed);
  },
    closeHelpModal() {
      this.helpModalOpen = false;
    }
  },
  mounted() {
    emitter.on('feature-selected', this.handleFeatureSelected);
    emitter.on('toggle-rock-search', this.toggleRockSearch);
    emitter.on('show-settings', () => {
      this.helpModalType = 'settings';
      this.helpModalOpen = true;
    });
    emitter.on('show-help', () => {
      this.helpModalType = 'help';
      this.helpModalOpen = true;
    });
    emitter.on('toggle-environmental-setup', () => {
      this.environmentalSetupOpen = !this.environmentalSetupOpen;
    });
    emitter.on('close-environmental-setup', () => {
      this.environmentalSetupOpen = false;
    });
    emitter.on('feature-hover-error', (error) => {
    console.warn('悬浮信息显示错误:', error);
    // 可以在这里添加用户友好的错误提示
})
  },
  beforeDestroy() {
    emitter.off('feature-selected', this.handleFeatureSelected);
    emitter.off('toggle-rock-search', this.toggleRockSearch);
    emitter.off('show-settings');
    emitter.off('show-help');
    emitter.off('toggle-environmental-setup');
    emitter.off('close-environmental-setup');
}
};

</script>

<style>
/* 添加全局样式 */

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

#app {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

/* 确保AI组件可见 */
.ai-component {
  position: relative;
  z-index: 9999;
}

/* 移除调试样式 */
/* .sidebar {
  background: red !important;
}

.menu-button {
  background: blue !important;
} */

.drawer-container {
  position: fixed;
  top: 0;
  right: 0;
  height: 100%;
  z-index: 1000;
}

.drawer-container-open {
  right: 0;
}

.drawer-toggle-button {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  width: 40px;
  height: 80px;
  background: linear-gradient(135deg, #4a90e2, #357abd);
  color: white;
  border: none;
  border-radius: 10px 0 0 10px;
  cursor: pointer;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  writing-mode: vertical-rl;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1001;
}

.drawer-toggle-button:hover {
  background: linear-gradient(135deg, #357abd, #2a5f8f);
  transform: translateY(-50%) scale(1.05);
}

.drawer-toggle-button:active {
  transform: translateY(-50%) scale(0.95);
}

.cesium-controls {
  position: absolute;
  top: 100px; /* 控件位于抽屉顶部下方 */
  left: -200px; /* 控件位于抽屉左侧 */
  display: flex;
  flex-direction: column;
  gap: 10px; /* 控件之间的间隙 */
  width: auto; /* 自动宽度 */
  height: auto; /* 自动高度 */
  background-color: rgba(255, 255, 255, 0.8); /* 背景颜色，方便调试 */
  z-index: 1001; /* 确保控件在抽屉上方 */
}
/* 添加slideout-window的样式，确保它不被其他元素遮挡 */
.slideout-window {
  z-index: 1001; /* 比侧边栏高，比模态框低 */
}

</style>