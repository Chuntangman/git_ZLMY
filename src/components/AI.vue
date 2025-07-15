<template>
    <!-- 可拖动的AI图标 -->
    <div 
        class="ai-icon" 
        :style="{ left: position.x + 'px', top: position.y + 'px' }"
        @mousedown="startDrag"
        @click="handleClick"
        :class="{ 'is-dragging': isDragging, 'is-open': isOpen }"
    >
        <div class="ai-icon-inner">
            <img 
                :src="connectionError || isLoading ? '/images/Loading_Dots_Blue.gif' : '/images/AI_Loop_Loader.gif'" 
                alt="AI Icon"
                class="ai-icon-image"
            />
        </div>
    </div>

    <!-- 对话框 -->
    <div v-if="isOpen" 
        class="ai-chat-container" 
        :class="{ 'chat-visible': isOpen }"
        :style="{ left: chatPosition.x + 'px', top: chatPosition.y + 'px' }"
        ref="chatContainer"
    >
        <div class="chat-header" @mousedown="startChatDrag">
            <div class="chat-title">
                智能地质助手
                <span class="connection-status" :class="{ 'connected': !connectionError }">
                    {{ connectionError ? '未连接' : '已连接' }}
                </span>
            </div>
            <!-- 移除重复的工具按钮 -->
            <div class="header-buttons">
                <button class="test-button" @click="testConnection" :disabled="isLoading">
                    测试连接
                </button>
                <button class="close-button" @click="toggleChat">×</button>
            </div>
        </div>
        
        <!-- 历史记录侧边栏 -->
        <div class="history-sidebar" :class="{ 'history-visible': showHistory }">
            <div class="history-header">
                <h3>历史记录</h3>
                <button class="clear-history" @click="clearHistory">清空历史</button>
            </div>
            <div class="history-list">
                <div v-for="(chat, index) in chatHistory" 
                    :key="index" 
                    class="history-item"
                    @click="loadChatHistory(chat)"
                >
                    <div class="history-item-title">{{ chat.title || '对话 ' + (index + 1) }}</div>
                    <div class="history-item-time">{{ chat.time }}</div>
                </div>
            </div>
        </div>

        <!-- 主聊天区域 -->
        <div class="chat-content" :class="{ 'with-history': showHistory }">
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

            <!-- 在 template 中的工具按钮部分 -->
            <div class="chat-input-container">
                <div class="chat-tools">
                    <button class="tool-button" title="语音输入（开发中）" disabled>
                        <font-awesome-icon :icon="['fas', 'microphone']" />
                    </button>
                    <button class="tool-button" title="上传文件（开发中）" disabled>
                        <font-awesome-icon :icon="['fas', 'file-upload']" />
                    </button>
                    <span class="divider"></span>
                    <button class="tool-button history-toggle" @click="toggleHistory" :class="{ 'active': showHistory }" title="历史记录">
                        <font-awesome-icon :icon="['fas', 'history']" />
                    </button>
                </div>
                <div class="chat-input">
                    <textarea 
                        v-model="userInput"
                        @keydown.enter.prevent="sendMessage"
                        placeholder="请输入您的问题..."
                        rows="1"
                        ref="inputArea"
                    ></textarea>
                    <button class="send-button" @click="sendMessage">
                        发送
                    </button>
                </div>
            </div>
        </div>

        <!-- 调整大小的边框 -->
        <div class="resize-handle resize-n" @mousedown="startResize('n', $event)"></div>
        <div class="resize-handle resize-e" @mousedown="startResize('e', $event)"></div>
        <div class="resize-handle resize-s" @mousedown="startResize('s', $event)"></div>
        <div class="resize-handle resize-w" @mousedown="startResize('w', $event)"></div>
        <div class="resize-handle resize-nw" @mousedown="startResize('nw', $event)"></div>
        <div class="resize-handle resize-ne" @mousedown="startResize('ne', $event)"></div>
        <div class="resize-handle resize-sw" @mousedown="startResize('sw', $event)"></div>
        <div class="resize-handle resize-se" @mousedown="startResize('se', $event)"></div>
    </div>
</template>

<script>
import { aiApi } from '@/api/api';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

