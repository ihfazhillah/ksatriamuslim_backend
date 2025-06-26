import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";
import { invoiceAPI } from "../services/api";
import { Invoice, Client } from "../types";
import { formatCurrency, formatDate } from "../utils/format";

const Invoices: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const response = await invoiceAPI.getInvoices();
      setInvoices(response.data || []);
    } catch (error: any) {
      console.error("Error loading invoices:", error);
      toast.error("Failed to load invoices");
      setInvoices([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (
    invoiceId: number,
    newStatus: Invoice["status"]
  ) => {
    try {
      await invoiceAPI.updateInvoiceStatus(invoiceId, newStatus);
      setInvoices((prev) =>
        prev.map((invoice) =>
          invoice.id === invoiceId ? { ...invoice, status: newStatus } : invoice
        )
      );
      toast.success("Invoice status updated successfully!");
    } catch (error: any) {
      toast.error("Failed to update invoice status");
    }
  };

  const handleDelete = async (invoice: Invoice) => {
    if (
      !window.confirm(
        `Are you sure you want to delete invoice ${invoice.invoice_number}?`
      )
    ) {
      return;
    }

    try {
      await invoiceAPI.deleteInvoice(invoice.id);
      setInvoices((prev) => prev.filter((i) => i.id !== invoice.id));
      toast.success("Invoice deleted successfully!");
    } catch (error: any) {
      toast.error("Failed to delete invoice");
    }
  };

  const handleDownloadPDF = async (invoice: Invoice) => {
    try {
      const response = await invoiceAPI.downloadInvoicePDF(invoice.id);
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${invoice.invoice_number}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      toast.error("Failed to download PDF");
    }
  };

  const handleRegeneratePDF = async (invoice: Invoice) => {
    try {
      await invoiceAPI.regenerateInvoicePDF(invoice.id);
      toast.success("PDF regenerated successfully!");
    } catch (error: any) {
      toast.error("Failed to regenerate PDF");
    }
  };

  // Filter and sort invoices
  const filteredInvoices = invoices
    .filter((invoice) => {
      const matchesSearch =
        invoice.invoice_number
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        invoice.client?.name
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        invoice.client?.email?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus =
        statusFilter === "all" || invoice.status === statusFilter;

      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy) {
        case "invoice_number":
          aValue = a.invoice_number;
          bValue = b.invoice_number;
          break;
        case "client_name":
          aValue = a.client?.name || "";
          bValue = b.client?.name || "";
          break;
        case "total_amount":
          aValue = a.total_idr || 0;
          bValue = b.total_idr || 0;
          break;
        case "invoice_date":
          aValue = a.invoice_date ? new Date(a.invoice_date) : new Date(0);
          bValue = b.invoice_date ? new Date(b.invoice_date) : new Date(0);
          break;
        default:
          aValue = a.created_at ? new Date(a.created_at) : new Date(0);
          bValue = b.created_at ? new Date(b.created_at) : new Date(0);
      }

      if (sortOrder === "asc") {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const getStatusBadge = (status: Invoice["status"]) => {
    const statusStyles = {
      draft: "bg-gray-100 text-gray-800",
      sent: "bg-blue-100 text-blue-800",
      paid: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
    };

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status]}`}
      >
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getStatusOptions = (currentStatus: Invoice["status"]) => {
    const allStatuses: Invoice["status"][] = [
      "draft",
      "sent",
      "paid",
      "cancelled",
    ];
    return allStatuses.filter((status) => status !== currentStatus);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
        <Link to="/invoices/create" className="btn btn-primary">
          + Create Invoice
        </Link>
      </div>

      {/* Filters and Search */}
      <div className="mb-6 space-y-4 md:space-y-0 md:flex md:items-center md:space-x-4">
        {/* Search */}
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Search by invoice number, client name, or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg
                className="h-5 w-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Status Filter */}
        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="paid">Paid</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        {/* Sort */}
        <div className="flex space-x-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="input"
          >
            <option value="created_at">Created Date</option>
            <option value="invoice_number">Invoice Number</option>
            <option value="client_name">Client Name</option>
            <option value="total_amount">Amount</option>
            <option value="invoice_date">Invoice Date</option>
          </select>
          <button
            onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
            className="btn btn-secondary px-3"
          >
            {sortOrder === "asc" ? "↑" : "↓"}
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-gray-900">
              {invoices.length}
            </div>
            <div className="text-sm text-gray-500">Total Invoices</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-green-600">
              {invoices.filter((i) => i.status === "paid").length}
            </div>
            <div className="text-sm text-gray-500">Paid</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-orange-600">
              {invoices.filter((i) => i.status === "sent").length}
            </div>
            <div className="text-sm text-gray-500">Pending</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(
                invoices
                  .filter((i) => i.status !== "cancelled")
                  .reduce((sum, i) => sum + (i.total_idr || 0), 0),
                "IDR"
              )}
            </div>
            <div className="text-sm text-gray-500">Total Value</div>
          </div>
        </div>
      </div>

      {/* Invoices Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredInvoices.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-500 mb-4">
                {searchTerm || statusFilter !== "all"
                  ? "No invoices found matching your filters."
                  : "No invoices yet."}
              </div>
              {!searchTerm && statusFilter === "all" && (
                <Link to="/invoices/create" className="btn btn-primary">
                  Create Your First Invoice
                </Link>
              )}
            </div>
          ) : (
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
                    Period
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Invoice Date
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredInvoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <Link
                          to={`/invoices/${invoice.id}`}
                          className="text-sm font-medium text-blue-600 hover:text-blue-900"
                        >
                          {invoice.invoice_number}
                        </Link>
                        <div className="text-sm text-gray-500">
                          {invoice.created_at
                            ? formatDate(invoice.created_at)
                            : "No date"}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {invoice.client?.name || "No client"}
                        </div>
                        <div className="text-sm text-gray-500">
                          {invoice.client?.email || "No email"}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div>
                        <div>
                          {invoice.period_start
                            ? formatDate(invoice.period_start)
                            : "No start date"}
                        </div>
                        <div className="text-gray-500">
                          to{" "}
                          {invoice.period_end
                            ? formatDate(invoice.period_end)
                            : "No end date"}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(invoice.total_idr || 0, "IDR")}
                      </div>
                      <div className="text-sm text-gray-500">
                        Subtotal:{" "}
                        {formatCurrency(invoice.subtotal_usd || 0, "USD")}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="relative">
                        <select
                          value={invoice.status}
                          onChange={(e) =>
                            handleStatusChange(
                              invoice.id,
                              e.target.value as Invoice["status"]
                            )
                          }
                          className="appearance-none bg-transparent border-none text-xs font-medium focus:outline-none"
                          style={{
                            color:
                              invoice.status === "paid"
                                ? "#059669"
                                : invoice.status === "sent"
                                ? "#2563eb"
                                : invoice.status === "cancelled"
                                ? "#dc2626"
                                : "#6b7280",
                          }}
                        >
                          <option value={invoice.status}>
                            {invoice.status.charAt(0).toUpperCase() +
                              invoice.status.slice(1)}
                          </option>
                          {getStatusOptions(invoice.status).map((status) => (
                            <option key={status} value={status}>
                              {status.charAt(0).toUpperCase() + status.slice(1)}
                            </option>
                          ))}
                        </select>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {invoice.invoice_date
                        ? formatDate(invoice.invoice_date)
                        : "No date"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <Link
                          to={`/invoices/${invoice.id}`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View
                        </Link>
                        <button
                          onClick={() => handleDownloadPDF(invoice)}
                          className="text-green-600 hover:text-green-900"
                        >
                          PDF
                        </button>
                        <button
                          onClick={() => handleRegeneratePDF(invoice)}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          Regenerate
                        </button>
                        <button
                          onClick={() => handleDelete(invoice)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default Invoices;
