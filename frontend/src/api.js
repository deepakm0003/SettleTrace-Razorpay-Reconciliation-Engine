import axios from 'axios';

// API Base URL - points to Vercel backend deployment
const API_BASE_URL = 'https://settle-trace-razorpay-reconciliation-engine-nv3g-elkzy365o.vercel.app';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getMetrics = async () => {
  const response = await api.get('/metrics');
  return response.data;
};

export const getExceptions = async () => {
  const response = await api.get('/exceptions');
  return response.data;
};

export const getAuditTrail = async (orderId) => {
  const response = await api.get(`/audit-trail/${orderId}`);
  return response.data;
};

export const refreshReconciliation = async () => {
  const response = await api.post('/reconcile/refresh');
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
