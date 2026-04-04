/**
 * DisruptShield API Client
 * All backend API calls centralized here.
 * Includes JWT auth interceptor.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ── Auth interceptor: attach JWT token to every request ──
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('ds_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// ── Auth ──
export const riderLogin = (email, password) =>
    api.post('/auth/rider-login', { email, password });

export const adminLogin = (email, password) =>
    api.post('/auth/admin-login', { email, password });

export const logout = () => api.post('/auth/logout');

export const getMe = () => api.get('/auth/me');

// ── Riders ──
export const uploadRidersCSV = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/riders/upload_csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

export const getRiders = (skip = 0, limit = 100) =>
    api.get('/riders', { params: { skip, limit } });

export const getRider = (riderId) =>
    api.get(`/riders/${riderId}`);

// ── Policies ──
export const getPolicy = (riderId) =>
    api.get(`/policies/${riderId}`);

export const getPremiumHistory = (riderId) =>
    api.get(`/policies/${riderId}/premium_history`);

export const getClaimHistory = (riderId) =>
    api.get(`/policies/${riderId}/claims`);

export const getPayoutHistory = (riderId) =>
    api.get(`/policies/${riderId}/payouts`);

// ── Premium ──
export const recalculatePremium = (riderId, data = {}) =>
    api.post(`/premium/recalculate/${riderId}`, data);

// ── Claims ──
export const submitClaim = (data) =>
    api.post('/claims/submit', data);

export const getClaimsByRider = (riderId) =>
    api.get(`/claims/${riderId}`);

// ── Payouts ──
export const processPayout = (claimId) =>
    api.post(`/payouts/process/${claimId}`);

// ── Events ──
export const createEvent = (data) =>
    api.post('/events/create', data);

export const getEvents = (skip = 0, limit = 50) =>
    api.get('/events', { params: { skip, limit } });

// ── Dashboard ──
export const getDashboardSummary = () =>
    api.get('/dashboard/summary');

// ── Admin Seeding ──
export const seedAdminData = () =>
    api.post('/admin/seed-data');

export default api;
