import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetch reconciliation metrics
 */
export const getMetrics = async () => {
  try {
    const response = await api.get('/metrics');
    return response.data;
  } catch (error) {
    console.error('Error fetching metrics:', error);
    throw error;
  }
};

/**
 * Fetch exceptions (non-matched orders), sorted by confidence ascending
 */
export const getExceptions = async () => {
  try {
    const response = await api.get('/exceptions');
    return response.data;
  } catch (error) {
    console.error('Error fetching exceptions:', error);
    throw error;
  }
};

/**
 * Fetch full audit trail for a specific order
 */
export const getAuditTrail = async (orderId) => {
  try {
    const response = await api.get(`/audit-trail/${orderId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching audit trail for ${orderId}:`, error);
    throw error;
  }
};

/**
 * Refresh reconciliation (clear cache, rerun pipeline)
 */
export const refreshReconciliation = async () => {
  try {
    const response = await api.post('/reconcile/refresh');
    return response.data;
  } catch (error) {
    console.error('Error refreshing reconciliation:', error);
    throw error;
  }
};

export default api;
