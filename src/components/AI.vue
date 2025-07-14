<template>
    <!-- 可拖动的AI图标 -->
    <div 
        class="ai-icon" 
        :style="{ left: position.x + 'px', top: position.y + 'px' }"
        @mousedown="startDrag"
        @click="handleClick"
        :class="{ 'is-dragging': isDragging, 'is-open': isOpen, 'connection-error': connectionError }"
    >
        <div class="ai-icon-inner">
            <div class="ai-icon-pulse"></div>
            <div class="ai-icon-core"></div>
        </div>
    </div>

    <!-- 对话框 -->
    <div v-if="isOpen" class="ai-chat-container" :class="{ 'chat-visible': isOpen }">
        <div class="chat-header">
            <div class="chat-title">
                AI Assistant
                <span class="connection-status" :class="{ 'connected': !connectionError }">
                    {{ connectionError ? '未连接' : '已连接' }}
                </span>
            </div>
            <div class="header-buttons">
                <button class="test-button" @click="testConnection" :disabled="isLoading">
                    测试连接
                </button>
                <button class="close-button" @click="toggleChat">×</button>
            </div>
        </div>
        
        <div class="chat-messages" ref="chatMessages">
            <div v-for="(message, index) in messages" 
                :key="index" 
                :class="['message', message.type]"
            >
                <div class="message-content" v-html="message.text"></div>
            </div>
            <div v-if="isLoading" class="message ai">
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        </div>

        <div class="chat-input">
            <textarea 
                v-model="userInput"
                @keydown.enter.prevent="sendMessage"
                placeholder="Type your message here..."
                rows="1"
                ref="inputArea"
            ></textarea>
            <button class="send-button" @click="sendMessage">
                <svg viewBox="0 0 24 24" class="send-icon">
                    <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
            </button>
        </div>
    </div>
</template>

<script>
import { aiApi } from '@/api/api';

export default {
    name: 'AI',
    data() {
        return {
            position: {
                x: 20,
                y: window.innerHeight - 100
            },
            isDragging: false,
            dragOffset: {
                x: 0,
                y: 0
            },
            isOpen: false,
            messages: [],
            userInput: '',
            dragStartTime: 0,
            isLoading: false,
            currentConversationId: '',
            eventSource: null,
            connectionError: false
        }
    },
    mounted() {
        // 设置初始位置
        this.position = {
            x: 20,
            y: window.innerHeight - 100
        };
        
        // 添加全局鼠标事件监听
        document.addEventListener('mousemove', this.onDrag)
        document.addEventListener('mouseup', this.stopDrag)
        // 添加窗口大小变化监听
        window.addEventListener('resize', this.handleResize)

        // 确保组件可见性
        console.log('AI Component mounted at position:', this.position);
        
        // 组件加载时测试连接
        this.testConnection();
    },
    beforeUnmount() {
        // 移除事件监听
        document.removeEventListener('mousemove', this.onDrag)
        document.removeEventListener('mouseup', this.stopDrag)
        window.removeEventListener('resize', this.handleResize)
        if (this.eventSource) {
            this.eventSource.close();
        }
    },
    methods: {
        handleResize() {
            // 当窗口大小改变时，确保图标保持在左下角
            if (!this.isDragging) {
                this.position.y = window.innerHeight - 100
            }
        },
        handleClick(e) {
            // 如果是拖动结束，不触发点击事件
            const dragEndTime = new Date().getTime();
            if (this.dragStartTime && (dragEndTime - this.dragStartTime) > 200) {
                return;
            }
            this.toggleChat();
        },
        startDrag(e) {
            this.dragStartTime = new Date().getTime();
            if (e.target.closest('.ai-icon')) {
                this.isDragging = true;
                const rect = e.target.getBoundingClientRect();
                this.dragOffset = {
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top
                };
            }
        },
        onDrag(e) {
            if (this.isDragging) {
                this.position = {
                    x: e.clientX - this.dragOffset.x,
                    y: e.clientY - this.dragOffset.y
                }
            }
        },
        stopDrag() {
            this.isDragging = false
        },
        toggleChat() {
            this.isOpen = !this.isOpen
        },
        async sendMessage() {
            if (!this.userInput.trim()) return;

            const userMessage = this.userInput.trim();
            this.messages.push({
                type: 'user',
                text: userMessage
            });

            this.userInput = '';
            this.isLoading = true;

            try {
                const response = await aiApi.sendChatMessage(
                    userMessage,
                    this.currentConversationId
                );

                if (response.conversation_id) {
                    this.currentConversationId = response.conversation_id;
                }

                // 处理响应
                if (response.answer) {
                    this.messages.push({
                        type: 'ai',
                        text: response.answer
                    });
                } else {
                    throw new Error('No answer in response');
                }

            } catch (error) {
                console.error('Error sending message:', error);
                this.messages.push({
                    type: 'ai',
                    text: '抱歉，发生了错误。错误信息：' + (error.response?.data?.message || error.message)
                });
            } finally {
                this.isLoading = false;
                this.$nextTick(() => {
                    const chatMessages = this.$refs.chatMessages;
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                });
            }
        },
        async testConnection() {
            this.isLoading = true;
            const result = await aiApi.testConnection();
            this.connectionError = !result.success;
            this.isLoading = false;

            if (result.success) {
                this.messages.push({
                    type: 'ai',
                    text: '连接测试成功！AI助手已准备就绪。'
                });
            } else {
                this.messages.push({
                    type: 'ai',
                    text: `连接测试失败：${result.error}`
                });
            }
        }
    }
}
</script>

