<template>
  <div class="modal-overlay" v-if="isOpen">
    <div class="search-window">
      <div class="window-header">
        <h2>岩石标本查询</h2>
        <button class="close-button" @click="$emit('toggle-window')">&times;</button>
      </div>

      <!-- 搜索区域 -->
      <div class="search-section">
        <!-- 基本名称搜索 -->
        <div class="main-search">
          <input 
            type="text" 
            v-model="searchQuery.基本名称" 
            placeholder="输入岩石基本名称..."
            class="main-search-input"
            @keyup.enter="searchRocks"
          />
          <button class="search-button" @click="searchRocks">
            <span class="search-icon">🔍</span>
            <span class="search-text">搜索</span>
          </button>
        </div>

        <!-- 高级筛选 -->
        <div class="advanced-filters">
          <div class="filter-row">
            <div class="filter-item">
              <label>岩石类别</label>
              <select v-model="searchQuery.岩石类别" @change="searchRocks">
                <option value="">全部</option>
                <option v-for="type in filterOptions.岩石类别" :key="type" :value="type">
                  {{ type }}
                </option>
              </select>
            </div>
            <div class="filter-item">
              <label>颜色</label>
              <select v-model="searchQuery.颜色" @change="searchRocks">
                <option value="">全部</option>
                <option v-for="color in filterOptions.颜色" :key="color" :value="color">
                  {{ color }}
                </option>
              </select>
            </div>
            <div class="filter-item">
              <label>主要成分</label>
              <select v-model="searchQuery.主要成分" @change="searchRocks">
                <option value="">全部</option>
                <option v-for="comp in mainComponents" :key="comp" :value="comp">
                  {{ comp }}
                </option>
              </select>
            </div>
          </div>
          <div class="filter-row">
            <div class="filter-item">
              <label>粒度（主要）</label>
              <select v-model="searchQuery.粒度" @change="searchRocks">
                <option value="">全部</option>
                <option v-for="size in filterOptions.粒度" :key="size" :value="size">
                  {{ size }}
                </option>
              </select>
            </div>
            <div class="filter-item">
              <label>特殊结构</label>
              <select v-model="searchQuery.特殊结构" @change="searchRocks">
                <option value="">全部</option>
                <option v-for="struct in filterOptions.特殊结构" :key="struct" :value="struct">
                  {{ struct }}
                </option>
              </select>
            </div>
            <div class="filter-item">
              <label>特殊矿物</label>
              <select v-model="searchQuery.特殊矿物" @change="searchRocks">
                <option value="">全部</option>
                <option v-for="mineral in filterOptions.特殊矿物" :key="mineral" :value="mineral">
                  {{ mineral }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- 结果展示区域 -->
      <div class="results-container">
        <div v-if="loading" class="loading-state">
          <span>加载中...</span>
        </div>
        <div v-else-if="error" class="error-state">
          <span>{{ error }}</span>
        </div>
        <div v-else-if="searchResults.length === 0" class="no-results">
          <span>未找到匹配的岩石标本</span>
        </div>
        <div v-else class="results-grid">
          <div v-for="rock in searchResults" :key="rock.ID" class="rock-card">
            <!-- 图片预留区域 -->
            <div class="rock-image-placeholder">
              <img v-if="rock.imageUrl" :src="rock.imageUrl" alt="岩石图片" />
              <div v-else class="no-image">暂无图片</div>
            </div>
            <!-- 岩石信息 -->
            <div class="rock-info">
              <h3>{{ rock.基本名称 }}</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">岩石类别:</span>
                  <span>{{ rock.岩石类别 }}</span>
                </div>
                <div class="info-item">
                  <span class="label">颜色:</span>
                  <span>{{ rock.颜色 }}</span>
                </div>
                <div class="info-item">
                  <span class="label">主要成分:</span>
                  <span>{{ rock.主要成分 }}</span>
                </div>
                <div class="info-item">
                  <span class="label">粒度:</span>
                  <span>{{ rock.粒度 }}</span>
                </div>
                <div class="info-item">
                  <span class="label">特殊结构:</span>
                  <span>{{ rock.特殊结构 || '无' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">特殊矿物:</span>
                  <span>{{ rock.特殊矿物 || '无' }}</span>
                </div>
              </div>
              <div class="classification-info">
                <small>系: {{ rock.系 }} | 组段: {{ rock.组段 }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { rockSampleApi } from '../api/api';

export default {
  name: 'SlideOutWindow',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const searchQuery = reactive({
      基本名称: '',
      岩石类别: '',
      颜色: '',
      主要成分: '',
      粒度: '',
      特殊结构: '',
      特殊矿物: ''
    });

    const filterOptions = reactive({
      岩石类别: [],
      颜色: [],
      主要成分: [],
      粒度: [],
      特殊结构: [],
      特殊矿物: []
    });

    // 预设的主要成分选项
    const mainComponents = [
      '石英',
      '正长石',
      '方解石',
      '粘土矿物',
      '白云石',
      '燧石',
      '长石',
      '斜长石',
      '角闪石',
      '钾长石',
      '黑云母',
      '赤铁矿',
      '黄铁矿',
      '海绿石',
      '晶屑'
    ];

    const searchResults = ref([]);
    const loading = ref(false);
    const error = ref(null);

    // 获取筛选选项
    const fetchFilterOptions = async () => {
      try {
        loading.value = true;
        error.value = null;
        const options = await rockSampleApi.getFilterOptions();
        Object.keys(filterOptions).forEach(key => {
          if (options[key]) {
            filterOptions[key] = options[key];
          }
        });
      } catch (err) {
        error.value = '获取筛选选项失败';
        console.error('Error fetching filter options:', err);
      } finally {
        loading.value = false;
      }
    };

    // 搜索岩石
    const searchRocks = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        // 构建查询参数
        const params = {};
        Object.entries(searchQuery).forEach(([key, value]) => {
          if (value) params[key] = value;
        });

        // 调用API
        const results = await rockSampleApi.getRockSamples(params);
        searchResults.value = results;
      } catch (err) {
        error.value = '搜索失败';
        console.error('搜索失败:', err);
      } finally {
        loading.value = false;
      }
    };

    // 组件挂载时获取筛选选项和执行初始搜索
    onMounted(() => {
      fetchFilterOptions();
      searchRocks(); // 执行初始搜索
    });

    return {
      searchQuery,
      filterOptions,
      mainComponents,
      searchResults,
      loading,
      error,
      searchRocks
    };
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.search-window {
  background: white;
  width: 90%;
  max-width: 1200px;
  height: 80vh;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.window-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.window-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 5px;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.close-button:hover {
  background: #f5f5f5;
  color: #333;
}

.search-section {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.main-search {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.main-search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s;
}

.main-search-input:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.search-button {
  padding: 0 24px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.search-button:hover {
  background: #357abd;
}

.advanced-filters {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.filter-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-item label {
  font-size: 14px;
  color: #666;
}

.filter-item select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.results-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 10px;
}

.rock-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  width: 100%;
  min-height: 400px; /* 设置固定最小高度 */
  display: flex;
  flex-direction: column;
}

.rock-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.rock-image-placeholder {
  height: 200px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0; /* 防止图片区域被压缩 */
}

.rock-image-placeholder img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #999;
  font-size: 14px;
}

.rock-info {
  padding: 15px;
  flex-grow: 1; /* 允许信息区域增长以填充剩余空间 */
  display: flex;
  flex-direction: column;
}

.rock-info h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.info-item {
  font-size: 14px;
}

.info-item .label {
  color: #666;
  margin-right: 5px;
}

.classification-info {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
  color: #999;
  font-size: 12px;
}

.loading-state,
.error-state,
.no-results {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #666;
}

.error-state {
  color: #ff4444;
}

/* 确保选择框样式统一 */
.filter-item select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

/* 添加响应式布局 */
@media (max-width: 1200px) {
  .results-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .results-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
</style>