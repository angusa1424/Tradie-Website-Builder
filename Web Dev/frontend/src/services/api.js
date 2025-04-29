import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error);
  }
);

// Auth endpoints
export const loginUser = (email, password) => 
  api.post('/auth/login', { email, password });

export const registerUser = (userData) => 
  api.post('/auth/register', userData);

export const logoutUser = () => 
  api.post('/auth/logout');

export const getCurrentUser = () => 
  api.get('/auth/me');

// Website endpoints
export const createWebsite = (websiteData) => 
  api.post('/websites', websiteData);

export const getWebsites = () => 
  api.get('/websites');

export const getWebsite = (id) => 
  api.get(`/websites/${id}`);

export const updateWebsite = (id, websiteData) => 
  api.put(`/websites/${id}`, websiteData);

export const deleteWebsite = (id) => 
  api.delete(`/websites/${id}`);

export const publishWebsite = (id) => 
  api.post(`/websites/${id}/publish`);

// Template endpoints
export const getTemplates = () => 
  api.get('/templates');

export const getTemplate = (id) => 
  api.get(`/templates/${id}`);

// Analytics endpoints
export const getWebsiteAnalytics = (websiteId) => 
  api.get(`/analytics/websites/${websiteId}`);

// User settings endpoints
export const updateUserSettings = (settings) => 
  api.put('/users/settings', settings);

export const updateUserProfile = (profile) => 
  api.put('/users/profile', profile);

// Subscription endpoints
export const getSubscriptionPlans = () => 
  api.get('/subscriptions/plans');

export const createSubscription = (planId) => 
  api.post('/subscriptions', { planId });

export const cancelSubscription = () => 
  api.post('/subscriptions/cancel');

// Custom domain endpoints
export const addCustomDomain = (websiteId, domain) => 
  api.post(`/websites/${websiteId}/domains`, { domain });

export const removeCustomDomain = (websiteId, domain) => 
  api.delete(`/websites/${websiteId}/domains/${domain}`);

// Version control endpoints
export const createWebsiteVersion = (websiteId) => 
  api.post(`/websites/${websiteId}/versions`);

export const getWebsiteVersions = (websiteId) => 
  api.get(`/websites/${websiteId}/versions`);

export const restoreWebsiteVersion = (websiteId, versionId) => 
  api.post(`/websites/${websiteId}/versions/${versionId}/restore`);

// API key management
export const generateApiKey = () => 
  api.post('/api-keys');

export const getApiKeys = () => 
  api.get('/api-keys');

export const revokeApiKey = (keyId) => 
  api.delete(`/api-keys/${keyId}`);

export default api; 