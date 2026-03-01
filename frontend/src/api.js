import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Default FastAPI port
});

export const getTrades = async (skip = 0, limit = 100) => {
  const response = await api.get(`/trades?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const getSummary = async () => {
  const response = await api.get('/summary');
  return response.data;
};

export const startBot = async () => {
  return await api.post('/control/start');
};

export const stopBot = async () => {
  return await api.post('/control/stop');
};

export default api;
