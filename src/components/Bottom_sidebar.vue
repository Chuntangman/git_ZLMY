// 底部边框栏组件，用于显示图片缩略图，支持翻页，点击图片时跳转到对应三维模型视角
<template>
  <div class="bottom-sidebar" :class="{ 'expanded': isExpanded }">
    <div class="expand-handle" @click="toggleExpand">
      <span class="expand-icon">{{ isExpanded ? '▼' : '▲' }}</span>
    </div>
    <div class="sidebar-content">
      <button class="arrow left" :disabled="currentPage === 0" @click="prevPage">
        <span>&lt;</span>
      </button>
      <div class="thumbnails">
        <div
          v-for="item in pagedItems"
          :key="item.ID"
          class="thumbnail-card"
          @click="handleThumbnailClick(item)"
          @mouseenter="handleMouseEnter(item)"
          @mouseleave="handleMouseLeave(item)"
        >
          <div class="tooltip" v-show="item.hovering">
            <div class="tooltip-content">
              <div class="tooltip-item">
                <span class="tooltip-label">经度：</span>
                <span class="tooltip-value">{{ item.大地坐标X }}</span>
              </div>
              <div class="tooltip-item">
                <span class="tooltip-label">纬度：</span>
                <span class="tooltip-value">{{ item.大地坐标Y }}</span>
              </div>
              <div class="tooltip-item">
                <span class="tooltip-label">盆地：</span>
                <span class="tooltip-value">{{ item.盆地 }}</span>
              </div>
              <div class="tooltip-item">
                <span class="tooltip-label">所处方位：</span>
                <span class="tooltip-value">{{ item.所处方位 }}</span>
              </div>
            </div>
          </div>
          <img :src="getThumbPath(item.URL)" :alt="item.地理地名" />
          <div class="thumbnail-info">
            <div class="thumbnail-id">#{{ item.ID }}</div>
            <div class="thumbnail-name">{{ item.地理地名 }}</div>
          </div>
        </div>
      </div>
      <button class="arrow right" :disabled="endIndex >= items.length" @click="nextPage">
        <span>&gt;</span>
      </button>
    </div>
  </div>
</template>

<script>
import emitter from '@/eventBus';
import defaultThumb from '@/image/图片.png';  // 使用已有的图片作为默认缩略图
import { get3DModels } from '../api/api';

export default {
  name: 'BottomSidebar',
  props: {
    pageSize: {
      type: Number,
      default: 5,
    },
  },
  data() {
    return {
      items: [],
      currentPage: 0,
      isExpanded: false, // 默认隐藏
      loading: false,
      error: null
    };
  },
  computed: {
    startIndex() {
      return this.currentPage * this.pageSize;
    },
    endIndex() {
      return this.startIndex + this.pageSize;
    },
    pagedItems() {
      return this.items.slice(this.startIndex, this.endIndex);
    },
  },
  methods: {
    prevPage() {
      if (this.currentPage > 0) this.currentPage--;
    },
    nextPage() {
      if (this.endIndex < this.items.length) this.currentPage++;
    },
    handleThumbnailClick(item) {
      // 处理模型路径：将 public/mock-models/xxx/tileset.json 转换为 /mock-models/xxx/tileset.json
      const modelPath = item.URL.replace(/^public\\/, '').replace(/\\/g, '/');
      
      // 1. 通知InfoMoveLoader加载模型
      emitter.emit('model-path-changed', '/' + modelPath);
      
      // 2. 触发露头信息显示（这不会影响其他组件，因为只有RightDrawer_lutou在监听这个事件）
      emitter.emit('thumbnail-clicked', item.ID);
      
      // 3. 如果有其他需要处理的点击事件，可以继续添加
    },
    toggleExpand() {
      this.isExpanded = !this.isExpanded;
    },
    expand() {
      this.isExpanded = true;
    },
    collapse() {
      this.isExpanded = false;
    },
    getThumbPath(url) {
      // 从模型路径生成缩略图路径
      // 例如: public/mock-models/yanhe/tileset.json -> /Thumbnail/yanhe.png
      if (!url) return defaultThumb;
      
      const match = url.match(/mock-models\/([^/]+)\/tileset\.json$/);
      if (match) {
        const modelName = match[1];
        return `/Thumbnail/${modelName}.png`;
      }
      return defaultThumb;
    },
    async loadItems() {
      this.loading = true;
      this.error = null;
      try {
        // 从数据库API获取数据
        const data = await get3DModels();
        // 为每个项目添加 hovering 属性
        this.items = data.map(item => ({
          ...item,
          hovering: false
        }));
      } catch (error) {
        console.error('Error loading items:', error);
        this.error = error.message;
        this.items = [];
      } finally {
        this.loading = false;
      }
    },
    handleMouseEnter(item) {
      item.hovering = true;
    },
    handleMouseLeave(item) {
      item.hovering = false;
    },
  },
  async mounted() {
    // 监听展开和收起事件
    emitter.on('expand-bottom-sidebar', this.expand);
    emitter.on('collapse-bottom-sidebar', this.collapse);
    // 加载数据
    await this.loadItems();
  },
  beforeDestroy() {
    // 移除事件监听
    emitter.off('expand-bottom-sidebar', this.expand);
    emitter.off('collapse-bottom-sidebar', this.collapse);
  }
};
</script>

<style scoped>
.bottom-sidebar {
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 80vw;
  min-width: 600px;
  max-width: 1200px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px 12px 0 0;
  box-shadow: 0 -2px 16px rgba(0,0,0,0.2);
  z-index: 1001;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translate(-50%, calc(100% - 4px)); /* 只露出4px的高度 */
}

.bottom-sidebar.expanded {
  transform: translate(-50%, 0);
}

.expand-handle {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 10px; /* 减小手柄高度为4px */
  background: inherit;
  border-radius: 12px 12px 0 0;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.expand-icon {
  display: none; /* 隐藏箭头图标 */
}

.sidebar-content {
  padding: 16px 24px 12px 24px;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.5); /* 确保内容区域也有背景色 */
}

.thumbnails {
  display: flex;
  flex: 1;
  justify-content: center;
  gap: 18px;
}

.thumbnail-card {
  width: 120px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  overflow: visible;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.thumbnail-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 12px rgba(0, 191, 255, 0.5);
}

.thumbnail-card img {
  width: 100%;
  height: 80px;
  object-fit: cover;
}

.thumbnail-info {
  padding: 8px;
  background: rgba(255, 255, 255, 0.8);
}

.thumbnail-id {
  color: #00bfff;
  font-size: 12px;
  margin-bottom: 2px;
}

.thumbnail-name {
  color: #333;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arrow {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.7);
  color: #333;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.arrow:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.9);
}

.arrow:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.arrow.left {
  margin-right: 10px;
}

.arrow.right {
  margin-left: 10px;
}

.tooltip {
  position: absolute;
  bottom: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  padding: 12px;
  border-radius: 8px;
  z-index: 1000;
  width: max-content;
  min-width: 200px;
  margin-bottom: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  pointer-events: none;
}

.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.95) transparent transparent transparent;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tooltip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.tooltip-label {
  color: #666;
  font-size: 12px;
}

.tooltip-value {
  color: #333;
  font-size: 13px;
  font-weight: 500;
}
</style> 