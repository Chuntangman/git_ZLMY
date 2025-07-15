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
            <div class="drawer-header">
              <div class="header-content">
                <h3>露头信息</h3>
              </div>
            </div>
            <div class="drawer-body">
              <!-- 主要内容区域 -->
              <div class="info-section">
                <div v-if="loading" class="loading-message">
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

                  <!-- 多媒体内容 -->
                  <div class="info-item media-section">
                    <div class="info-label">多媒体内容</div>
                    <div v-if="loading" class="loading-message">
                      加载中...
                    </div>
                    <div v-else-if="!lutouDetails?.has_media" class="no-media-message">
                      暂无相关数据
                    </div>
                    <div v-else class="media-content">
                      <!-- 图片内容 -->
                      <div v-for="media in imageFiles" :key="media.id" class="media-item">
                        <img :src="media.data" :alt="lutouDetails.地理地名" class="media-image" @click="showFullImage(media.data)" />
                      </div>
                      
                      <!-- 视频内容 -->
                      <div v-for="media in videoFiles" :key="media.id" class="media-item video-container">
                        <div class="video-thumbnail" @click="playVideo(media)">
                          <video 
                            class="media-video" 
                            preload="metadata"
                          >
                            <source :src="media.url" type="video/mp4">
                            您的浏览器不支持视频播放。
                          </video>
                          <div class="play-button">
                            <i class="play-icon">▶</i>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
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
      isOpen: false,
      currentModelId: null,
      debug: false // 关闭调试模式
    }
  },
  computed: {
    // 过滤图片文件
    imageFiles() {
      if (!this.lutouDetails?.media_files) return [];
      return this.lutouDetails.media_files.filter(media => 
        media.type && ['png', 'jpg', 'jpeg'].includes(media.type.toLowerCase()) && media.data
      );
    },
    // 过滤视频文件
    videoFiles() {
      if (!this.lutouDetails?.media_files) return [];
      return this.lutouDetails.media_files.filter(media => 
        media.type && media.type.toLowerCase() === 'mp4' && media.url
      );
    }
  },
  watch: {
    // 监听lutouDetails变化，用于调试
    lutouDetails: {
      handler(newVal) {
        console.log('lutouDetails updated:', {
          hasMedia: newVal?.has_media,
          mediaFilesCount: newVal?.media_files?.length,
          mediaFiles: newVal?.media_files
        });
      },
      deep: true
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
      this.lutouDetails = null;
      this.currentModelId = null;
    },
    async handleThumbnailClick(modelId) {
      console.log('Thumbnail clicked:', modelId);
      
      // 如果是同一个模型，不重复加载
      if (this.currentModelId === modelId && this.lutouDetails) {
        this.isOpen = true;
        return;
      }
      
      this.loading = true;
      this.error = null;
      this.currentModelId = modelId;
      
      try {
        console.log('Fetching details for model:', modelId);
        const details = await get3DModelDetails(modelId);
        console.log('Received details:', details);
        this.lutouDetails = details;
        this.isOpen = true;
      } catch (error) {
        console.error('Error fetching lutou details:', error);
        this.error = '加载露头信息时发生错误';
        this.lutouDetails = null;
      } finally {
        this.loading = false;
      }
    },
    showFullImage(imageUrl) {
      // 创建全屏图片查看器
      const viewer = document.createElement('div');
      viewer.className = 'fullscreen-viewer';
      viewer.innerHTML = `
        <div class="fullscreen-content">
          <img src="${imageUrl}" alt="Full size image">
          <button class="close-button">关闭</button>
        </div>
      `;
      document.body.appendChild(viewer);
      
      // 添加关闭事件
      viewer.querySelector('.close-button').onclick = () => {
        document.body.removeChild(viewer);
      };
      viewer.onclick = (e) => {
        if (e.target === viewer) {
          document.body.removeChild(viewer);
        }
      };
    },
    playVideo(media) {
      // 创建全屏视频播放器
      const viewer = document.createElement('div');
      viewer.className = 'fullscreen-viewer';
      
      // 构建完整的视频URL
      let videoUrl = media.url;
      console.log('Original video URL:', videoUrl);
      
      // 处理相对路径
      if (!videoUrl.startsWith('http')) {
        // 移除项目名前缀
        videoUrl = videoUrl.replace('my-cesium-app/', '');
        // 确保文件扩展名
        if (!videoUrl.endsWith('.mp4')) {
          videoUrl = videoUrl + '.mp4';
        }
        // 使用相对于public目录的路径
        if (!videoUrl.startsWith('/')) {
          videoUrl = '/' + videoUrl;
        }
      }
      
      console.log('Processed video URL:', videoUrl);
      
      viewer.innerHTML = `
        <div class="fullscreen-content">
          <video controls autoplay class="fullscreen-video" preload="auto">
            <source src="${videoUrl}" type="video/mp4">
            您的浏览器不支持视频播放。
          </video>
          <button class="close-button">关闭</button>
          <div class="video-status"></div>
        </div>
      `;
      
      // 在添加到DOM之前设置样式
      viewer.style.position = 'fixed';
      viewer.style.top = '0';
      viewer.style.left = '0';
      viewer.style.width = '100%';
      viewer.style.height = '100%';
      viewer.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
      viewer.style.display = 'flex';
      viewer.style.justifyContent = 'center';
      viewer.style.alignItems = 'center';
      viewer.style.zIndex = '10000';
      
      document.body.appendChild(viewer);
      
      // 获取视频元素
      const videoElement = viewer.querySelector('video');
      const statusDiv = viewer.querySelector('.video-status');
      
      // 设置视频样式
      videoElement.style.maxWidth = '90vw';
      videoElement.style.maxHeight = '80vh';
      videoElement.style.width = 'auto';
      videoElement.style.height = 'auto';
      
      // 设置状态提示样式
      statusDiv.style.position = 'absolute';
      statusDiv.style.bottom = '20px';
      statusDiv.style.left = '50%';
      statusDiv.style.transform = 'translateX(-50%)';
      statusDiv.style.color = 'white';
      statusDiv.style.padding = '10px';
      statusDiv.style.borderRadius = '4px';
      statusDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
      
      // 获取关闭按钮
      const closeButton = viewer.querySelector('.close-button');
      closeButton.style.position = 'absolute';
      closeButton.style.top = '20px';
      closeButton.style.right = '20px';
      closeButton.style.padding = '8px 16px';
      closeButton.style.backgroundColor = 'white';
      closeButton.style.border = 'none';
      closeButton.style.borderRadius = '4px';
      closeButton.style.cursor = 'pointer';
      closeButton.style.zIndex = '10001';
      
      const cleanup = () => {
        videoElement.pause();
        document.body.removeChild(viewer);
        document.removeEventListener('keydown', handleKeyDown);
      };
      
      // 添加视频事件监听
      videoElement.onloadstart = () => {
        statusDiv.textContent = '开始加载视频...';
        console.log('Video load started');
      };
      
      videoElement.oncanplay = () => {
        statusDiv.textContent = '视频已准备就绪';
        console.log('Video can play');
      };
      
      videoElement.onplaying = () => {
        statusDiv.textContent = '';
        console.log('Video is playing');
      };
      
      videoElement.onwaiting = () => {
        statusDiv.textContent = '视频加载中...';
        console.log('Video is buffering');
      };
      
      videoElement.onerror = (e) => {
        console.error('Video error:', videoElement.error);
        console.error('Error event:', e);
        console.error('Video source:', videoUrl);
        statusDiv.textContent = `视频加载失败: ${videoElement.error?.message || '未知错误'}`;
      };
      
      // 添加关闭事件
      closeButton.onclick = cleanup;
      
      // 点击背景关闭
      viewer.onclick = (e) => {
        if (e.target === viewer) {
          cleanup();
        }
      };
      
      // 添加键盘事件监听
      const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
          cleanup();
        }
      };
      document.addEventListener('keydown', handleKeyDown);
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

