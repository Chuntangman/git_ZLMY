<template>
  <div class="viewer-container">
    <CesiumViewer 
      ref="mainViewer"
      :isMainView="true"
      @view-ready="handleViewReady"
    />
    <!-- 标注工具栏 -->
    <div class="annotation-toolbar" v-if="annotationSettings.enabled">
      <button 
        v-for="tool in annotationTools" 
        :key="tool.type"
        :class="['tool-btn', { active: currentTool === tool.type }]"
        @click="selectTool(tool.type)"
        :title="tool.title"
      >
        {{ tool.label }}
      </button>
    </div>
    <!-- 测量结果显示 -->
    <div class="measurement-result" v-if="measurementSettings.enabled && measurementResult">
      {{ measurementResult }}
    </div>
  </div>
</template>

<script>
import CesiumViewer from './CesiumViewer.vue';
import emitter from '@/eventBus';

export default {
  name: 'MapViewer',
  components: {
    CesiumViewer
  },
  data() {
    return {
      viewer: null,
      scene: null,
      camera: null,
      annotationSettings: {
        enabled: false,
        color: '#FF0000',
        scale: 1.0,
        showLabel: true,
        font: '14px sans-serif',
        style: 'point'
      },
      drawingSettings: {
        enabled: false,
        type: 'polyline',
        color: '#00FF00',
        width: 2,
        fill: true,
        fillColor: '#00FF00',
        fillAlpha: 0.5
      },
      measurementSettings: {
        enabled: false,
        type: 'distance',
        showLabels: true,
        unit: 'meters'
      },
      currentTool: null,
      measurementResult: null,
      annotationTools: [
        { type: 'point', label: '点标注', title: '添加点标注' },
        { type: 'polyline', label: '线', title: '绘制线段' },
        { type: 'polygon', label: '面', title: '绘制多边形' },
        { type: 'rectangle', label: '矩形', title: '绘制矩形' },
        { type: 'circle', label: '圆形', title: '绘制圆形' },
        { type: 'text', label: '文字', title: '添加文字标注' },
        { type: 'distance', label: '距离', title: '测量距离' },
        { type: 'area', label: '面积', title: '测量面积' },
        { type: 'height', label: '高度', title: '测量高度' }
      ],
      drawingEntities: [],
      measurementEntities: []
    }
  },
  methods: {
    handleViewReady(viewerData) {
      this.viewer = viewerData.viewer;
      this.scene = viewerData.scene;
      this.camera = viewerData.camera;
      this.initializeEventHandlers();
    },
    initializeEventHandlers() {
      // 监听标注设置变更
      emitter.on('toggle-annotation', this.toggleAnnotation);
      emitter.on('update-annotation-style', this.updateAnnotationStyle);
      emitter.on('update-annotation-color', this.updateAnnotationColor);
      
      // 监听绘图设置变更
      emitter.on('toggle-drawing', this.toggleDrawing);
      emitter.on('update-drawing-type', this.updateDrawingType);
      
      // 监听测量设置变更
      emitter.on('toggle-measurement', this.toggleMeasurement);
      emitter.on('update-measurement-type', this.updateMeasurementType);
    },
    selectTool(toolType) {
      if (this.currentTool === toolType) {
        this.currentTool = null;
        this.deactivateAllTools();
      } else {
        this.currentTool = toolType;
        this.activateTool(toolType);
      }
    },
    activateTool(toolType) {
      if (!this.viewer) return;
      
      const Cesium = this.$Cesium;
      const handler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);
      
      switch (toolType) {
        case 'point':
          this.activatePointTool(handler);
          break;
        case 'polyline':
          this.activatePolylineTool(handler);
          break;
        case 'polygon':
          this.activatePolygonTool(handler);
          break;
        case 'rectangle':
          this.activateRectangleTool(handler);
          break;
        case 'circle':
          this.activateCircleTool(handler);
          break;
        case 'text':
          this.activateTextTool(handler);
          break;
        case 'distance':
        case 'area':
        case 'height':
          this.activateMeasurementTool(handler, toolType);
          break;
      }
    },
    deactivateAllTools() {
      if (this.viewer) {
        // 清理所有事件处理器
        this.viewer.screenSpaceEventHandler.removeInputAction(
          this.$Cesium.ScreenSpaceEventType.LEFT_CLICK
        );
        this.viewer.screenSpaceEventHandler.removeInputAction(
          this.$Cesium.ScreenSpaceEventType.MOUSE_MOVE
        );
        this.viewer.screenSpaceEventHandler.removeInputAction(
          this.$Cesium.ScreenSpaceEventType.RIGHT_CLICK
        );
      }
      this.currentTool = null;
      this.measurementResult = null;
    },
    // 工具激活方法
    activatePointTool(handler) {
      const Cesium = this.$Cesium;
      handler.setInputAction((click) => {
        const cartesian = this.viewer.scene.pickPosition(click.position);
        if (cartesian) {
          this.addPoint(cartesian);
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    },
    activatePolylineTool(handler) {
      const Cesium = this.$Cesium;
      let positions = [];
      let polyline;
      
      handler.setInputAction((click) => {
        const cartesian = this.viewer.scene.pickPosition(click.position);
        if (cartesian) {
          if (positions.length === 0) {
            positions.push(cartesian);
            positions.push(cartesian.clone());
            polyline = this.addPolyline(positions);
          }
          positions.push(cartesian);
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
      
      handler.setInputAction((movement) => {
        if (positions.length >= 2) {
          const cartesian = this.viewer.scene.pickPosition(movement.endPosition);
          if (cartesian) {
            positions[positions.length - 1] = cartesian;
          }
        }
      }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
      
      handler.setInputAction(() => {
        handler.destroy();
        this.currentTool = null;
      }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);
    },
    // 添加实体方法
    addPoint(position) {
      const entity = this.viewer.entities.add({
        position: position,
        point: {
          pixelSize: 10,
          color: this.$Cesium.Color.fromCssColorString(this.annotationSettings.color),
          outlineColor: this.$Cesium.Color.WHITE,
          outlineWidth: 2
        }
      });
      this.drawingEntities.push(entity);
      return entity;
    },
    addPolyline(positions) {
      const entity = this.viewer.entities.add({
        polyline: {
          positions: positions,
          width: this.drawingSettings.width,
          material: this.$Cesium.Color.fromCssColorString(this.drawingSettings.color),
          clampToGround: true
        }
      });
      this.drawingEntities.push(entity);
      return entity;
    },
    // 清理方法
    clearDrawings() {
      this.drawingEntities.forEach(entity => {
        this.viewer.entities.remove(entity);
      });
      this.drawingEntities = [];
    },
    clearMeasurements() {
      this.measurementEntities.forEach(entity => {
        this.viewer.entities.remove(entity);
      });
      this.measurementEntities = [];
      this.measurementResult = null;
    }
  },
  beforeUnmount() {
    // 清理事件监听
    emitter.off('toggle-annotation');
    emitter.off('update-annotation-style');
    emitter.off('update-annotation-color');
    emitter.off('toggle-drawing');
    emitter.off('update-drawing-type');
    emitter.off('toggle-measurement');
    emitter.off('update-measurement-type');
    
    // 清理实体
    this.clearDrawings();
    this.clearMeasurements();
  }
}
</script>

<style scoped>
.viewer-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.annotation-toolbar {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.tool-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.3s ease;
}

.tool-btn:hover {
  background: #f0f0f0;
}

.tool-btn.active {
  background: #4a90e2;
  color: white;
}

.measurement-result {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style> 