// 信息帮助功能，用于显示详细信息，支持弹窗展示和交互
<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="close-button" @click="closeModal">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="type === 'settings'" class="settings-content">
          <div class="setting-item">
            <label>地图样式</label>
            <select v-model="selectedMapStyle">
              <option value="default">默认</option>
              <option value="dark">暗色</option>
              <option value="light">亮色</option>
            </select>
          </div>
          <div class="setting-item">
            <label>动画效果</label>
            <div class="toggle-switch" title="开启后可以看到地图上的动画过渡效果">
              <input type="checkbox" v-model="enableAnimations" id="animations">
              <label for="animations"></label>
            </div>
          </div>
          <!-- 添加新的特效控制选项 -->
          <div class="setting-item">
            <div class="label-with-tooltip" 
                 title="开启后可以看到太阳光照对地球表面的影响，在白天和黑夜交替时最明显。
建议：调整时间到日出或日落时分观察效果最佳。">
              <label>太阳光照效果</label>
              <span class="info-icon">?</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="enableSunLighting" id="sunLighting">
              <label for="sunLighting"></label>
            </div>
          </div>
          <div class="setting-item">
            <div class="label-with-tooltip" 
                 title="开启后可以看到地球大气层的蓝色渐变效果。
建议：远距离观察地球时效果最明显，可以通过鼠标滚轮缩放查看。">
              <label>大气效果</label>
              <span class="info-icon">?</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="enableAtmosphere" id="atmosphere">
              <label for="atmosphere"></label>
            </div>
          </div>
          <div class="setting-item">
            <div class="label-with-tooltip" 
                 title="开启后可以看到地形的阴影效果，使地形更加立体。
建议：在山地区域放大观察效果最明显。">
              <label>地形阴影</label>
              <span class="info-icon">?</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="enableTerrainShadows" id="terrainShadows">
              <label for="terrainShadows"></label>
            </div>
          </div>
          <div class="setting-item">
            <div class="label-with-tooltip" 
                 title="开启后会在地球表面显示流星特效。
建议：在夜晚场景下观察效果最佳。">
              <label>粒子效果</label>
              <span class="info-icon">?</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="enableParticleEffects" id="particleEffects">
              <label for="particleEffects"></label>
            </div>
          </div>
          <div class="setting-item">
            <div class="label-with-tooltip" 
                 title="开启后会显示飞行路径动画。
建议：开启后可以看到飞行轨迹，并且相机会自动跟随。">
              <label>飞行动画</label>
              <span class="info-icon">?</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="enableFlightAnimations" id="flightAnimations">
              <label for="flightAnimations"></label>
            </div>
          </div>
          <div class="setting-item">
            <div class="label-with-tooltip" 
                 title="开启后可以看到逼真的水面波动和反射效果。
建议：在海洋、湖泊等水域区域观察效果最佳，水面会随时间缓慢波动。">
              <label>水体特效</label>
              <span class="info-icon">?</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="enableWaterEffect" id="waterEffect">
              <label for="waterEffect"></label>
            </div>
          </div>
          <div class="setting-item">
            <div class="label-with-tooltip" 
                 title="开启后将使用更高质量的地球纹理和渲染效果。
建议：开启后地形和建筑物的细节会更加清晰，但可能会影响性能。">
              <label>高质量纹理</label>
              <span class="info-icon">?</span>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" v-model="enableHighQualityTextures" id="highQualityTextures">
              <label for="highQualityTextures"></label>
            </div>
          </div>
        </div>
        <div v-else class="help-content">
          <div class="help-section">
            <h4>使用说明</h4>
            <p>1. 点击侧边栏按钮可以切换不同的功能模块</p>
            <p>2. 使用鼠标滚轮可以缩放地图</p>
            <p>3. 按住鼠标左键可以旋转视角</p>
            <p>4. 按住鼠标右键可以平移地图</p>
          </div>
          <div class="help-section">
            <h4>快捷键</h4>
            <p>Ctrl + Z: 撤销操作</p>
            <p>Ctrl + Y: 重做操作</p>
            <p>Space: 重置视角</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelpButton',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'settings'
    }
  },
  data() {
    return {
      selectedMapStyle: 'default',
      enableAnimations: false,
      enableSunLighting: false,
      enableAtmosphere: false,
      enableTerrainShadows: false,
      enableParticleEffects: false,
      enableFlightAnimations: false,
      enableWaterEffect: false,
      enableHighQualityTextures: false
    }
  },
  computed: {
    title() {
      return this.type === 'settings' ? '设置' : '帮助';
    }
  },
  watch: {
    enableSunLighting(newVal) {
      this.$emit('update-effect', 'sunLighting', newVal);
    },
    enableAtmosphere(newVal) {
      this.$emit('update-effect', 'atmosphere', newVal);
    },
    enableTerrainShadows(newVal) {
      this.$emit('update-effect', 'terrainShadows', newVal);
    },
    enableParticleEffects(newVal) {
      this.$emit('update-effect', 'particleEffects', newVal);
    },
    enableFlightAnimations(newVal) {
      this.$emit('update-effect', 'flightAnimations', newVal);
    },
    enableWaterEffect(newVal) {
      this.$emit('update-effect', 'waterEffect', newVal);
    },
    enableHighQualityTextures(newVal) {
      this.$emit('update-effect', 'highQualityTextures', newVal);
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.9));
  border-radius: 15px;
  width: 400px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  animation: modalFadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #333;
  transform: rotate(90deg);
}

.modal-body {
  padding: 20px;
}

.setting-item {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-item label {
  color: #2c3e50;
  font-size: 14px;
  font-weight: 500;
}

.setting-item select {
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.8);
  color: #2c3e50;
  font-size: 14px;
  transition: all 0.3s ease;
}

.setting-item select:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-switch label {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.toggle-switch label:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

.toggle-switch input:checked + label {
  background-color: #4a90e2;
}

.toggle-switch input:checked + label:before {
  transform: translateX(26px);
}

.help-section {
  margin-bottom: 25px;
}

.help-section h4 {
  color: #2c3e50;
  font-size: 16px;
  margin-bottom: 10px;
  font-weight: 600;
}

.help-section p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin: 8px 0;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.label-with-tooltip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: help;
}

.info-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #e0e0e0;
  color: #666;
  font-size: 12px;
  font-weight: bold;
  cursor: help;
}

.label-with-tooltip:hover {
  color: #4a90e2;
}

.info-icon:hover {
  background-color: #4a90e2;
  color: white;
}

/* 添加工具提示样式 */
[title] {
  position: relative;
}

[title]:hover::after {
  content: attr(title);
  position: absolute;
  left: -10px;
  top: 100%;
  z-index: 1000;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: pre-wrap;
  width: max-content;
  max-width: 300px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  pointer-events: none;
  margin-top: 8px;
}

[title]:hover::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 100%;
  border: 6px solid transparent;
  border-bottom-color: rgba(0, 0, 0, 0.8);
  transform: translateY(-2px);
  pointer-events: none;
}

.setting-item {
  position: relative;
}
</style> 