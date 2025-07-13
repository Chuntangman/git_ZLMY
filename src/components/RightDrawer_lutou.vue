// 右侧露头抽屉组件，用于显示露头信息，支持动画和交互
<template>
  <div>
    <button v-if="showButton" class="toggle-button" @click="toggleDrawer">Toggle Right Drawer</button>
    <div class="right-drawer" :class="{ 'right-drawer-open': isOpen }">
      <div class="drawer-content">
        <div class="drawer-header">
          <div class="header-content">
            <h3>露头信息</h3>
          </div>
        </div>
        <div class="drawer-body">
          <!-- 主要内容区域 -->
          <div class="info-section">
            <div v-if="loading" class="loading">
              加载中...
            </div>
            <div v-else-if="error" class="error-message">
              {{ error }}
            </div>
            <div v-else-if="!lutouDetails" class="no-data">
              请选择一个要素以查看详细信息
            </div>
            <div v-else class="lutou-details">
              <div class="info-grid">
                <!-- 地理地名 -->
                <div class="info-item">
                  <div class="info-label">地理地名</div>
                  <div class="info-value">{{ lutouDetails.地理地名 }}</div>
                </div>
                
                <!-- 盆地 -->
                <div class="info-item">
                  <div class="info-label">盆地</div>
                  <div class="info-value">{{ lutouDetails.盆地 }}</div>
                </div>
                
                <!-- 所处方位 -->
                <div class="info-item">
                  <div class="info-label">所处方位</div>
                  <div class="info-value">{{ lutouDetails.所处方位 }}</div>
                </div>
                
                <!-- 大地坐标X -->
                <div class="info-item">
                  <div class="info-label">经度</div>
                  <div class="info-value">{{ lutouDetails.大地坐标X }}</div>
                </div>
                
                <!-- 大地坐标Y -->
                <div class="info-item">
                  <div class="info-label">纬度</div>
                  <div class="info-value">{{ lutouDetails.大地坐标Y }}</div>
                </div>
              </div>
              
              <!-- 文字介绍 -->
              <div class="info-item description">
                <div class="info-label">文字介绍</div>
                <div class="info-value description-text">{{ lutouDetails.文字介绍 }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { get3DModelDetails } from '../api/api';
import emitter from '@/eventBus';

export default {
  name: 'RightDrawer_lutou',
  data() {
    return {
      loading: false,
      error: null,
      lutouDetails: null,
      isOpen: false
    }
  },
  mounted() {
    // 监听缩略图点击事件
    emitter.on('thumbnail-clicked', this.handleThumbnailClick);
    // 监听关闭事件
    emitter.on('close-lutou-drawer', this.closeDrawer);
  },
  beforeDestroy() {
    // 移除事件监听
    emitter.off('thumbnail-clicked', this.handleThumbnailClick);
    emitter.off('close-lutou-drawer', this.closeDrawer);
  },
  methods: {
    toggleDrawer() {
      this.isOpen = !this.isOpen;
    },
    closeDrawer() {
      this.isOpen = false;
    },
    async handleThumbnailClick(modelId) {
      this.loading = true;
      this.error = null;
      try {
        const details = await get3DModelDetails(modelId);
        this.lutouDetails = details;
        this.isOpen = true; // 在获取数据成功后打开抽屉
      } catch (error) {
        console.error('Error fetching lutou details:', error);
        this.error = '加载露头信息时发生错误';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.right-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
  backdrop-filter: blur(10px);
  box-shadow: -2px 0 15px rgba(0, 0, 0, 0.1);
  border-radius: 20px 0 0 20px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(100%);
  z-index: 1000;
  border-left: 1px solid rgba(74, 144, 226, 0.1);
}

.right-drawer-open {
  transform: translateX(0);
}

.drawer-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(74, 144, 226, 0.1);
  margin-bottom: 20px;
}

.drawer-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

.drawer-body::-webkit-scrollbar {
  width: 6px;
}

.drawer-body::-webkit-scrollbar-track {
  background: rgba(74, 144, 226, 0.1);
  border-radius: 3px;
}

.drawer-body::-webkit-scrollbar-thumb {
  background: rgba(74, 144, 226, 0.3);
  border-radius: 3px;
}

.drawer-body::-webkit-scrollbar-thumb:hover {
  background: rgba(74, 144, 226, 0.5);
}

.info-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.description {
  grid-column: 1 / -1;
  margin-top: 20px;
}

.description-text {
  white-space: pre-wrap;
  line-height: 1.6;
  margin-top: 8px;
}

.info-item {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  padding: 15px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(74, 144, 226, 0.1);
  position: relative;
  overflow: hidden;
}

.info-item::before {
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

.info-item:hover::before {
  opacity: 1;
}

.info-item:hover {
  transform: translateX(-5px) scale(1.02);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2);
}

.info-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.info-value {
  font-size: 16px;
  color: #333;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(74, 144, 226, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(74, 144, 226, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(74, 144, 226, 0);
  }
}

.info-item:focus-within {
  animation: pulse 1.5s infinite;
}

.toggle-button {
  position: fixed;
  top: 50px;
  right: 0;
  padding: 10px 20px 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-top-left-radius: 10px;
  border-bottom-left-radius: 10px;
  cursor: pointer;
  outline: none;
  font-size: 16px;
  transition: background-color 0.3s;
  z-index: 999;
}

.toggle-button:hover {
  background-color: #0056b3;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 10px;
  color: #666;
}

.error-message {
  background: #fef0f0;
  color: #f56c6c;
  padding: 15px;
  border-radius: 8px;
  margin: 10px;
  text-align: center;
  border: 1px solid #fde2e2;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 10px;
  color: #666;
  font-size: 14px;
}

.lutou-details {
  padding: 20px;
}
</style> 