// User and Authentication Types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface AuthTokens {
  key: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password1: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

// Clockify Configuration Types
export interface ClockifyConfig {
  id?: number;
  api_key: string;
  workspace_id: string;
  clockify_user_id: string;
  hourly_rate: number;
  conversion_rate: number;
  company_name: string;
  company_address: string;
  company_phone: string;
  company_email: string;
  bank_name: string;
  bank_account_number: string;
  bank_account_name: string;
  created_at?: string;
  updated_at?: string;
}

// Client Types
export interface Client {
  id: number;
  name: string;
  email: string;
  address_line1: string;
  address_line2?: string;
  address_line3?: string;
  address_line4?: string;
  phone?: string;
  created_at?: string;
  updated_at?: string;
}

// For display purposes
export interface ClientDisplay
  extends Omit<
    Client,
    "address_line1" | "address_line2" | "address_line3" | "address_line4"
  > {
  address: string;
}

// Invoice Types
export interface Invoice {
  id: number;
  invoice_number: string;
  client: ClientDisplay;
  period_start: string;
  period_end: string;
  invoice_date: string;
  due_date?: string; // Optional since backend doesn't have this
  total_hours: number;
  hourly_rate: number; // USD hourly rate
  subtotal_usd: number; // Subtotal in USD (was 'subtotal')
  conversion_rate: number;
  total_idr: number; // Total in IDR (was 'total_amount')
  tax_rate?: number; // Optional
  tax_amount?: number; // Optional, calculated
  status: "draft" | "sent" | "paid" | "cancelled";
  pdf_file?: string;
  pdf_url?: string;
  created_at: string;
  updated_at: string;
  manual_entries: ManualEntry[];
  time_entries: ClockifyTimeEntry[];
}

export interface CreateInvoiceRequest {
  client_id: number;
  invoice_number: string;
  period_start: string;
  period_end: string;
  invoice_date: string;
  due_date: string;
  tax_rate?: number;
  conversion_rate: number;
  excluded_entries?: string[];
  manual_entries?: CreateManualEntryRequest[];
}

export interface CreateManualEntryRequest {
  description: string;
  rate: number; // Backend uses 'rate'
  quantity: number;
}

// Manual Entry Types
export interface ManualEntry {
  id: number;
  description: string;
  rate: number; // Backend uses 'rate' not 'unit_price'
  quantity: number;
  total_amount: number;
  created_at: string;
  updated_at: string;
}

// Time Entry Types
export interface ClockifyTimeEntry {
  id: number;
  clockify_id: string;
  description: string;
  project_id?: string; // Clockify project ID
  project_name: string;
  task_name?: string;
  duration?: string | null; // For backward compatibility
  duration_hours: string; // Actual field from backend
  start_time: string; // Format: "202506241333"
  end_time: string; // Format: "202506241428"
  billable?: boolean;
  hourly_rate?: number;
  total_amount?: number;
  created_at: string; // Format: "202506260738"
}

// Clockify Project Types
export interface ClockifyProject {
  id: number;
  clockify_id: string;
  name: string;
  client_name?: string;
  color?: string;
  archived: boolean;
  last_synced: string;
  created_at: string;
  updated_at: string;
}

export interface TimeEntriesPreview {
  entries: ClockifyTimeEntry[];
  total_hours: number;
  total_amount: number;
  summary: {
    [projectName: string]: {
      hours: number;
      amount: number;
    };
  };
}

// Dashboard Types
export interface DashboardStats {
  total_invoices: number;
  total_revenue: number;
  unpaid_invoices: number;
  unpaid_amount: number;
  recent_invoices: Invoice[];
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Form Types
export interface ClockifyConfigFormData {
  api_key: string;
  workspace_id: string;
  clockify_user_id: string;
  hourly_rate: number;
  conversion_rate: number;
  company_name: string;
  company_address: string;
  company_phone: string;
  company_email: string;
  bank_name: string;
  bank_account_number: string;
  bank_account_name: string;
}

export interface ClientFormData {
  name: string;
  email: string;
  address_line1: string;
  address_line2?: string;
  address_line3?: string;
  address_line4?: string;
  phone?: string;
}

export interface InvoiceFormData {
  client_id: number;
  invoice_number: string;
  period_start: string;
  period_end: string;
  invoice_date: string;
  due_date: string;
  tax_rate: number;
}
