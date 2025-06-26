import React from "react";
import { useQuery } from "react-query";
import { useNavigate } from "react-router-dom";
import {
  DollarSign,
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Eye,
} from "lucide-react";
import { invoiceAPI } from "../services/api";
import { Invoice } from "../types";
import { formatCurrency } from "../utils/format";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const {
    data: dashboardData,
    isLoading,
    error,
  } = useQuery(
    "dashboard-stats",
    () => invoiceAPI.getDashboardStats().then((res) => res.data),
    {
      refetchOnWindowFocus: false,
    }
  );

  const getStatusBadgeClass = (status: Invoice["status"]) => {
    switch (status) {
      case "draft":
        return "badge badge-warning";
      case "sent":
        return "badge badge-primary";
      case "paid":
        return "badge badge-success";
      case "cancelled":
        return "badge badge-danger";
      default:
        return "badge";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="card-body">
          <div className="flex items-center space-x-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>Failed to load dashboard data</span>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData?.has_clockify_config) {
    return (
      <div className="card">
        <div className="card-body text-center">
          <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Clockify Configuration Required
          </h3>
          <p className="text-gray-600 mb-4">
            Please configure your Clockify API settings before creating
            invoices.
          </p>
          <button
            onClick={() => navigate("/config")}
            className="btn btn-primary"
          >
            Configure Clockify
          </button>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats;
  const recentInvoices = dashboardData?.recent_invoices || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <button
          onClick={() => navigate("/invoices/create")}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Create Invoice</span>
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Invoices"
          value={stats?.total_invoices || 0}
          icon={FileText}
          color="blue"
        />
        <StatCard
          title="Draft Invoices"
          value={stats?.draft_invoices || 0}
          icon={Clock}
          color="yellow"
        />
        <StatCard
          title="Paid Invoices"
          value={stats?.paid_invoices || 0}
          icon={CheckCircle}
          color="green"
        />
        <StatCard
          title="Total Earnings (USD)"
          value={formatCurrency(stats?.total_earnings_usd || 0, "USD")}
          icon={DollarSign}
          color="green"
          isAmount
        />
      </div>

      {/* Recent Invoices */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Recent Invoices
            </h2>
            <button
              onClick={() => navigate("/invoices")}
              className="btn btn-secondary text-sm"
            >
              View All
            </button>
          </div>
        </div>
        <div className="card-body p-0">
          {recentInvoices.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No invoices created yet.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Invoice
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Client
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentInvoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {invoice.invoice_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {invoice.client_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(invoice.subtotal_usd, "USD")}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={getStatusBadgeClass(invoice.status)}>
                          {invoice.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(invoice.invoice_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={() => navigate(`/invoices/${invoice.id}`)}
                          className="text-primary-600 hover:text-primary-700"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  color: "blue" | "yellow" | "green" | "red";
  isAmount?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  color,
  isAmount = false,
}) => {
  const colorClasses = {
    blue: "text-blue-600 bg-blue-100",
    yellow: "text-yellow-600 bg-yellow-100",
    green: "text-green-600 bg-green-100",
    red: "text-red-600 bg-red-100",
  };

  return (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center">
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="h-6 w-6" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p
              className={`text-2xl font-semibold text-gray-900 ${
                isAmount ? "text-lg" : ""
              }`}
            >
              {value}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
