// 环境设置组件，用于管理和控制Cesium地图上的各种标注功能
<template>
  <div class="environmental-setup" v-show="isOpen">
    <div class="setup-header">
      <h3>环境设置</h3>
      <button @click="closeSetup" class="close-btn">×</button>
    </div>
    <div class="setup-content">
      <div class="annotation-section">
        <h4>标注工具</h4>
        <div class="tool-buttons">
          <button 
            v-for="tool in annotationTools" 
            :key="tool.id"
            @click="selectTool(tool)"
            :class="['tool-btn', { active: currentTool === tool.id }]"
            :title="tool.description"
          >
            {{ tool.name }}
          </button>
        </div>
      </div>
      
      <!-- 标注样式设置面板 -->
      <div class="style-panel" v-if="currentTool">
        <h4>样式设置</h4>
        <!-- 通用设置 -->
        <div class="style-item">
          <label>颜色</label>
          <input type="color" v-model="annotationStyle.color">
        </div>
        
        <!-- 根据不同工具显示不同的设置选项 -->
        <template v-if="currentTool === 'billboard'">
          <div class="style-item">
            <label>图标大小</label>
            <input type="range" v-model="annotationStyle.scale" min="0.1" max="5" step="0.1">
          </div>
          <div class="style-item">
            <label>选择图标</label>
            <select v-model="annotationStyle.image">
              <option value="pin">标注针</option>
              <option value="marker">标记点</option>
              <option value="flag">旗帜</option>
            </select>
          </div>
        </template>
        
        <template v-if="currentTool === 'label'">
          <div class="style-item">
            <label>字体大小</label>
            <input type="number" v-model="annotationStyle.fontSize" min="10" max="50">
          </div>
          <div class="style-item">
            <label>文本内容</label>
            <input type="text" v-model="annotationStyle.text" placeholder="输入标签文本">
          </div>
        </template>
        
        <template v-if="currentTool === 'polyline'">
          <div class="style-item">
            <label>线宽</label>
            <input type="range" v-model="annotationStyle.width" min="1" max="10">
          </div>
          <div class="style-item">
            <label>线型</label>
            <select v-model="annotationStyle.style">
              <option value="solid">实线</option>
              <option value="dashed">虚线</option>
              <option value="dotted">点线</option>
            </select>
          </div>
        </template>
        
        <template v-if="currentTool === 'polygon'">
          <div class="style-item">
            <label>填充透明度</label>
            <input type="range" v-model="annotationStyle.alpha" min="0" max="1" step="0.1">
          </div>
          <div class="style-item">
            <label>边框宽度</label>
            <input type="number" v-model="annotationStyle.outlineWidth" min="1" max="10">
          </div>
        </template>
      </div>
      
      <div class="action-buttons">
        <button @click="startDrawing" :disabled="!currentTool">开始绘制</button>
        <button @click="clearAnnotations">清除所有</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import emitter from '@/eventBus'