.media-section {
  margin-top: 20px;
}

.media-content {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 10px;
}

.media-item {
  position: relative;
  aspect-ratio: 16/9;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s ease;
  background: #f5f5f5;
}

.media-item:hover {
  transform: scale(1.05);
}

.media-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.media-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #000;
}

.video-container {
  position: relative;
  cursor: pointer;
}

.video-thumbnail {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.play-icon {
  color: white;
  font-size: 24px;
  margin-left: 4px;
}

.video-container:hover .play-button {
  background: rgba(0, 0, 0, 0.9);
  transform: translate(-50%, -50%) scale(1.1);
}

.fullscreen-video {
  max-width: 90vw;
  max-height: 80vh;
  width: auto;
  height: auto;
}

.fullscreen-viewer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.fullscreen-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.fullscreen-content img,
.fullscreen-content video {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
}

.close-button {
  position: absolute;
  top: -40px;
  right: 0;
  background: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  z-index: 10000;
}

.close-button:hover {
  background: #f0f0f0;
}

.debug-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.debug-info h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #495057;
}

.debug-info pre {
  margin: 10px 0;
  padding: 10px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow-x: auto;
}

.no-media-message {
  text-align: center;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  color: #666;
  font-size: 14px;
  margin-top: 10px;
}
</style> 