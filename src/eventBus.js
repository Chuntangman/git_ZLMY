// src/eventBus.js
import mitt from 'mitt'

// 创建事件总线实例
const emitter = mitt()

// 导出实例
export default emitter