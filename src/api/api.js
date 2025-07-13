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
    const response = await fetch(`http://localhost:5000/api/3d-models/${modelId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching 3D model details:', error);
    throw error;
  }
}