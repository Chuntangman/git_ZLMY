// 要素点击信息组件，用于显示点击要素的详细信息，支持属性展示和交互
<template>
  <!-- 使用过渡动画效果 -->
  <transition name="fade">
    <!-- 主容器，根据visible属性控制显示/隐藏 -->
    <div v-if="visible" class="click-container" :style="containerStyle" @click="handleContainerClick">
      <!-- 媒体图标区域（固定在气泡上方） -->
      <div class="media-icons">
        <!-- 遍历媒体列表，渲染每个媒体图标 -->
        <div 
          v-for="(media, index) in mediaList" 
          :key="index"
          class="media-icon"
          @click.stop="openMedia(media)">
          <!-- 为第一个图标添加波纹效果 -->
          <div class="circle" :class="{ 'ripple-effect': index === 0 }"></div>
          <!-- 媒体图标图片 -->
          <img :src="media.icon" :alt="media.type">
          <!-- 媒体类型文字 -->
          <span class="media-type">{{ media.type }}</span>
        </div>
      </div>

      <!-- 信息气泡区域 -->
      <div class="info-bubble">
        <div class="bubble-content">
          <!-- 标题 -->
          <h4>岩石标本信息</h4>
          <!-- 信息网格布局 -->
          <div class="info-grid">
            <!-- 编号信息行 -->
            <div class="info-row">
              <span class="info-label">编号</span>
              <span class="info-value">{{ feature.number || 'N/A' }}</span>
            </div>
            <!-- 基本名称信息行 -->
            <div class="info-row">
              <span class="info-label">基本名称</span>
              <span class="info-value">{{ feature.properties?.['基本名称'] || '未知' }}</span>
            </div>
            <!-- 岩石类别信息行 -->
            <div class="info-row">
              <span class="info-label">岩石类别</span>
              <span class="info-value">{{ feature.properties?.['岩石类别'] || '未知' }}</span>
            </div>
            <!-- 颜色信息行 -->
            <div class="info-row">
              <span class="info-label">颜色</span>
              <span class="info-value">{{ feature.properties?.['颜色'] || '未知' }}</span>
            </div>
          </div>
        </div>
        <!-- 位置标记（三角形指示器） -->
        <div class="location-marker"></div>
      </div>
    </div>
  </transition>
</template>

<script>
// 导入事件总线
import emitter from '@/eventBus';
// 导入图片
import videoIcon from '@/image/视频.png';
import imageIcon from '@/image/图片.png';
// import jumpIcon from '@/image/跳转.jpg';  // 注销跳转按钮

export default {
  // 组件名称
  name: 'FeatureClickInfo',
  
  // 组件数据
  data() {
    return {
      visible: false,        // 控制组件显示/隐藏
      feature: {},           // 存储特征信息
      position: { x: 0, y: 0 }, // 存储点击位置坐标
      // 媒体列表数据
      mediaList: [
        { type: '视频', icon: videoIcon, url: '' },
        { type: '图片', icon: imageIcon, url: '' },
        // { type: '跳转', icon: jumpIcon, url: '' }  // 注销跳转按钮
      ]
    };
  },

  // 计算属性
  computed: {
    // 计算容器的样式
    containerStyle() {
      return {
        left: `${this.position.x}px`,      // 水平位置
        top: `${this.position.y}px`,       // 垂直位置
        transform: 'translate(-50%, -100%)' // 居中定位
      };
    }
  },

  // 方法
  methods: {
    // 显示信息方法
    async showInfo({ feature, position }) {
      this.position = position;  // 更新位置信息
      
      try {
        // 获取 NewRegion3D.json 数据
        const response = await fetch('/mock-models/NewRegion3D.json');
        const jsonData = await response.json();
        
        // 根据编号查找对应的要素
        const matchedFeature = jsonData.features.find(f => f.properties.Number === feature.number);
        
        if (matchedFeature) {
          // 合并原有feature和找到的JSON数据
          this.feature = {
            ...feature,
            properties: matchedFeature.properties
          };
        } else {
          // 如果没找到匹配的，使用原有数据
          this.feature = feature;
        }
      } catch (error) {
        console.error('加载NewRegion3D.json失败:', error);
        this.feature = feature;
      }
      
      this.visible = true;       // 显示组件
      // 点击要素时展开底部边栏
      emitter.emit('expand-bottom-sidebar');
    },

    // 隐藏信息方法
    hideInfo() {
      this.visible = false;      // 隐藏组件
      // 隐藏信息时收起底部边栏
      emitter.emit('collapse-bottom-sidebar');
    },

    // 打开媒体方法
    openMedia(media) {
      console.log('打开媒体:', media.type);
    },

    // 处理容器点击事件
    handleContainerClick() {
      // 点击容器时展开底部边栏，不再需要判断JSON数据
      emitter.emit('expand-bottom-sidebar');
    },

    // 处理文档点击事件
    handleDocumentClick(event) {
      // 如果点击的不是容器内的元素，则隐藏信息和收起底部边栏
      if (this.visible && !this.$el.contains(event.target)) {
        this.hideInfo();
      }
    }
  },

  // 组件挂载后
  mounted() {
    // 监听特征点击事件
    emitter.on('feature-click', this.showInfo);
    // 监听清除特征点击事件
    emitter.on('feature-click-clear', this.hideInfo);
    // 添加文档点击事件监听
    document.addEventListener('click', this.handleDocumentClick);
  },

  // 组件卸载前
  beforeUnmount() {
    // 移除事件监听
    emitter.off('feature-click', this.showInfo);
    emitter.off('feature-click-clear', this.hideInfo);
    // 移除文档点击事件监听
    document.removeEventListener('click', this.handleDocumentClick);
  }
};
</script>

<style scoped>
/* 容器定位 */
.click-container {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1000;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
  cursor: pointer;
}

/* 媒体图标容器 */
.media-icons {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

/* 单个媒体图标 */
.media-icon {
  position: relative;
  width: 50px;
  height: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 圆形背景 */
.circle {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(255,255,255,0.9);
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  z-index: -1;
  transition: all 0.3s ease;
}

/* 波纹动效（仅第一个图标） */
.ripple-effect {
  animation: ripple 2s infinite; /* 调整动画速度 */
}
@keyframes ripple {
  0% {
    box-shadow: 0 0 0 0 rgba(74, 144, 226, 0.7);
  }
  40% {
    box-shadow: 0 0 0 15px rgba(74, 144, 226, 0);
  }
  60% {
    box-shadow: 0 0 0 20px rgba(74, 144, 226, 0);
  }
  80% {
    box-shadow: 0 0 0 25px rgba(74, 144, 226, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(74, 144, 226, 0);
  }
}

/* 图标图片 */
.media-icon img {
  width: 24px;
  height: 24px;
  margin-bottom: 2px;
}

/* 图标文字 */
.media-type {
  font-size: 10px;
  color: #333;
  font-weight: 500;
}

/* 信息气泡 */
.info-bubble {
  position: relative;
  background: white;

  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  min-width: 200px;
}

.bubble-content {
  text-align: center;
}

.bubble-content h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(74, 144, 226, 0.05);
  border-radius: 8px;
}

.info-label {
  font-size: 12px;
  color: #666;
}

.info-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.location-marker {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid white;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -90%) scale(0.9);
}
</style>