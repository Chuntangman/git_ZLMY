// 右侧抽屉组件，用于显示可滑出的内容，支持动画和交互
<template>
  <div>
    <button v-if="showButton" class="toggle-button" @click="toggleDrawer">Toggle Right Drawer</button>
    <div class="right-drawer" :class="{ 'right-drawer-open': isOpen }">
      <div class="drawer-content">
        <div class="drawer-header">
          <div class="header-content">
            <h3>{{ isViewingDetails ? selectedEntityId : '关联信息' }}</h3>
            <button v-if="isViewingDetails" class="back-button" @click="backToRelations">
              返回
            </button>
          </div>
        </div>
        <div class="drawer-body">
          <!-- Relations List View -->
          <div v-if="!isViewingDetails">
            <div v-if="selectedFeature && !loading">
              <div v-if="currentRelations.length > 0">
                <div v-for="(relation, index) in filteredRelations" :key="index" class="relation-item">
                  <div class="relation-header">
                    <div class="relation-title">关联关系 #{{index + 1}}</div>
                    <div class="relation-type">{{ relation['关联类型'] }}</div>
                  </div>
                  <div class="relation-content">
                    <div class="relation-entities">
                      <div class="entity-flow">
                        <span 
                          class="entity" 
                          @click="viewEntityDetails(relation['关联实体ID1'])"
                          style="cursor: pointer;"
                        >
                          {{ relation['关联实体ID1'] }}
                        </span>
                        <span class="relation-arrow">
                          <span class="arrow-label">关联程度: {{ relation['关联程度'].toFixed(2) }}</span>
                          →
                        </span>
                        <span 
                          class="entity" 
                          @click="viewEntityDetails(relation['关联实体ID2'])"
                          style="cursor: pointer;"
                        >
                          {{ relation['关联实体ID2'] }}
                        </span>
                      </div>
                    </div>
                    <div class="image-container" v-if="relation.url">
                      <img :src="relation.url" :alt="'关联图片'" @error="handleImageError">
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="no-data">
                暂无关联数据
              </div>
            </div>
            <div v-else-if="loading" class="loading">
              加载中...
            </div>
          </div>

          <!-- Entity Details View -->
          <div v-else class="entity-details">
            <div class="tabs">
              <div 
                class="tab" 
                :class="{ active: currentTab === 'basic' }"
                @click="currentTab = 'basic'"
              >
                基本信息
              </div>
              <div 
                class="tab" 
                :class="{ active: currentTab === 'thin-section' }"
                @click="currentTab = 'thin-section'"
              >
                薄片鉴定
              </div>
              <div 
                class="tab" 
                :class="{ active: currentTab === 'xrf' }"
                @click="currentTab = 'xrf'"
              >
                XRF测试
              </div>
            </div>
            <div class="tab-content">
              <div v-if="currentTab === 'basic'" class="tab-pane">
                <!-- Basic Info Content -->
                <div v-if="loading" class="loading">加载中...</div>
                <div v-else-if="sampleDetails" class="sample-details">
                  <div class="info-section">
                    <h4>基本属性</h4>
                    <div class="info-grid">
                      <div class="info-item">
                        <div class="info-label">名称</div>
                        <div class="info-value">{{ sampleDetails.名称 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">盆地</div>
                        <div class="info-value">{{ sampleDetails.盆地 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">来源</div>
                        <div class="info-value">{{ sampleDetails.来源 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">层位</div>
                        <div class="info-value">{{ sampleDetails.层位 }}</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 样品图片显示 -->
                  <div v-if="sampleDetails.media_files && sampleDetails.media_files.length > 0" class="media-section">
                    <h4>样品图片</h4>
                    <div class="media-grid">
                      <div v-for="(media, index) in sampleDetails.media_files" :key="index" class="media-item">
                        <img :src="media.data" :alt="'样品图片 ' + (index + 1)" @error="handleImageError">
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data">暂无样品信息</div>
              </div>
              <div v-else-if="currentTab === 'thin-section'" class="tab-pane">
                <!-- Thin Section Content -->
                <div v-if="loading" class="loading">加载中...</div>
                <div v-else-if="thinSectionDetails" class="thin-section-details">
                  <!-- 基本特征组 -->
                  <div class="info-section">
                    <h4>基本特征</h4>
                    <div class="info-grid">
                      <div class="info-item">
                        <div class="info-label">岩类</div>
                        <div class="info-value">{{ thinSectionDetails.岩类 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">成分</div>
                        <div class="info-value">{{ thinSectionDetails.成分 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">粒度</div>
                        <div class="info-value">{{ thinSectionDetails.粒度 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">颜色</div>
                        <div class="info-value">{{ thinSectionDetails.颜色 }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- 特殊特征组 -->
                  <div class="info-section">
                    <h4>特殊特征</h4>
                    <div class="info-grid">
                      <div class="info-item">
                        <div class="info-label">特殊物质</div>
                        <div class="info-value">{{ thinSectionDetails.特殊物质 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">特殊结构</div>
                        <div class="info-value">{{ thinSectionDetails.特殊结构 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">磨圆</div>
                        <div class="info-value">{{ thinSectionDetails.磨圆 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">分选</div>
                        <div class="info-value">{{ thinSectionDetails.分选 }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- 含量分析组 -->
                  <div class="info-section">
                    <h4>含量分析</h4>
                    <div class="info-grid">
                      <div class="info-item">
                        <div class="info-label">面孔率</div>
                        <div class="info-value">{{ thinSectionDetails.面孔率 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">岩屑含量</div>
                        <div class="info-value">{{ thinSectionDetails.岩屑含量 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">长石含量</div>
                        <div class="info-value">{{ thinSectionDetails.长石含量 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">石英含量</div>
                        <div class="info-value">{{ thinSectionDetails.石英含量 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">杂基</div>
                        <div class="info-value">{{ thinSectionDetails.杂基 }}</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 薄片照片显示 -->
                  <div v-if="thinSectionDetails.media_files && thinSectionDetails.media_files.length > 0" class="media-section">
                    <h4>薄片照片</h4>
                    <div class="media-grid">
                      <div v-for="(media, index) in thinSectionDetails.media_files" :key="index" class="media-item">
                        <img :src="media.data" :alt="'薄片照片 ' + (index + 1)" @error="handleImageError">
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data">暂无薄片鉴定数据</div>
              </div>
              <div v-else-if="currentTab === 'xrf'" class="tab-pane">
                <div v-if="loading" class="loading">加载中...</div>
                <div v-else-if="xrfDetails" class="xrf-details">
                  <!-- 基本信息 -->
                  <div class="info-section">
                    <h4>基本信息</h4>
                    <div class="info-grid">
                      <div class="info-item">
                        <div class="info-label">层位</div>
                        <div class="info-value">{{ xrfDetails.层位 }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">野外定名</div>
                        <div class="info-value">{{ xrfDetails.野外定名 }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- 元素含量 -->
                  <div class="info-section">
                    <h4>元素含量分析</h4>
                    <div class="info-grid">
                      <div class="info-item">
                        <div class="info-label">Si</div>
                        <div class="info-value">{{ xrfDetails.Si }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">Mg</div>
                        <div class="info-value">{{ xrfDetails.Mg }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">Al</div>
                        <div class="info-value">{{ xrfDetails.Al }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">K</div>
                        <div class="info-value">{{ xrfDetails.K }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">Ca</div>
                        <div class="info-value">{{ xrfDetails.Ca }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">Fe</div>
                        <div class="info-value">{{ xrfDetails.Fe }}</div>
                      </div>
                      <div class="info-item">
                        <div class="info-label">Ba</div>
                        <div class="info-value">{{ xrfDetails.Ba }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data">暂无XRF测试数据</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getRelations, getRockSampleDetails, getThinSectionDetails, getXRFTestResults } from '../api/api';

export default {
  name: 'RightDrawer',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    selectedFeature: {
      type: Object,
      default: null
    },
    showButton: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    filteredRelations() {
      return this.currentRelations.filter(relation => relation['关联类型'] === '标本-样品');
    }
  },
  data() {
    return {
      currentRelations: [],
      loading: false,
      imageError: false,
      isViewingDetails: false,
      selectedEntityId: null,
      currentTab: 'basic',
      sampleDetails: null,
      thinSectionDetails: null,
      xrfDetails: null,
      tabs: [
        { id: 'basic', name: '基本信息' },
        { id: 'thin-section', name: '薄片鉴定' },
        { id: 'xrf', name: 'XRF测试' }
      ]
    }
  },
  watch: {
    selectedFeature: {
      immediate: true,
      handler(newFeature) {
        if (newFeature && newFeature.number) {
          this.findRelations(newFeature.number);
        } else {
          this.currentRelations = [];
        }
      }
    },
    currentTab: {
      immediate: true,
      handler: async function(newTab) {
        if (this.selectedEntityId) {
          if (newTab === 'basic' && !this.sampleDetails) {
            await this.viewEntityDetails(this.selectedEntityId);
          } else if (newTab === 'thin-section' && !this.thinSectionDetails) {
            await this.fetchThinSectionDetails(this.selectedEntityId);
          } else if (newTab === 'xrf' && !this.xrfDetails) {
            await this.fetchXRFDetails(this.selectedEntityId);
          }
        }
      }
    }
  },
  methods: {
    toggleDrawer() {
      this.$emit('toggle');
    },
    async findRelations(entityId) {
      this.loading = true;
      try {
        this.currentRelations = await getRelations(entityId);
      } catch (error) {
        console.error('Error loading relations:', error);
        this.currentRelations = [];
      } finally {
        this.loading = false;
      }
    },
    handleImageError(event) {
      event.target.style.display = 'none';
      console.error('Image failed to load:', event.target.src);
    },
    async viewEntityDetails(entityId) {
      console.log('Entity clicked:', entityId);
      this.selectedEntityId = entityId;
      this.isViewingDetails = true;
      this.currentTab = 'basic';
      this.loading = true;
      this.sampleDetails = null;
      this.thinSectionDetails = null;
      this.xrfDetails = null;
      
      try {
        const details = await getRockSampleDetails(entityId);
        this.sampleDetails = details;
      } catch (error) {
        console.error('Error loading sample details:', error);
      } finally {
        this.loading = false;
      }
      
      this.$emit('entity-selected', entityId);
    },
    backToRelations() {
      this.isViewingDetails = false;
      this.selectedEntityId = null;
      this.sampleDetails = null;
      this.thinSectionDetails = null;
      this.xrfDetails = null;
    },
    async fetchXRFDetails(id) {
      try {
        this.loading = true;
        const data = await getXRFTestResults(id);
        this.xrfDetails = data;
      } catch (error) {
        console.error('Error fetching XRF details:', error);
        this.xrfDetails = null;
      } finally {
        this.loading = false;
      }
    },
    async fetchThinSectionDetails(id) {
      try {
        this.loading = true;
        const details = await getThinSectionDetails(id);
        this.thinSectionDetails = details;
      } catch (error) {
        console.error('Error loading thin section details:', error);
        this.thinSectionDetails = null;
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

.info-item {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
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

/* 添加新的动画效果 */
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

/* 按钮样式 */
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

.relation-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #f9f9f9;
}

.relation-item:nth-child(3n+1) {
  background: linear-gradient(to right, #90bee9, #f9f9f9);
}

.relation-item:nth-child(3n+2) {
  background: linear-gradient(to right, #e49bce, #f9f9f9);
}

.relation-item:nth-child(3n+3) {
  background: linear-gradient(to right, #a2d695, #f9f9f9);
}

.relation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.relation-title {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.relation-type {
  color: #666;
  font-size: 14px;
  padding: 2px 8px;
  background: #e8e8e8;
  border-radius: 4px;
}

.relation-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.relation-entities {
  padding: 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.entity-flow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px;
}

.entity {
  padding: 6px 12px;
  background: #e3f2fd;
  border-radius: 4px;
  color: #1976d2;
  font-weight: 500;
  cursor: pointer !important;
  transition: all 0.3s ease;
  user-select: none;
  z-index: 10;
  position: relative;
}

.entity:hover {
  background: #bbdefb;
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.entity:active {
  transform: scale(0.98);
}

.relation-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #666;
  font-size: 18px;
  position: relative;
}

.arrow-label {
  font-size: 12px;
  color: #666;
  position: absolute;
  top: -20px;
  white-space: nowrap;
}

.image-container {
  margin-top: 10px;
  width: 100%;
  max-height: 200px;
  overflow: hidden;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.back-button {
  padding: 4px 12px;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #e0e0e0;
}

.tabs {
  display: flex;
  gap: 2px;
  background: #f5f5f5;
  padding: 2px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.tab {
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  font-size: 14px;
  color: #666;
}

.tab:hover {
  color: #409EFF;
  background-color: rgba(64, 158, 255, 0.1);
}

.tab.active {
  color: #409EFF;
  border-bottom-color: #409EFF;
  font-weight: 500;
}

.tab-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  min-height: 300px;
}

.placeholder-content {
  color: #999;
  text-align: center;
  padding: 40px;
  font-size: 14px;
  background: #f9f9f9;
  border-radius: 6px;
  border: 2px dashed #eee;
}

.entity-details {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.sample-details {
  padding: 20px;
}

.info-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.info-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.info-item {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.info-item:hover {
  background: #f0f2f5;
  transform: translateY(-2px);
}

.info-label {
  color: #666;
  font-size: 12px;
  margin-bottom: 4px;
}

.info-value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.media-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-top: 20px;
}

.media-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.media-item {
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.media-item:hover {
  transform: scale(1.05);
}

.media-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tab-pane {
  padding: 15px;
}

.loading, .no-data {
  text-align: center;
  padding: 20px;
  color: #666;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 10px;
}

.xrf-details {
  padding: 20px;
}
</style>
