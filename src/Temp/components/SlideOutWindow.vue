// 滑出窗口组件，用于显示可滑出的内容，支持动画和交互
<template>
  <div class="slideout-window" 
    :class="{ 'slideout-window-open': isOpen }"
    :style="{left:windowLeft}"
  >   
    <div v-if="isOpen" class="slideout-content">
      <button class="close-button" @click="$emit('toggle-window')">&times;</button>
      <div class="window-header">
        <h3>岩石查找</h3>
      </div>
      <div class="search-container">
        <div class="search-input-wrapper">
          <input 
            type="text" 
            placeholder="输入岩石名称..." 
            v-model="searchQuery"
            class="search-input"
          />
          <button class="search-button" @click="searchRocks">
            <span class="search-icon">🔍</span>
            <span class="search-text">搜索</span>
          </button>
        </div>
      </div>
      <div class="results-container">
        <div v-for="rock in filteredRocks" :key="rock.id" class="rock-item">
          <div class="rock-content">
            <span class="rock-name">{{ rock.name }}</span>
            <span class="rock-id">#{{ rock.id }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { watch } from 'vue';
export default {
  name: 'SlideOutWindow',
  props: {
    isOpen: {
      type: Boolean,
      default: false,
      required: true
    },
    sidebarCollapsed: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      searchQuery: '',
      rocks: [
        { id: 1, name: '花岗岩' },
        { id: 2, name: '玄武岩' },
        { id: 3, name: '砂岩' },
      ]
    };
  },
  computed: {
    filteredRocks() {
      if (!this.searchQuery) return this.rocks;
      return this.rocks.filter(rock =>
        rock.name.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
    windowLeft() {
      const val = this.sidebarCollapsed ? '60px' : '153px';
      return val;
    }
  },
  methods: {
    searchRocks() {
      console.log('搜索:', this.searchQuery);
    }
  },
  watch: {
    sidebarCollapsed(val) {
      console.log('sidebarCollapsed 变化了：', val);
    }
  }
}
</script>

<style scoped>
.slideout-window {
  position: fixed;
  top: 0;
  z-index: 1000;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  height: 100%;
  display: flex;
  align-items: flex-start;
  width: 400px;
}

.slideout-content {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.95));
  backdrop-filter: blur(10px);
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.1);
  border-radius: 0 20px 20px 0;
  padding: 20px;
  overflow-y: auto;
  border-right: 1px solid rgba(74, 144, 226, 0.1);
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: rgba(74, 144, 226, 0.1);
  color: #4a90e2;
  transform: rotate(90deg) scale(1.1);
}

.window-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(74, 144, 226, 0.1);
}

.window-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.search-container {
  margin: 20px 0;
}

.search-input-wrapper {
  display: flex;
  gap: 10px;
  position: relative;
}

.search-input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid rgba(74, 144, 226, 0.2);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(5px);
}

.search-input:focus {
  outline: none;
  border-color: rgba(74, 144, 226, 0.4);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 1);
}

.search-button {
  padding: 0 20px;
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.9), rgba(53, 122, 189, 0.9));
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.2);
  backdrop-filter: blur(5px);
}

.search-button:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
  background: linear-gradient(135deg, rgba(74, 144, 226, 1), rgba(53, 122, 189, 1));
}

.search-button:active {
  transform: translateY(0) scale(0.98);
}

.search-icon {
  font-size: 16px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

.search-text {
  font-size: 14px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.results-container {
  margin-top: 20px;
}

.rock-item {
  padding: 12px 15px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  margin-bottom: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: 1px solid rgba(74, 144, 226, 0.1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(5px);
}

.rock-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.1), rgba(74, 144, 226, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.rock-item:hover::before {
  opacity: 1;
}

.rock-item:hover {
  transform: translateX(5px) scale(1.02);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.15);
  background: rgba(255, 255, 255, 1);
  border-color: rgba(74, 144, 226, 0.2);
}

.rock-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.rock-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.rock-id {
  font-size: 12px;
  color: #666;
  background: rgba(74, 144, 226, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.rock-item:hover .rock-id {
  background: rgba(74, 144, 226, 0.2);
  color: #4a90e2;
}

/* 更新动画效果 */
@keyframes slideIn {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.slideout-window-open {
  animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>