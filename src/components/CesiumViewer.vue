// Cesium地图容器组件，用于加载和显示三维地图，支持鼠标移动显示坐标，点击事件处理，以及加载地质走廊相关组件
<template>
    <div id="cesiumContainer">
        <div v-if="coordinates" class="coordinates-display">
            <div class="coordinate-item">
                <span class="coordinate-label">经度:</span>
                <span class="coordinate-value">{{ coordinates.longitude.toFixed(6) }}°</span>
            </div>
            <div class="coordinate-item">
                <span class="coordinate-label">纬度:</span>
                <span class="coordinate-value">{{ coordinates.latitude.toFixed(6) }}°</span>
            </div>
        </div>
        <geo-json-loader v-if="showGeologicalCorridor" ref="geoJsonLoader" :viewer="viewer" />
        <model-loader v-if="showGeologicalCorridor" ref="modelLoader" :viewer="viewer" />
        <bottom-sidebar />
    </div>
</template>

<script>
import emitter from '@/eventBus'
import GeoJsonLoader from './GeoJsonLoader.vue'
import ModelLoader from './ModelLoader.vue'
import BottomSidebar from './Bottom_sidebar.vue'

export default {
    name: 'cesiumViewer',
    components: {
        ModelLoader,
        GeoJsonLoader,
        BottomSidebar,
    },
    data() {
        return {
            viewer: null,
            showGeologicalCorridor: false,
            coordinates: null
        }
    },
    mounted() {
        // 通过全局属性访问Cesium
        const Cesium = this.$Cesium;
        this.viewer = new Cesium.Viewer('cesiumContainer', {
            infoBox: false,                 // 信息框
            animation: false,  // 时间线动画控制
            timeline: false,   // 时间线显示
        });
        this.viewer._cesiumWidget._creditContainer.style.display = 'none';

        // 初始化完成后触发事件
        this.$emit('viewer-ready', this.viewer);

        // 添加鼠标移动事件监听
        this.viewer.screenSpaceEventHandler.setInputAction(
            (movement) => {
                const cartesian = this.viewer.camera.pickEllipsoid(movement.endPosition, this.viewer.scene.globe.ellipsoid);
                if (cartesian) {
                    const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
                    const longitude = Cesium.Math.toDegrees(cartographic.longitude);
                    const latitude = Cesium.Math.toDegrees(cartographic.latitude);
                    this.coordinates = { longitude, latitude };
                } else {
                    this.coordinates = null;
                }
            },
            Cesium.ScreenSpaceEventType.MOUSE_MOVE
        );

        // 正确的事件监听
        emitter.on('load-geological-corridor', (show = true) => {
            this.showGeologicalCorridor = show;
            this.$nextTick(() => {
                this.$refs.modelLoader?.loadModel();
                this.$refs.geoJsonLoader?.loadGeoJson();
            });
        });
        // 监听点击事件
        this.viewer.screenSpaceEventHandler.setInputAction(
            (click) => {
                const pickedObject = this.viewer.scene.pick(click.position);
                if (pickedObject) {
                    this.$emit('feature-clicked', pickedObject);
                } else {
                    this.$emit('click-blank');
                    // 发送关闭露头抽屉的事件
                    emitter.emit('close-lutou-drawer');
                }
            },
            Cesium.ScreenSpaceEventType.LEFT_CLICK
        );
    },
    methods: {
        onClick(click) {
            const pickedObject = this.viewer.scene.pick(click.position);
            if (!pickedObject) {
                this.$emit('click-blank');
                // 这里也添加关闭事件
                emitter.emit('close-lutou-drawer');
            }
        }
    },
    beforeUnmount() {
        if (this.viewer && !this.viewer.isDestroyed) {
            this.viewer.destroy();
        }
        emitter.off('load-geological-corridor');
    }
}
</script>

<style scoped>
#cesiumContainer {
    width: 100%;
    height: 100%;
    position: relative;
}

.coordinates-display {
    position: absolute;
    bottom: 20px;
    right: 20px; /* 改为右下角 */
    background-color: rgba(255, 255, 255, 0.5); /* 改为白色背景，50%透明度 */
    padding: 10px 15px;
    border-radius: 8px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    z-index: 999;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.coordinate-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.coordinate-label {
    color: #666;
    font-size: 13px;
}

.coordinate-value {
    color: #333;
    font-weight: 500;
    font-size: 13px;
}
</style>