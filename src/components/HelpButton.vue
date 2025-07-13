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
            <div class="toggle-switch">
              <input type="checkbox" v-model="enableAnimations" id="animations">
              <label for="animations"></label>
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
      enableAnimations: true
    }
  },
  computed: {
    title() {
      return this.type === 'settings' ? '设置' : '帮助';
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
</style> 