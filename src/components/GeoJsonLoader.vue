// GeoJSON加载器组件，用于加载和显示GeoJSON数据，支持地质走廊相关地理信息展示
<template>
  <div class="geo-json-loader"></div>
</template>

<script>
import emitter from '@/eventBus';

export default {
  name: 'GeoJsonLoader',
  props: {
    viewer: {
      type: Object,
      required: true,
      validator: (value) => value && !value.isDestroyed()
    }
  },
  data() {
    return {
      dataSource: null,
      clickHandler: null,
      loadAttempted: false,
      lastClickedFeature: null // 记录最后点击的特征
    };
  },
  mounted() {
    this.safeLoadGeoJson();
    emitter.on('load-geological-corridor', this.safeLoadGeoJson);
  },
  methods: {
    async safeLoadGeoJson() {
      if (!this.isViewerReady()) {
        this.loadAttempted = true;
        return;
      }
      try {
        await this.loadGeoJson();
      } catch (error) {
        console.error('GeoJSON加载失败:', error);
      }
    },

    async loadGeoJson() {
      this.cleanup();

      // 模拟数据
      const mockData = {
        geoJsonUrl: '/mock-models/NewRegion3D.json',
        style: {
          stroke: '#0000FF',
          fill: '#00FF00',
          strokeWidth: 3
        }
      };

      const Cesium = this.$Cesium;
      
      // 加载数据源
      this.dataSource = await Cesium.GeoJsonDataSource.load(
        mockData.geoJsonUrl,
        {
          stroke: Cesium.Color.BLUE,
          fill: Cesium.Color.GREEN.withAlpha(0.01), // 设置为99%透明
          strokeWidth: 3
        }
      );

      await this.viewer.dataSources.add(this.dataSource);
      //geojson透明度
      // 设置实体样式
      this.dataSource.entities.values.forEach(entity => {
        if (entity.polygon) {
          entity.polygon.material = Cesium.Color.GREEN.withAlpha(0.01); // 设置为99%透明
          entity.polygon.outline = true;
          entity.polygon.outlineColor = Cesium.Color.BLACK.withAlpha(0.01); // 边框也设置为99%透明
          entity.isPickable = true;
        }
      });

      this.setupClickHandler();
    },

    setupClickHandler() {
      if (!this.isViewerReady()) return;

      const Cesium = this.$Cesium;
      
      // 移除旧的事件处理器
      if (this.clickHandler && !this.clickHandler.isDestroyed()) {
        this.clickHandler.destroy();
      }

      this.clickHandler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);
      
      this.clickHandler.setInputAction((click) => {
        const pickedObject = this.viewer.scene.pick(click.position);
        
        if (pickedObject?.id?.properties) {
          // 获取特征属性
          const properties = {
            area: pickedObject.id.properties?.Area?.getValue(),
            number: pickedObject.id.properties?.Number?.getValue(),
            tilesetPath: pickedObject.id.properties?.tilesetPath?.getValue() || ''
          };
          
          // 获取屏幕坐标（使用点击位置）
          const position = { 
            x: click.position.x, 
            y: click.position.y 
          };
          
          // 存储最后点击的特征
          this.lastClickedFeature = {
            feature: properties,
            position: position
          };
          
          // 触发点击事件
          emitter.emit('feature-click', this.lastClickedFeature);
          
          // 同时触发原有的选择事件（用于抽屉）
          this.$emit('feature-selected', properties);
          
        } else {
          // 点击空白处时清除显示
          emitter.emit('feature-click-clear');
          this.lastClickedFeature = null;
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    },

    isViewerReady() {
      return this.viewer && !this.viewer.isDestroyed();
    },

    cleanup() {
      if (this.dataSource && this.isViewerReady()) {
        this.viewer.dataSources.remove(this.dataSource);
      }
      if (this.clickHandler && !this.clickHandler.isDestroyed()) {
        this.clickHandler.destroy();
      }
      this.dataSource = null;
      this.clickHandler = null;
      this.lastClickedFeature = null;
    }
  },
  beforeUnmount() {
    emitter.off('load-geological-corridor', this.safeLoadGeoJson);
    this.cleanup();
  }
};
</script>