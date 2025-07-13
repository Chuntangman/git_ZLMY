// 侧边栏组件，用于显示侧边菜单，支持导航和交互
<template>
  <div :class="['sidebar', { collapsed }]">
    <div class="toggle-button" @click="toggleSidebar">
      <i class="arrow" :class="collapsed ? 'arrow-right' : 'arrow-left'"></i>
    </div>
    <div class="menu">
      <button @click="loadGeologicalCorridor" class="menu-button">
        <img src="../image/长廊.png" class="icon" />
        <span v-if="!collapsed" class="button-text">地质长廊</span>
      </button>
      <button @click="toggleRockSearch" class="menu-button">
        <img src="../image/岩石.png" class="icon">
        <span v-if="!collapsed" class="button-text">岩石查找</span>
      </button>
      <button @click="toggleoutcrops" class="menu-button">
        <img src="../image/一般露头.png" class="icon">
        <span v-if="!collapsed" class="button-text">地质露头</span>
      </button>
      <button @click="toggleoutcropSearch" class="menu-button">
        <img src="../image/研究露头.png" class="icon">
        <span v-if="!collapsed" class="button-text">露头查找</span>
      </button>
    </div>
    <div class="bottom-menu">
      <button @click="showSettings" class="bottom-button" title="设置">
        <i class="bottom-icon">⚙️</i>
        <span v-if="!collapsed" class="bottom-text">设置</span>
      </button>
      <button @click="showHelp" class="bottom-button" title="帮助">
        <i class="bottom-icon">❓</i>
        <span v-if="!collapsed" class="bottom-text">帮助</span>
      </button>
    </div>
  </div>
</template>

<script>
import emitter from '@/eventBus';

export default {
  name: 'Sidebar',
  data() {
    return {
      collapsed: true
    }
  },
  methods: {
    toggleSidebar() {
      this.collapsed = !this.collapsed;
      this.$emit('sidebar-collapse', this.collapsed);
    },
    loadGeologicalCorridor() {
      emitter.emit('load-geological-corridor');
      
    },
    toggleRockSearch() {
      emitter.emit('toggle-rock-search');
    },
    showSettings() {
      emitter.emit('show-settings');
    },
    showHelp() {
      emitter.emit('show-help');
    },
    toggleModule(moduleName) {
      // 其他模块逻辑
    }
  }
};
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 240px;
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.95), rgba(53, 122, 189, 0.95));
  backdrop-filter: blur(10px);
  z-index: 50;
  padding: 30px 0;
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.15);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar.collapsed {
  width: 80px;
}

.menu {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 15px;
  gap: 20px;
}

.menu-button {
  width: 90%;
  height: 65px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(5px);
}

.menu-button:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.menu-button:active {
  transform: translateY(0);
}

.icon {
  width: 32px;
  height: 32px;
  margin-right: 15px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.button-text {
  font-size: 15px;
  font-weight: 500;
  color: #2c3e50;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.sidebar.collapsed .menu-button {
  width: 60px;
  height: 60px;
  padding: 0;
  justify-content: center;
  border-radius: 12px;
}

.sidebar.collapsed .icon {
  margin-right: 0;
}

.toggle-button {
  position: absolute;
  top: 50%;
  right: -15px;
  width: 30px;
  height: 30px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.toggle-button:hover {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.arrow {
  border: solid #4a90e2;
  border-width: 0 2px 2px 0;
  display: inline-block;
  padding: 6px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.arrow-left {
  transform: rotate(135deg);
}

.arrow-right {
  transform: rotate(-45deg);
}

/* 更新动画效果 */
@keyframes buttonPulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 255, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
}

.menu-button:focus {
  animation: buttonPulse 1.5s infinite;
}

/* 更新悬停效果 */
.menu-button::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.menu-button:hover::after {
  opacity: 1;
}

.bottom-menu {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  padding: 0 15px;
}

.bottom-button {
  width: 90%;
  height: 50px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(5px);
}

.bottom-button:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.bottom-icon {
  font-size: 20px;
  margin-right: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.bottom-text {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.sidebar.collapsed .bottom-button {
  width: 50px;
  height: 50px;
  padding: 0;
  justify-content: center;
  border-radius: 12px;
}

.sidebar.collapsed .bottom-icon {
  margin-right: 0;
}

/* 添加新的悬停效果 */
.bottom-button::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.bottom-button:hover::after {
  opacity: 1;
}
</style>