export default {
    name: 'AI',
    components: {
        FontAwesomeIcon
    },
    data() {
        return {
            position: {
                x: window.innerWidth - 200,
                y: window.innerHeight - 200
            },
            chatPosition: {
                x: window.innerWidth - 500,
                y: 100
            },
            chatSize: {
                width: 450,
                height: 600
            },
            isDragging: false,
            isResizing: false,
            resizeDirection: '',
            dragOffset: {
                x: 0,
                y: 0
            },
            isOpen: false,
            messages: [{
                type: 'ai',
                text: '你好！我是你的小助手，无论你对岩石的种类、地层的结构，还是矿物的成分和形成过程感兴趣，我都可以为你提供详细的解答。请告诉我你想了解的内容，或者你是否有具体的问题？'
            }],
            userInput: '',
            dragStartTime: 0,
            isLoading: false,
            currentConversationId: '',
            eventSource: null,
            connectionError: false,
            showHistory: false,
            chatHistory: [],
            currentChatId: null,
            isDraggingChat: false,  // 新增：专门用于对话框拖动的状态
        }
    },
    watch: {
        // 监听对话框位置变化
        chatPosition: {
            handler(newPos) {
                // 确保对话框不会超出屏幕边界
                if (newPos.x < 0) this.chatPosition.x = 0;
                if (newPos.y < 0) this.chatPosition.y = 0;
                if (newPos.x + this.chatSize.width > window.innerWidth) {
                    this.chatPosition.x = window.innerWidth - this.chatSize.width;
                }
                if (newPos.y + this.chatSize.height > window.innerHeight) {
                    this.chatPosition.y = window.innerHeight - this.chatSize.height;
                }
            },
            deep: true
        }
    },
    mounted() {
        // 设置初始位置
        this.position = {
            x: window.innerWidth - 200,  // Moved left 100px (from -100 to -200)
            y: window.innerHeight - 200  // Moved up 50px
        };
        
        // 添加全局鼠标事件监听
        document.addEventListener('mousemove', this.onDrag)
        document.addEventListener('mousemove', this.onResize)
        document.addEventListener('mouseup', this.stopDrag)
        document.addEventListener('mouseup', this.stopResize)
        // 添加窗口大小变化监听
        window.addEventListener('resize', this.handleResize)

        // 确保组件可见性
        console.log('AI Component mounted at position:', this.position);
        
        // 组件加载时测试连接
        this.testConnection();
        
        // 加载历史记录
        this.loadChatHistoryFromStorage()
    },
    beforeUnmount() {
        // 移除事件监听
        document.removeEventListener('mousemove', this.onDrag)
        document.removeEventListener('mousemove', this.onResize)
        document.removeEventListener('mouseup', this.stopDrag)
        document.removeEventListener('mouseup', this.stopResize)
        window.removeEventListener('resize', this.handleResize)
        if (this.eventSource) {
            this.eventSource.close();
        }
    },
    methods: {
        handleResize() {
            // 当窗口大小改变时，确保图标保持在右下角
            if (!this.isDragging) {
                this.position = {
                    x: window.innerWidth - 200,  // Moved left 100px (from -100 to -200)
                    y: window.innerHeight - 200  // Moved up 50px
                }
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
            // 确保只有点击AI图标时才触发
            if (!e.target.closest('.ai-icon')) return;
            
            this.dragStartTime = new Date().getTime();
            this.isDragging = true;
            const rect = e.target.getBoundingClientRect();
            this.dragOffset = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            e.stopPropagation(); // 阻止事件冒泡
        },

        onDrag(e) {
            // 分别处理AI图标和对话框的拖动
            if (this.isDragging) {
                // AI图标拖动逻辑
                const newX = e.clientX - this.dragOffset.x;
                const newY = e.clientY - this.dragOffset.y;
                
                // 限制在窗口范围内
                this.position = {
                    x: Math.max(0, Math.min(window.innerWidth - 180, newX)),
                    y: Math.max(0, Math.min(window.innerHeight - 180, newY))
                };
            } else if (this.isDraggingChat) {
                // 对话框拖动逻辑
                const newX = e.clientX - this.dragOffset.x;
                const newY = e.clientY - this.dragOffset.y;
                
                // 限制在窗口范围内
                this.chatPosition = {
                    x: Math.max(0, Math.min(window.innerWidth - this.chatSize.width, newX)),
                    y: Math.max(0, Math.min(window.innerHeight - this.chatSize.height, newY))
                };
            }
        },

        stopDrag() {
            if (this.isDragging || this.isDraggingChat) {
                this.isDragging = false;
                this.isDraggingChat = false;
                
                // 移除拖动遮罩
                const overlay = document.getElementById('drag-overlay');
                if (overlay) {
                    overlay.remove();
                }
            }
        },

        toggleChat() {
            this.isOpen = !this.isOpen
        },
        startChatDrag(e) {
            // 如果正在调整大小，不启动拖动
            if (this.isResizing) return;
            
            // 确保只在点击header时才触发拖动
            if (!e.target.closest('.chat-header')) return;
            
            // 如果点击的是按钮，不触发拖动
            if (e.target.closest('button')) return;
            
            this.isDraggingChat = true;
            const rect = this.$refs.chatContainer.getBoundingClientRect();
            this.dragOffset = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            
            // 添加临时遮罩防止文本选择
            const overlay = document.createElement('div');
            overlay.id = 'drag-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 9999;
                cursor: move;
            `;
            document.body.appendChild(overlay);
            
            e.stopPropagation(); // 阻止事件冒泡
        },

        startResize(direction, e) {
            if (this.isResizing) return;
            
            this.isResizing = true;
            this.resizeDirection = direction;
            
            const rect = this.$refs.chatContainer.getBoundingClientRect();
            this.initialSize = {
                width: rect.width,
                height: rect.height,
                x: rect.left,
                y: rect.top,
                mouseX: e.clientX,
                mouseY: e.clientY
            };

            // 添加临时遮罩
            const overlay = document.createElement('div');
            overlay.id = 'resize-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 9999;
                cursor: ${direction}-resize;
                background: transparent;
            `;
            document.body.appendChild(overlay);
            
            document.body.style.userSelect = 'none';
            e.stopPropagation();
            e.preventDefault();
        },

        onResize(e) {
            if (!this.isResizing) return;

            const minWidth = 350;
            const minHeight = 450;
            const maxWidth = window.innerWidth - 20;
            const maxHeight = window.innerHeight - 20;

            const deltaX = e.clientX - this.initialSize.mouseX;
            const deltaY = e.clientY - this.initialSize.mouseY;

            let newWidth = this.initialSize.width;
            let newHeight = this.initialSize.height;
            let newX = this.initialSize.x;
            let newY = this.initialSize.y;

            switch (this.resizeDirection) {
                case 'e':
                    newWidth = Math.min(maxWidth, Math.max(minWidth, this.initialSize.width + deltaX));
                    break;
                case 'w':
                    const possibleWidth = this.initialSize.width - deltaX;
                    if (possibleWidth >= minWidth && possibleWidth <= maxWidth) {
                        newWidth = possibleWidth;
                        newX = this.initialSize.x + deltaX;
                    }
                    break;
                case 's':
                    newHeight = Math.min(maxHeight, Math.max(minHeight, this.initialSize.height + deltaY));
                    break;
                case 'n':
                    const possibleHeight = this.initialSize.height - deltaY;
                    if (possibleHeight >= minHeight && possibleHeight <= maxHeight) {
                        newHeight = possibleHeight;
                        newY = this.initialSize.y + deltaY;
                    }
                    break;
                case 'se':
                    newWidth = Math.min(maxWidth, Math.max(minWidth, this.initialSize.width + deltaX));
                    newHeight = Math.min(maxHeight, Math.max(minHeight, this.initialSize.height + deltaY));
                    break;
                case 'sw':
                    newHeight = Math.min(maxHeight, Math.max(minHeight, this.initialSize.height + deltaY));
                    const possibleWidthSW = this.initialSize.width - deltaX;
                    if (possibleWidthSW >= minWidth && possibleWidthSW <= maxWidth) {
                        newWidth = possibleWidthSW;
                        newX = this.initialSize.x + deltaX;
                    }
                    break;
                case 'ne':
                    newWidth = Math.min(maxWidth, Math.max(minWidth, this.initialSize.width + deltaX));
                    const possibleHeightNE = this.initialSize.height - deltaY;
                    if (possibleHeightNE >= minHeight && possibleHeightNE <= maxHeight) {
                        newHeight = possibleHeightNE;
                        newY = this.initialSize.y + deltaY;
                    }
                    break;
                case 'nw':
                    const possibleWidthNW = this.initialSize.width - deltaX;
                    const possibleHeightNW = this.initialSize.height - deltaY;
                    if (possibleWidthNW >= minWidth && possibleWidthNW <= maxWidth) {
                        newWidth = possibleWidthNW;
                        newX = this.initialSize.x + deltaX;
                    }
                    if (possibleHeightNW >= minHeight && possibleHeightNW <= maxHeight) {
                        newHeight = possibleHeightNW;
                        newY = this.initialSize.y + deltaY;
                    }
                    break;
            }

            this.$refs.chatContainer.style.width = `${newWidth}px`;
            this.$refs.chatContainer.style.height = `${newHeight}px`;
            this.chatPosition = { x: newX, y: newY };
        },

        stopResize() {
            if (!this.isResizing) return;
            
            this.isResizing = false;
            // 移除临时遮罩
            const overlay = document.getElementById('resize-overlay');
            if (overlay) {
                overlay.remove();
            }
            // 恢复文本选择
            document.body.style.userSelect = '';
        },

        toggleHistory() {
            console.log('Toggling history panel');
            this.showHistory = !this.showHistory;
        },

        saveChatToHistory() {
            const currentTime = new Date().toLocaleString();
            // 获取第一条消息的前30个字符作为标题
            const firstMessage = this.messages[0]?.text || '';
            const title = firstMessage.length > 30 ? firstMessage.slice(0, 30) + '...' : firstMessage;

            const chatData = {
                id: Date.now(),
                title: title,
                messages: [...this.messages],
                time: currentTime
            };

            this.chatHistory.unshift(chatData);
            this.saveChatHistoryToStorage();
            console.log('Chat saved to history:', chatData);
        },

        loadChatHistory(chat) {
            console.log('Loading chat history:', chat);
            this.messages = [...chat.messages];
            this.currentChatId = chat.id;
            this.showHistory = false;
        },

        clearHistory() {
            console.log('Clearing chat history');
            this.chatHistory = [];
            localStorage.removeItem('chatHistory');
        },

        saveChatHistoryToStorage() {
            try {
                localStorage.setItem('chatHistory', JSON.stringify(this.chatHistory));
                console.log('Chat history saved to storage');
            } catch (error) {
                console.error('Error saving chat history:', error);
            }
        },

        loadChatHistoryFromStorage() {
            try {
                const history = localStorage.getItem('chatHistory');
                if (history) {
                    this.chatHistory = JSON.parse(history);
                    console.log('Chat history loaded from storage:', this.chatHistory);
                }
            } catch (error) {
                console.error('Error loading chat history:', error);
            }
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

                if (response.answer) {
                    this.messages.push({
                        type: 'ai',
                        text: response.answer
                    });
                    // 确保在每次对话后保存历史记录
                    this.saveChatToHistory();
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
    z-index: 10000;
    cursor: pointer;
    user-select: none;
    transition: all 0.3s ease;
    pointer-events: auto;
}

.ai-icon-inner {
    width: 180px;  /* Increased from 60px to 180px (3x) */
    height: 180px; /* Increased from 60px to 180px (3x) */
    position: relative;
    border-radius: 50%;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s ease;
    overflow: hidden;
}

.ai-icon-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.ai-icon-inner:hover {
    transform: scale(1.1);
}

/* Remove old animations and styles */
.ai-icon-core {
    display: none;
}

.ai-icon-pulse {
    display: none;
}

.ai-chat-container {
    position: fixed;
    z-index: 9998;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    opacity: 0;
    transform: translateY(20px);
    animation: slideIn 0.3s forwards;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    min-width: 350px;
    min-height: 450px;
    user-select: none;
}

.chat-header {
    cursor: move;
    user-select: none;
    position: relative;
    z-index: 1;
    padding: 20px;
    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-title {
    font-weight: 600;
    font-size: 1.2em;
    display: flex;
    align-items: center;
    gap: 10px;
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
    background: rgba(248, 249, 250, 0.9);
    user-select: text;
}

.message {
    max-width: 85%;
    padding: 12px 16px;
    border-radius: 15px;
    font-size: 0.95em;
    line-height: 1.5;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.message.user {
    align-self: flex-end;
    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
    color: white;
    border-bottom-right-radius: 5px;
}

.message.ai {
    align-self: flex-start;
    background: white;
    color: #333;
    border-bottom-left-radius: 5px;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.chat-input-container {
    padding: 15px;
    background: white;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.chat-tools {
    display: flex;
    gap: 10px;
    padding-bottom: 10px;
}

.tool-button {
    background: none;
    border: none;
    padding: 8px;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.3s;
    color: #666;
    display: flex;
    align-items: center;
    justify-content: center;
}

.tool-button:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #1a73e8;
    transform: scale(1.1);
}

.tool-button svg {
    width: 20px;
    height: 20px;
}

.chat-input {
    display: flex;
    gap: 10px;
    align-items: flex-end;
}

textarea {
    flex: 1;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 20px;
    padding: 12px 20px;
    resize: none;
    font-family: inherit;
    font-size: 0.95em;
    line-height: 1.4;
    max-height: 120px;
    outline: none;
    transition: border-color 0.3s;
    user-select: text;
}

textarea:focus {
    border-color: #1a73e8;
}

.send-button {
    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
    border: none;
    border-radius: 20px;
    padding: 10px 20px;
    color: white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s;
}

.send-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 5px rgba(26, 115, 232, 0.2);
}

.send-icon {
    width: 24px;
    height: 24px;
    color: white;
}

/* 自定义滚动条 */
.chat-messages::-webkit-scrollbar {
    width: 5px;
}

.chat-messages::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
}

.chat-messages::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.3);
}

.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 4px 8px;
}

.typing-indicator span {
    width: 6px;
    height: 6px;
    background: #1a73e8;
    border-radius: 50%;
    animation: typing 1s infinite ease-in-out;
}

@keyframes typing {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
}

.message-content {
    white-space: pre-wrap;
    word-break: break-word;
}

.connection-status {
    font-size: 0.8em;
    margin-left: 10px;
    padding: 4px 8px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.2);
}

.connection-status.connected {
    background: rgba(76, 175, 80, 0.2);
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

/* Remove connection error style since we're using GIFs now */
.ai-icon.connection-error .ai-icon-inner {
    background: transparent;
}

/* 优化调整大小的手柄样式 */
.resize-handle {
    position: absolute;
    background: transparent;
    z-index: 2;
}

.resize-n, .resize-s {
    left: 0;
    right: 0;
    height: 12px;
    cursor: ns-resize;
}

.resize-e, .resize-w {
    top: 0;
    bottom: 0;
    width: 12px;
    cursor: ew-resize;
}

.resize-n { top: -6px; }
.resize-s { bottom: -6px; }
.resize-e { right: -6px; }
.resize-w { left: -6px; }

.resize-nw, .resize-ne, .resize-sw, .resize-se {
    width: 20px;
    height: 20px;
    background: transparent;
    position: absolute;
    z-index: 3;
}

.resize-nw { 
    top: -6px; 
    left: -6px; 
    cursor: nw-resize;
}
.resize-ne { 
    top: -6px; 
    right: -6px; 
    cursor: ne-resize;
}
.resize-sw { 
    bottom: -6px; 
    left: -6px; 
    cursor: sw-resize;
}
.resize-se { 
    bottom: -6px; 
    right: -6px; 
    cursor: se-resize;
}

/* 添加hover效果以提高可见性 */
.resize-handle:hover {
    background: rgba(26, 115, 232, 0.2);
}

/* 确保调整大小时不会选中文本 */
.ai-chat-container {
    z-index: 9997;
}

.chat-messages, .chat-input textarea {
    user-select: text;
}

/* 历史记录侧边栏样式 */
.history-sidebar {
    position: absolute;
    right: -300px;
    top: 0;
    width: 300px;
    height: 100%;
    background: rgba(255, 255, 255, 0.98);
    border-left: 1px solid rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    z-index: 10;
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
}

.history-visible {
    right: 0;
}

.history-header {
    padding: 15px;
    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.history-header h3 {
    margin: 0;
    font-size: 1.1em;
    font-weight: 500;
}

.clear-history {
    background: none;
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
    transition: all 0.3s;
}

.clear-history:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: white;
}

.history-list {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
}

.history-item {
    padding: 12px 15px;
    border-radius: 8px;
    background: rgba(248, 249, 250, 0.9);
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.3s;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.history-item:hover {
    background: rgba(26, 115, 232, 0.1);
    transform: translateY(-1px);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.history-item-title {
    font-size: 0.95em;
    color: #333;
    margin-bottom: 5px;
    font-weight: 500;
}

.history-item-time {
    font-size: 0.8em;
    color: #666;
}

/* 确保主聊天区域在历史记录打开时正确调整 */
.chat-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
    position: relative;
    z-index: 0;
}

.chat-content.with-history {
    margin-right: 300px;
}

@keyframes slideIn {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style> 