export default {
  name: 'EnvironmentalSetup',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    viewer: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const currentTool = ref(null)
    const drawingMode = ref(false)
    const annotations = reactive(new Map())
    
    const annotationTools = [
      { id: 'billboard', name: '点标注', description: '添加点标注' },
      { id: 'label', name: '文本标注', description: '添加文本标签' },
      { id: 'polyline', name: '线标注', description: '添加路径线条' },
      { id: 'polygon', name: '面标注', description: '添加多边形区域' }
    ]
    
    const annotationStyle = reactive({
      color: '#ff0000',
      scale: 1,
      image: 'pin',
      fontSize: 16,
      text: '',
      width: 2,
      style: 'solid',
      alpha: 0.5,
      outlineWidth: 2
    })
    
    // 处理标注绘制
    const handleClick = (event) => {
      if (!drawingMode.value || !currentTool.value) return
      
      const cartesian = props.viewer.camera.pickEllipsoid(
        event.position,
        props.viewer.scene.globe.ellipsoid
      )
      
      if (!cartesian) return
      
      switch (currentTool.value) {
        case 'billboard':
          addBillboard(cartesian)
          break
        case 'label':
          addLabel(cartesian)
          break
        case 'polyline':
          addToPolyline(cartesian)
          break
        case 'polygon':
          addToPolygon(cartesian)
          break
      }
    }
    
    // 添加点标注
    const addBillboard = (position) => {
      const billboard = props.viewer.entities.add({
        position: position,
        billboard: {
          image: `/images/${annotationStyle.image}.png`,
          scale: annotationStyle.scale,
          color: Cesium.Color.fromCssColorString(annotationStyle.color)
        }
      })
      annotations.set(billboard.id, billboard)
      drawingMode.value = false
    }
    
    // 添加文本标注
    const addLabel = (position) => {
      const label = props.viewer.entities.add({
        position: position,
        label: {
          text: annotationStyle.text || '标签',
          font: `${annotationStyle.fontSize}px sans-serif`,
          fillColor: Cesium.Color.fromCssColorString(annotationStyle.color),
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          outlineWidth: 2,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM
        }
      })
      annotations.set(label.id, label)
      drawingMode.value = false
    }
    
    // 存储多段线的点
    const polylinePositions = []
    
    // 添加线段点
    const addToPolyline = (position) => {
      polylinePositions.push(position)
      
      if (polylinePositions.length > 1) {
        // 如果已经存在线条实体，则更新它
        const existingPolyline = Array.from(annotations.values())
          .find(entity => entity.polyline)
        
        if (existingPolyline) {
          existingPolyline.polyline.positions = new Cesium.CallbackProperty(() => {
            return polylinePositions
          }, false)
        } else {
          // 创建新的线条实体
          const polyline = props.viewer.entities.add({
            polyline: {
              positions: polylinePositions,
              width: annotationStyle.width,
              material: new Cesium.PolylineDashMaterialProperty({
                color: Cesium.Color.fromCssColorString(annotationStyle.color),
                dashLength: annotationStyle.style === 'dashed' ? 16.0 : 0.0
              })
            }
          })
          annotations.set(polyline.id, polyline)
        }
      }
    }
    
    // 存储多边形的点
    const polygonPositions = []
    
    // 添加多边形点
    const addToPolygon = (position) => {
      polygonPositions.push(position)
      
      if (polygonPositions.length > 2) {
        // 如果已经存在多边形实体，则更新它
        const existingPolygon = Array.from(annotations.values())
          .find(entity => entity.polygon)
        
        if (existingPolygon) {
          existingPolygon.polygon.hierarchy = new Cesium.CallbackProperty(() => {
            return new Cesium.PolygonHierarchy(polygonPositions)
          }, false)
        } else {
          // 创建新的多边形实体
          const polygon = props.viewer.entities.add({
            polygon: {
              hierarchy: new Cesium.PolygonHierarchy(polygonPositions),
              material: new Cesium.ColorMaterialProperty(
                Cesium.Color.fromCssColorString(annotationStyle.color).withAlpha(annotationStyle.alpha)
              ),
              outline: true,
              outlineColor: Cesium.Color.WHITE,
              outlineWidth: annotationStyle.outlineWidth
            }
          })
          annotations.set(polygon.id, polygon)
        }
      }
    }
    
    // 开始绘制
    const startDrawing = () => {
      drawingMode.value = true;
      if (currentTool.value === 'polyline') {
        polylinePositions.length = 0;
      } else if (currentTool.value === 'polygon') {
        polygonPositions.length = 0;
      }
      
      // 发送开始绘制事件
      emitter.emit('start-drawing', {
        tool: currentTool.value,
        style: annotationStyle
      });
    }
    
    // 清除所有标注
    const clearAnnotations = () => {
      emitter.emit('clear-annotations');
      annotations.clear();
      polylinePositions.length = 0;
      polygonPositions.length = 0;
    }
    
    // 选择工具
    const selectTool = (tool) => {
      if (currentTool.value === tool.id) {
        currentTool.value = null;
        emitter.emit('stop-drawing');
      } else {
        currentTool.value = tool.id;
        if (drawingMode.value) {
          emitter.emit('stop-drawing');
          drawingMode.value = false;
        }
      }
    }
    
    // 关闭设置面板
    const closeSetup = () => {
      if (drawingMode.value) {
        emitter.emit('stop-drawing');
        drawingMode.value = false;
      }
      emitter.emit('close-environmental-setup');
    }
    
    return {
      currentTool,
      annotationTools,
      annotationStyle,
      startDrawing,
      clearAnnotations,
      selectTool,
      closeSetup
    }
  }
}
</script>

<style scoped>
.environmental-setup {
  position: fixed;
  top: 50%;
  left: 80px;
  transform: translateY(-50%);
  width: 300px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.setup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.setup-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.annotation-section {
  margin-bottom: 20px;
}

.tool-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 10px;
}

.tool-btn {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.tool-btn:hover {
  background: #f5f5f5;
}

.tool-btn.active {
  background: #4a90e2;
  color: white;
  border-color: #4a90e2;
}

.style-panel {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.style-item {
  margin-bottom: 10px;
}

.style-item label {
  display: block;
  margin-bottom: 5px;
  color: #666;
}

.style-item input[type="color"],
.style-item input[type="range"],
.style-item input[type="number"],
.style-item input[type="text"],
.style-item select {
  width: 100%;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-buttons button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: #4a90e2;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.action-buttons button:hover {
  background: #357abd;
}

.action-buttons button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style> 