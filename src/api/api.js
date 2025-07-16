import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('发送请求:', config.url, config.params);
    return config;
  },
  error => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('收到响应:', response.data);
    return response;
  },
  error => {
    console.error('响应错误:', error);
    return Promise.reject(error);
  }
);

export default {
  getRockDetail(id) {
    return api.get(`/geo/rocks/${id}`);
  },
  
  getGeoJsonData() {
    return api.get('/geo/geojson');
  },

  // 获取关联岩石信息
  getRelatedRockInfo(number) {
    console.log('调用getRelatedRockInfo, number:', number);
    return api.get(`/related-rock/${number}`);
  }
};

//岩石样品关联
export const getRelations = async (entityId) => {
    try {
        const response = await api.get(`/relations/${entityId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching relations:', error);
        throw error;
    }
};

//岩石样品-基本信息
export const getRockSampleDetails = async (sampleId) => {
    try {
        const response = await api.get(`/rock-sample/${sampleId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching rock sample details:', error);
        throw error;
    }
};

//薄片鉴定报告
export const getThinSectionDetails = async (sampleId) => {
    try {
        const response = await api.get(`/thin-section/${sampleId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching thin section details:', error);
        throw error;
    }
};

//XRF测试结果
export const getXRFTestResults = async (sampleId) => {
    try {
        const response = await api.get(`/xrf-test/${sampleId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching XRF test results:', error);
        throw error;
    }
};

//三维模型数据
export const get3DModels = async () => {
    try {
        const response = await api.get(`/3d-models`);
        return response.data;
    } catch (error) {
        console.error('Error fetching 3D models:', error);
        throw error;
    }
};

export const get3DModelById = async (modelId) => {
    try {
        const response = await api.get(`/3d-models/${modelId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching 3D model details:', error);
        throw error;
    }
};

export async function get3DModelDetails(modelId) {
  try {
    console.log('Fetching 3D model details for ID:', modelId);
    const response = await fetch(`http://localhost:5000/api/3d-models/${modelId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Received raw data:', data);
    
    // 处理媒体文件数据
    if (data.media_files) {
      data.media_files = data.media_files.map(media => {
        const type = media.type?.toLowerCase() || '';
        return {
          ...media,
          type,
          isImage: ['png', 'jpg', 'jpeg'].includes(type),
          isVideo: type === 'mp4'
        };
      });
      console.log('Processed media files:', data.media_files);
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching 3D model details:', error);
    throw error;
  }
}

// 岩石标本查询相关API
export const rockSampleApi = {
  // 获取岩石标本列表（带过滤）
  getRockSamples: async (filters = {}) => {
    try {
      const response = await api.get('/rock-samples', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching rock samples:', error);
      throw error;
    }
  },

  // 获取过滤选项
  getFilterOptions: async () => {
    try {
      const response = await api.get('/rock-samples/filters');
      return response.data;
    } catch (error) {
      console.error('Error fetching filter options:', error);
      throw error;
    }
  }
};

// AI Chat API 配置
const AI_API_BASE_URL = '/api/dify';  // 使用代理URL
const AI_API_KEY = 'app-0N3NXK5QifxHob782Pm3nadw';

// 创建专用的axios实例
const aiAxios = axios.create({
  baseURL: AI_API_BASE_URL,
  timeout: 30000, // 增加超时时间到30秒
  headers: {
    'Authorization': `Bearer ${AI_API_KEY}`,
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
  }
});

// AI聊天相关API
export const aiApi = {
  // 测试连接
  testConnection: async () => {
    try {
      const response = await aiAxios.post('/chat-messages', {
        inputs: {},
        query: "Hello, this is a test message",
        response_mode: "blocking",
        user: "test-user-" + Date.now(),
      });
      console.log('API连接测试成功:', response.data);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('API连接测试失败:', error.response?.data || error.message);
      return {
        success: false,
        error: error.response?.data || error.message
      };
    }
  },

  // 发送聊天消息
  sendChatMessage: async (message, conversationId = '') => {
    try {
      console.log('Sending message:', {
        message,
        conversationId,
        url: `${AI_API_BASE_URL}/chat-messages`
      });

      const response = await aiAxios.post('/chat-messages', {
        inputs: {},
        query: message,
        response_mode: "blocking", // 暂时使用阻塞模式进行测试
        conversation_id: conversationId,
        user: "user-" + Date.now(),
      });

      console.log('Response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw error;
    }
  },

  // 上传文件（如果需要的话）
  uploadFile: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${AI_API_BASE_URL}/files/upload`, formData, {
        headers: {
          'Authorization': `Bearer ${AI_API_KEY}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  }
};