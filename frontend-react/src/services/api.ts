import axios, { AxiosResponse } from "axios";
import { toast } from "react-toastify";
import {
  ClockifyConfig,
  Client,
  Invoice,
  CreateInvoiceRequest,
  TimeEntriesPreview,
  DashboardStats,
  AuthTokens,
  LoginRequest,
  RegisterRequest,
  User,
  ManualEntry,
} from "../types";

const API_BASE_URL = "/api";

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    } else if (error.response?.status >= 500) {
      toast.error("Server error occurred. Please try again later.");
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (data: LoginRequest): Promise<AxiosResponse<AuthTokens>> =>
    api.post("/auth/login/", data),

  register: (data: RegisterRequest): Promise<AxiosResponse<{ key: string }>> =>
    api.post("/auth/registration/", data),

  logout: (): Promise<AxiosResponse<void>> => api.post("/auth/logout/"),

  getCurrentUser: (): Promise<AxiosResponse<User>> => api.get("/auth/user/"),
};

// Invoice Management API
export const invoiceAPI = {
  // Dashboard
  getDashboardStats: (): Promise<AxiosResponse<DashboardStats>> =>
    api.get("/invoice-management/dashboard/"),

  // Clockify Configuration
  getClockifyConfig: (): Promise<AxiosResponse<ClockifyConfig>> =>
    api.get("/invoice-management/config/"),

  createOrUpdateClockifyConfig: (
    data: Partial<ClockifyConfig>
  ): Promise<AxiosResponse<ClockifyConfig>> =>
    api.post("/invoice-management/config/", data),

  testClockifyConnection: (data: {
    api_key: string;
    workspace_id: string;
    clockify_user_id: string;
  }): Promise<
    AxiosResponse<{ success: boolean; message: string; entries_count: number }>
  > => api.post("/invoice-management/config/test/", data),

  // Clients
  getClients: (): Promise<AxiosResponse<Client[]>> =>
    api.get("/invoice-management/clients/"),

  createClient: (
    data: Omit<Client, "id" | "created_at" | "updated_at">
  ): Promise<AxiosResponse<Client>> =>
    api.post("/invoice-management/clients/", data),

  updateClient: (
    id: number,
    data: Partial<Client>
  ): Promise<AxiosResponse<Client>> =>
    api.put(`/invoice-management/clients/${id}/`, data),

  deleteClient: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/invoice-management/clients/${id}/`),

  // Invoices
  getInvoices: (): Promise<AxiosResponse<Invoice[]>> =>
    api.get("/invoice-management/invoices/"),

  getInvoice: (id: number): Promise<AxiosResponse<Invoice>> =>
    api.get(`/invoice-management/invoices/${id}/`),

  createInvoice: (
    data: CreateInvoiceRequest
  ): Promise<AxiosResponse<Invoice>> =>
    api.post("/invoice-management/invoices/", data),

  updateInvoiceStatus: (
    id: number,
    status: Invoice["status"]
  ): Promise<AxiosResponse<{ status: string }>> =>
    api.patch(`/invoice-management/invoices/${id}/status/`, { status }),

  deleteInvoice: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/invoice-management/invoices/${id}/`),

  downloadInvoicePDF: (id: number): Promise<AxiosResponse<Blob>> =>
    api.get(`/invoice-management/invoices/${id}/pdf/`, {
      responseType: "blob",
    }),

  regenerateInvoicePDF: (
    id: number
  ): Promise<
    AxiosResponse<{ success: boolean; message: string; pdf_url?: string }>
  > => api.post(`/invoice-management/invoices/${id}/regenerate-pdf/`),

  // Time Entries Preview
  previewTimeEntries: (
    data: {
      period_start: string;
      period_end: string;
    },
    options?: { signal?: AbortSignal }
  ): Promise<AxiosResponse<TimeEntriesPreview>> =>
    api.post("/invoice-management/time-entries/preview/", data, options),

  // Manual Entries
  getManualEntries: (
    invoiceId: number
  ): Promise<AxiosResponse<ManualEntry[]>> =>
    api.get(`/invoice-management/invoices/${invoiceId}/manual-entries/`),

  createManualEntry: (
    invoiceId: number,
    data: Omit<ManualEntry, "id" | "total_amount" | "created_at" | "updated_at">
  ): Promise<AxiosResponse<ManualEntry>> =>
    api.post(`/invoice-management/invoices/${invoiceId}/manual-entries/`, data),

  updateManualEntry: (
    id: number,
    data: Partial<ManualEntry>
  ): Promise<AxiosResponse<ManualEntry>> =>
    api.put(`/invoice-management/manual-entries/${id}/`, data),

  deleteManualEntry: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/invoice-management/manual-entries/${id}/`),
};

// Auth helpers
export const authHelpers = {
  setTokens: (tokens: AuthTokens) => {
    localStorage.setItem("access_token", tokens.key);
  },

  clearTokens: () => {
    localStorage.removeItem("access_token");
  },

  getAccessToken: () => localStorage.getItem("access_token"),

  isAuthenticated: () => !!localStorage.getItem("access_token"),
};

export default api;