<style scoped>
.ai-icon {
    position: fixed;
    z-index: 10000; /* 增加z-index确保在最顶层 */
    cursor: pointer; /* 改为 pointer 表示可点击 */
    user-select: none;
    transition: all 0.3s ease;
    pointer-events: auto;
}

.ai-icon-inner {
    width: 60px;
    height: 60px;
    position: relative;
    border-radius: 50%;
    background: linear-gradient(145deg, #2196f3, #21cbf3);
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s ease;
    opacity: 0.9; /* 添加一些透明度 */
}

.ai-icon-inner:hover {
    transform: scale(1.1);
    opacity: 1;
}

.ai-icon-core {
    width: 40px;  /* 增加内核大小 */
    height: 40px;
    background: white;
    border-radius: 50%;
    position: relative;
    animation: pulse 2s infinite;
}

.ai-icon-pulse {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: rgba(33, 150, 243, 0.4);
    animation: ripple 1.5s infinite;
}

@keyframes ripple {
    0% {
        transform: scale(1);
        opacity: 0.4;
    }
    100% {
        transform: scale(1.4);
        opacity: 0;
    }
}

@keyframes pulse {
    0% {
        transform: scale(0.95);
    }
    50% {
        transform: scale(1.05);
    }
    100% {
        transform: scale(0.95);
    }
}

.ai-chat-container {
    position: fixed;
    z-index: 9998;  /* 确保对话框也在最顶层 */
    right: 30px;
    bottom: 30px;
    width: 350px;
    height: 500px;
    background: white;
    border-radius: 20px; /* 改回正常的圆角 */
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    opacity: 0;
    transform: translateY(20px);
    animation: slideIn 0.3s forwards;
}

@keyframes slideIn {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.chat-header {
    padding: 20px;
    background: linear-gradient(145deg, #2196f3, #21cbf3);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chat-title {
    font-weight: 600;
    font-size: 1.1em;
}

.close-button {
    background: none;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    line-height: 1;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.message {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 15px;
    font-size: 0.95em;
    line-height: 1.4;
}

.message.user {
    align-self: flex-end;
    background: #2196f3;
    color: white;
    border-bottom-right-radius: 5px;
}

.message.ai {
    align-self: flex-start;
    background: #f5f5f5;
    color: #333;
    border-bottom-left-radius: 5px;
}

.chat-input {
    padding: 15px;
    border-top: 1px solid #eee;
    display: flex;
    gap: 10px;
    align-items: flex-end;
}

textarea {
    flex: 1;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 10px 15px;
    resize: none;
    font-family: inherit;
    font-size: 0.95em;
    line-height: 1.4;
    max-height: 100px;
    outline: none;
}

.send-button {
    background: #2196f3;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.3s;
}

.send-button:hover {
    background: #1976d2;
}

.send-icon {
    width: 24px;
    height: 24px;
    color: white;
}

/* 自定义滚动条样式 */
.chat-messages::-webkit-scrollbar {
    width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
    background: #555;
}

.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 4px 8px;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: #2196f3;
    border-radius: 50%;
    animation: typing 1s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.3s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

.message-content {
    white-space: pre-wrap;
    word-break: break-word;
}

.connection-status {
    font-size: 0.8em;
    margin-left: 10px;
    padding: 2px 6px;
    border-radius: 10px;
    background-color: rgba(255, 255, 255, 0.2);
}

.connection-status.connected {
    color: #4CAF50;
}

.header-buttons {
    display: flex;
    align-items: center;
    gap: 10px;
}

.test-button {
    background: none;
    border: 1px solid white;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    cursor: pointer;
    transition: all 0.3s;
}

.test-button:hover {
    background: rgba(255, 255, 255, 0.1);
}

.test-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.ai-icon.connection-error .ai-icon-inner {
    background: linear-gradient(145deg, #ff4444, #ff6b6b);
}
</style> 