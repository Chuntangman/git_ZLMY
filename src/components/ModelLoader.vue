// 模型加载器组件，用于加载和显示三维模型，支持地质走廊相关模型展示
<template>
  <div class="model-loader"></div>
</template>

<script>
import emitter from '@/eventBus';

export default {
  name: 'ModelLoader',
  props: {
    viewer: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      tileset: null,
      isLoading: false,
      isModelLoaded: false,
      modelPosition: null // 存储模型位置
    };
  },
  mounted() {
    emitter.on('viewer-ready', this.initModelLoading);
    this.exposeMethods();
  },
  methods: {
    async loadModel() {
      if (this.isLoading) return;
      
      // 如果模型已经加载，只移动视角
      if (this.isModelLoaded && this.tileset) {
        await this.moveToModel();
        return;
      }

      this.isLoading = true;

      try {
        if (!this.$Cesium) {
          console.error('Cesium未正确注入');
          return;
        }
        const Cesium = this.$Cesium;

        // 临时测试代码
        const mockData = {
          modelUrl: '/mock-models/out4/tileset.json'
        };
        console.log('使用模拟数据:', mockData);
        const modelUrl = mockData.modelUrl;

        // 先移动到模型位置
        if (this.modelPosition) {
          await this.moveToPosition(this.modelPosition);
        } else {
          // 如果没有存储的位置，先加载模型获取位置
          this.tileset = new Cesium.Cesium3DTileset({
            url: modelUrl,
            maximumScreenSpaceError: 32,
            skipLevelOfDetail: true,
            dynamicScreenSpaceError: false,
          });
          await this.tileset.readyPromise;
          this.modelPosition = this.tileset.boundingSphere.center;
          await this.moveToModel();
          this.viewer.scene.primitives.remove(this.tileset);
          this.tileset.destroy();
        }

        // 等待3秒
        await new Promise(resolve => setTimeout(resolve, 2200));

        // 加载模型
        this.tileset = new Cesium.Cesium3DTileset({
          url: modelUrl,
          maximumScreenSpaceError: 32,
          skipLevelOfDetail: true,
          dynamicScreenSpaceError: false,
        });

        this.viewer.scene.primitives.add(this.tileset);

        await this.tileset.readyPromise;
        console.log('Tileset加载完成');
        this.isModelLoaded = true;

      } catch (error) {
        console.error('模型加载失败:', error);
      } finally {
        this.isLoading = false;
      }
    },

    // 移动到指定位置
    async moveToPosition(position) {
      const Cesium = this.$Cesium;
      await this.viewer.camera.flyTo({
        destination: position,
        orientation: {
          heading: Cesium.Math.toRadians(0),
          pitch: Cesium.Math.toRadians(-35),
          roll: 0.0
        },
        duration: 2
      });
    },

    // 移动到模型位置
    async moveToModel() {
      if (!this.tileset) return;
      
      const Cesium = this.$Cesium;
      const boundingSphere = this.tileset.boundingSphere;
      await this.viewer.camera.flyToBoundingSphere(boundingSphere, {
        offset: new Cesium.HeadingPitchRange(
          Cesium.Math.toRadians(0),
          Cesium.Math.toRadians(-35),
          boundingSphere.radius * 1.5
        ),
        duration: 2
      });
    },

    initModelLoading() {
      this.loadModel();
    },

    exposeMethods() {
      if (typeof this.$options.expose === 'undefined') {
        this.$options.expose = [];
      }
      this.$options.expose.push('loadModel');
    }
  },
  beforeUnmount() {
    if (this.tileset) {
      this.viewer.scene.primitives.removeAndDestroy(this.tileset);
    }
    emitter.off('viewer-ready', this.initModelLoading);
  }
};
</script>

<style scoped>
.model-loader {
  display: none;
}
</style>