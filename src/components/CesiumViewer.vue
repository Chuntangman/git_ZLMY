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
            currentEntity: null, // 用于存储绘制中的实体
            particleSystem: null,
            flightAnimations: [],
            meteorSystem: null,
            waterMaterial: null,
            rotationEnabled: true,
            rotationEventHandler: null
        }
    },
    mounted() {
        // 通过全局属性访问Cesium
        const Cesium = this.$Cesium;
        this.viewer = new Cesium.Viewer('cesiumContainer', {
            infoBox: false,
            animation: false,
            timeline: false,
            terrainProvider: Cesium.createWorldTerrain(),
            scene3DOnly: true,
            baseLayerPicker: false,
            navigationHelpButton: false,
            fullscreenButton: false,
            geocoder: false,
            homeButton: false,
            sceneModePicker: false,
            selectionIndicator: false,
            requestRenderMode: true,
            maximumRenderTimeChange: Infinity
        });

        // 隐藏版权信息
        this.viewer._cesiumWidget._creditContainer.style.display = 'none';

        // 初始化地球特效
        this.initializeEarthEffects();

        // 设置炫酷的初始相机动画
        this.setupInitialCameraAnimation();

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

        // 监听特效更新事件
        emitter.on('update-effect', (effectType, enabled) => {
            this.updateEffect(effectType, enabled);
        });

        // 设置场景质量
        this.viewer.scene.postProcessStages.fxaa.enabled = true;
        this.viewer.scene.globe.maximumScreenSpaceError = 1.0;
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
        },

        setupInitialCameraAnimation() {
            const Cesium = this.$Cesium;
            
            // 设置初始位置（远距离）
            this.viewer.camera.setView({
                destination: Cesium.Cartesian3.fromDegrees(114.3, 30.6, 20000000.0), // 武汉上空远点
                orientation: {
                    heading: Cesium.Math.toRadians(0.0),
                    pitch: Cesium.Math.toRadians(-85.0),
                    roll: 0.0
                }
            });

            // 添加大气发光效果
            this.viewer.scene.globe.enableLighting = true;
            this.viewer.scene.globe.atmosphereLighting = true;

            // 创建相机飞行动画
            setTimeout(() => {
                // 定义飞行路径点
                const flightPath = [
                    {
                        destination: Cesium.Cartesian3.fromDegrees(114.3, 30.6, 10000000.0),
                        orientation: {
                            heading: Cesium.Math.toRadians(-45.0),
                            pitch: Cesium.Math.toRadians(-55.0),
                            roll: 0.0
                        },
                        duration: 3.0
                    },
                    {
                        destination: Cesium.Cartesian3.fromDegrees(114.3, 30.6, 10000000.0),
                        orientation: {
                            heading: Cesium.Math.toRadians(-45.0),
                            pitch: Cesium.Math.toRadians(-65.0),
                            roll: 0.0
                        },
                        duration: 3.0
                    },
                    {
                        destination: Cesium.Cartesian3.fromDegrees(114.3, 30.6, 500000.0),
                        orientation: {
                            heading: Cesium.Math.toRadians(0.0),
                            pitch: Cesium.Math.toRadians(-75.0),
                            roll: 0.0
                        },
                        duration: 2.0
                    },
                    {
                        // 蔡甸区坐标（114.0294, 30.5844）
                        destination: Cesium.Cartesian3.fromDegrees(114.0294, 30.5844, 100000.0),
                        orientation: {
                            heading: Cesium.Math.toRadians(-30.0), // 稍微调整视角以更好地观察蔡甸区
                            pitch: Cesium.Math.toRadians(-85.0),
                            roll: 0.0
                        },
                        duration: 3.0
                    },
                    {
                        // 最终降低高度，提供更好的观察视角
                        destination: Cesium.Cartesian3.fromDegrees(114.0294, 30.5844, 30000.0),
                        orientation: {
                            heading: Cesium.Math.toRadians(-30.0),
                            pitch: Cesium.Math.toRadians(-85.0),
                            roll: 0.0
                        },
                        duration: 2.0
                    }
                ];

                // 执行连续飞行
                const flyToSequence = (index) => {
                    if (index >= flightPath.length) {
                        // 所有飞行完成，不再启动旋转
                        return;
                    }

                    const point = flightPath[index];
                    this.viewer.camera.flyTo({
                        destination: point.destination,
                        orientation: point.orientation,
                        duration: point.duration,
                        complete: () => {
                            // 延迟一小段时间后开始下一段飞行
                            setTimeout(() => {
                                flyToSequence(index + 1);
                            }, 500);
                        }
                    });
                };

                // 开始飞行序列
                flyToSequence(0);
            }, 1000);
        },

        // 移除 startSlowRotation 方法的调用，因为我们不再需要旋转效果
        startSlowRotation() {
            // 保留方法但不执行任何操作，以防其他地方还在调用
        },

        initializeEarthEffects() {
            const Cesium = this.$Cesium;
            
            // 设置默认视角（已移至setupInitialCameraAnimation）

            // 启用地形阴影
            this.viewer.scene.globe.enableLighting = true;
            this.viewer.scene.globe.shadows = Cesium.ShadowMode.ENABLED;

            // 启用大气效果
            this.viewer.scene.globe.enableLighting = true;
            this.viewer.scene.globe.atmosphereLighting = true;
            this.viewer.scene.globe.atmosphereHueShift = 0.0;
            this.viewer.scene.globe.atmosphereSaturationShift = 0.0;
            this.viewer.scene.globe.atmosphereBrightnessShift = 0.0;

            // 初始化水体材质
            this.waterMaterial = new Cesium.Material({
                fabric: {
                    type: 'Water',
                    uniforms: {
                        normalMap: '/cesium/Assets/Textures/waterNormals.jpg',
                        frequency: 1000.0,
                        animationSpeed: 0.01,
                        amplitude: 10.0,
                        specularIntensity: 5.0,
                        baseWaterColor: new Cesium.Color(0.2, 0.3, 0.6, 1.0)
                    }
                }
            });

            // 初始化粒子系统
            this.initializeParticleSystem();
        },

        initializeParticleSystem() {
            const Cesium = this.$Cesium;
            
            // 创建流星效果
            this.meteorSystem = new Cesium.ParticleSystem({
                image: '/images/particle.png',
                startScale: 1.0,
                endScale: 0.0,
                minimumParticleLife: 1.0,
                maximumParticleLife: 3.0,
                minimumSpeed: 100.0,
                maximumSpeed: 200.0,
                imageSize: new Cesium.Cartesian2(25, 25),
                emissionRate: 5.0,
                lifetime: 16.0,
                emitter: new Cesium.CircleEmitter(0.5),
                modelMatrix: Cesium.Matrix4.fromTranslation(
                    Cesium.Cartesian3.fromDegrees(116.413384, 39.910925, 100000.0)
                )
            });
        },

        updateEffect(effectType, enabled) {
            const Cesium = this.$Cesium;
            
            switch(effectType) {
                case 'sunLighting':
                    this.viewer.scene.globe.enableLighting = enabled;
                    this.viewer.scene.globe.dynamicAtmosphereLighting = enabled;
                    this.viewer.scene.globe.dynamicAtmosphereLightingFromSun = enabled;
                    break;
                    
                case 'atmosphere':
                    this.viewer.scene.skyAtmosphere.show = enabled;
                    this.viewer.scene.globe.showGroundAtmosphere = enabled;
                    if (enabled) {
                        this.viewer.scene.skyAtmosphere.brightnessShift = 0.2;
                        this.viewer.scene.skyAtmosphere.hueShift = 0.0;
                        this.viewer.scene.skyAtmosphere.saturationShift = 0.1;
                    }
                    break;
                    
                case 'terrainShadows':
                    this.viewer.scene.globe.enableLighting = enabled;
                    this.viewer.scene.globe.shadows = enabled ? 
                        Cesium.ShadowMode.ENABLED : Cesium.ShadowMode.DISABLED;
                    this.viewer.shadowMap.enabled = enabled;
                    if (enabled) {
                        this.viewer.shadowMap.darkness = 0.3;
                        this.viewer.scene.globe.terrainExaggeration = 1.1;
                    } else {
                        this.viewer.scene.globe.terrainExaggeration = 1.0;
                    }
                    break;
                    
                case 'particleEffects':
                    if (enabled) {
                        this.viewer.scene.primitives.add(this.meteorSystem);
                        // 增强粒子效果
                        this.meteorSystem.emissionRate = 10.0;
                        this.meteorSystem.startScale = 1.5;
                        this.meteorSystem.minimumParticleLife = 1.5;
                        this.meteorSystem.maximumParticleLife = 4.0;
                    } else {
                        this.viewer.scene.primitives.remove(this.meteorSystem);
                    }
                    break;
                    
                case 'flightAnimations':
                    if (enabled) {
                        this.startFlightAnimations();
                    } else {
                        this.stopFlightAnimations();
                    }
                    break;
                
                case 'waterEffect':
                    if (enabled) {
                        this.viewer.scene.globe.enableLighting = true;
                        this.viewer.scene.globe.oceanNormalMapUrl = '/cesium/Assets/Textures/waterNormals.jpg';
                        this.viewer.scene.globe.showWaterEffect = true;
                        this.viewer.scene.globe.baseWaterColor = new Cesium.Color(0.2, 0.3, 0.6, 1.0);
                        this.viewer.scene.globe.oceanNormalMapUrl = '/cesium/Assets/Textures/waterNormals.jpg';
                        this.viewer.scene.globe.specularMap = '/cesium/Assets/Textures/earthspec1k.jpg';
                        this.viewer.scene.globe.showWaterEffect = true;
                        this.viewer.scene.globe.waterFrequency = 1000.0;
                        this.viewer.scene.globe.waterAnimationSpeed = 0.01;
                    } else {
                        this.viewer.scene.globe.showWaterEffect = false;
                    }
                    break;

                case 'highQualityTextures':
                    if (enabled) {
                        this.viewer.scene.globe.maximumScreenSpaceError = 1.0;
                        this.viewer.scene.globe.tileCacheSize = 1000;
                        this.viewer.scene.globe.maximumLevel = 19;
                        this.viewer.scene.globe.baseColor = Cesium.Color.BLACK;
                        this.viewer.scene.globe.enableLighting = true;
                        this.viewer.scene.globe.atmosphereLighting = true;
                        this.viewer.scene.postProcessStages.fxaa.enabled = true;
                        this.viewer.scene.globe.showGroundAtmosphere = true;
                        this.viewer.scene.globe.atmosphereHueShift = 0.0;
                        this.viewer.scene.globe.atmosphereSaturationShift = 0.1;
                        this.viewer.scene.globe.atmosphereBrightnessShift = 0.2;
                    } else {
                        this.viewer.scene.globe.maximumScreenSpaceError = 2.0;
                        this.viewer.scene.globe.tileCacheSize = 100;
                        this.viewer.scene.globe.maximumLevel = 15;
                        this.viewer.scene.postProcessStages.fxaa.enabled = false;
                    }
                    break;
            }
        },

        startFlightAnimations() {
            const Cesium = this.$Cesium;
            
            // 创建一个简单的飞行路径动画
            const position = Cesium.Cartesian3.fromDegrees(
                116.413384, 39.910925, 10000.0
            );
            
            const entity = this.viewer.entities.add({
                position: position,
                model: {
                    uri: '/models/airplane.glb',
                    minimumPixelSize: 128,
                    maximumScale: 20000
                },
                path: {
                    resolution: 1,
                    material: new Cesium.PolylineGlowMaterialProperty({
                        glowPower: 0.1,
                        color: Cesium.Color.YELLOW
                    }),
                    width: 10
                }
            });

            this.flightAnimations.push(entity);
            
            // 设置相机跟随
            this.viewer.trackedEntity = entity;
        },

        stopFlightAnimations() {
            // 停止所有飞行动画
            this.flightAnimations.forEach(entity => {
                this.viewer.entities.remove(entity);
            });
            this.flightAnimations = [];
            this.viewer.trackedEntity = undefined;
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
        emitter.off('update-effect');
        
        // 清理相机动画
        if (this.rotationEventHandler) {
            this.viewer.scene.preUpdate.removeEventListener(this.rotationEventHandler);
        }
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