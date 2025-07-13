// 信息移动加载器组件，用于加载三维模型并控制视角跳转，支持动态切换模型路径
<template>
  <div class="info-move-loader"></div>
</template>

<script>
import emitter from '@/eventBus';

export default {
  name: 'InfoMoveLoader',
  props: {
    viewer: {
      type: Object,
      required: true
    },
    modelPath: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      tileset: null,
      isLoading: false,
      isModelLoaded: false,
      modelPosition: null,
      lastModelUrl: '',
      tempTileset: null // 用于临时加载获取位置信息
    };
  },
  mounted() {
    emitter.on('model-path-changed', this.handleModelPathChanged);
    this.exposeMethods();
  },
  methods: {
    handleModelPathChanged(newPath) {
      if (newPath && !this.isLoading) {
        this.loadModel(newPath);
      }
    },

    async loadModel(modelUrl) {
      if (this.isLoading) return;
      
      this.isLoading = true;
      
      try {
        if (!this.$Cesium) {
          console.error('Cesium未正确注入');
          return;
        }
        
        if (!modelUrl) {
          console.error('未提供模型路径');
          return;
        }

        const Cesium = this.$Cesium;
        console.log('加载模型:', modelUrl);

        // 清理现有模型
        if (this.tileset) {
          this.viewer.scene.primitives.remove(this.tileset);
          this.tileset = null;
        }

        // 创建临时tileset来获取位置信息
        this.tempTileset = await new Promise((resolve, reject) => {
          const tileset = new Cesium.Cesium3DTileset({
            url: modelUrl,
            maximumScreenSpaceError: 32,
            skipLevelOfDetail: true,
            dynamicScreenSpaceError: false,
          });

          tileset.readyPromise
            .then(() => resolve(tileset))
            .catch(error => {
              console.error('临时Tileset加载失败:', error);
              reject(error);
            });
        });

        // 获取位置信息
        const boundingSphere = this.tempTileset.boundingSphere;
        
        // 移动相机
        await this.moveToPosition(boundingSphere);

        // 移除临时模型
        if (this.tempTileset) {
          this.viewer.scene.primitives.remove(this.tempTileset);
          this.tempTileset = null;
        }

        // 等待0.5秒
        await new Promise(resolve => setTimeout(resolve, 1200));

        // 加载正式模型
        const newTileset = await new Promise((resolve, reject) => {
          const tileset = new Cesium.Cesium3DTileset({
            url: modelUrl,
            maximumScreenSpaceError: 32,
            skipLevelOfDetail: true,
            dynamicScreenSpaceError: false,
          });

          tileset.readyPromise
            .then(() => resolve(tileset))
            .catch(error => {
              console.error('正式Tileset加载失败:', error);
              reject(error);
            });
        });

        // 保存新的tileset引用并添加到场景
        this.tileset = newTileset;
        this.viewer.scene.primitives.add(this.tileset);
        
        // 更新状态
        this.lastModelUrl = modelUrl;
        this.modelPosition = boundingSphere.center;
        this.isModelLoaded = true;

      } catch (error) {
        console.error('模型加载失败:', error);
        if (this.tileset) {
          this.viewer.scene.primitives.remove(this.tileset);
          this.tileset = null;
        }
        if (this.tempTileset) {
          this.viewer.scene.primitives.remove(this.tempTileset);
          this.tempTileset = null;
        }
        this.lastModelUrl = '';
        this.modelPosition = null;
        this.isModelLoaded = false;
      } finally {
        this.isLoading = false;
      }
    },

    async moveToPosition(boundingSphere) {
      if (!boundingSphere) return;
      
      const Cesium = this.$Cesium;
      
      try {
        await this.viewer.camera.flyToBoundingSphere(boundingSphere, {
          offset: new Cesium.HeadingPitchRange(
            Cesium.Math.toRadians(0),
            Cesium.Math.toRadians(-35),
            boundingSphere.radius * 1.5
          ),
          duration: 2
        });
      } catch (error) {
        console.error('相机移动失败:', error);
      }
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
      this.viewer.scene.primitives.remove(this.tileset);
      this.tileset = null;
    }
    if (this.tempTileset) {
      this.viewer.scene.primitives.remove(this.tempTileset);
      this.tempTileset = null;
    }
    emitter.off('model-path-changed', this.handleModelPathChanged);
  }
};
</script> 