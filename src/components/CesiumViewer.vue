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
            coordinates: null,
            drawingHandler: null,
            currentDrawingMode: null,
            currentPoints: null, // 用于存储绘制中的点
            currentEntity: null // 用于存储绘制中的实体
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

        // 监听环境设置相关事件
        emitter.on('start-drawing', ({ tool, style }) => {
            this.startDrawing(tool, style);
        });

        emitter.on('stop-drawing', () => {
            this.stopDrawing();
        });

        emitter.on('clear-annotations', () => {
            this.clearAnnotations();
        });

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
        },
        
        // 开始绘制
        startDrawing(tool, style) {
            this.cleanupDrawingEvents();
            this.currentDrawingMode = tool;
            
            const Cesium = this.$Cesium;
            this.drawingHandler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);
            
            // 处理点击事件
            this.drawingHandler.setInputAction((click) => {
                const cartesian = this.viewer.camera.pickEllipsoid(
                    click.position,
                    this.viewer.scene.globe.ellipsoid
                );
                
                if (!cartesian) return;
                
                switch (tool) {
                    case 'billboard':
                        this.viewer.entities.add({
                            position: cartesian,
                            billboard: {
                                image: `/images/${style.image}.png`,
                                scale: style.scale,
                                color: Cesium.Color.fromCssColorString(style.color)
                            }
                        });
                        break;
                        
                    case 'label':
                        this.viewer.entities.add({
                            position: cartesian,
                            label: {
                                text: style.text || '标签',
                                font: `${style.fontSize}px sans-serif`,
                                fillColor: Cesium.Color.fromCssColorString(style.color),
                                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                                outlineWidth: 2,
                                verticalOrigin: Cesium.VerticalOrigin.BOTTOM
                            }
                        });
                        break;
                        
                    case 'polyline':
                        if (!this.currentPoints) this.currentPoints = [];
                        this.currentPoints.push(cartesian);
                        
                        if (this.currentPoints.length > 1) {
                            if (this.currentEntity) {
                                this.viewer.entities.remove(this.currentEntity);
                            }
                            this.currentEntity = this.viewer.entities.add({
                                polyline: {
                                    positions: this.currentPoints,
                                    width: style.width,
                                    material: new Cesium.PolylineDashMaterialProperty({
                                        color: Cesium.Color.fromCssColorString(style.color),
                                        dashLength: style.style === 'dashed' ? 16.0 : 0.0
                                    })
                                }
                            });
                        }
                        break;
                        
                    case 'polygon':
                        if (!this.currentPoints) this.currentPoints = [];
                        this.currentPoints.push(cartesian);
                        
                        if (this.currentPoints.length > 2) {
                            if (this.currentEntity) {
                                this.viewer.entities.remove(this.currentEntity);
                            }
                            this.currentEntity = this.viewer.entities.add({
                                polygon: {
                                    hierarchy: new Cesium.PolygonHierarchy(this.currentPoints),
                                    material: Cesium.Color.fromCssColorString(style.color).withAlpha(style.alpha),
                                    outline: true,
                                    outlineColor: Cesium.Color.WHITE,
                                    outlineWidth: style.outlineWidth
                                }
                            });
                        }
                        break;
                }
            }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
            
            // 添加鼠标移动事件用于实时预览
            if (tool === 'polyline' || tool === 'polygon') {
                this.drawingHandler.setInputAction((movement) => {
                    if (!this.currentPoints || this.currentPoints.length === 0) return;
                    
                    const cartesian = this.viewer.camera.pickEllipsoid(
                        movement.endPosition,
                        this.viewer.scene.globe.ellipsoid
                    );
                    
                    if (!cartesian) return;
                    
                    if (this.currentEntity) {
                        const positions = [...this.currentPoints, cartesian];
                        if (tool === 'polyline') {
                            this.currentEntity.polyline.positions = positions;
                        } else {
                            this.currentEntity.polygon.hierarchy = new Cesium.PolygonHierarchy(positions);
                        }
                    }
                }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
            }
        },

        // 停止绘制
        stopDrawing() {
            this.cleanupDrawingEvents();
            this.currentPoints = null;
            this.currentEntity = null;
            this.currentDrawingMode = null;
        },

        // 清除所有标注
        clearAnnotations() {
            this.viewer.entities.removeAll();
            this.currentPoints = null;
            this.currentEntity = null;
        },

        // 清理绘制事件
        cleanupDrawingEvents() {
            if (this.drawingHandler) {
                this.drawingHandler.destroy();
                this.drawingHandler = null;
            }
        }
    },
    beforeUnmount() {
        this.cleanupDrawingEvents();
        if (this.viewer && !this.viewer.isDestroyed) {
            this.viewer.destroy();
        }
        // 移除事件监听
        emitter.off('start-drawing');
        emitter.off('stop-drawing');
        emitter.off('clear-annotations');
        emitter.off('load-geological-corridor');
    }
}
</script>

<style scoped>
#cesiumContainer {
    width: 100%;
    height: 100%;
    position: relative;
    z-index: 1; /* 添加较低的z-index */
}

.coordinates-display {
    position: absolute;
    bottom: 20px;
    right: 20px;
    background-color: rgba(255, 255, 255, 0.5);
    padding: 10px 15px;
    border-radius: 8px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    z-index: 2; /* 确保坐标显示在地图上方但在AI下方 */
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