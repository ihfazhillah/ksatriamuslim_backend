import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { toast } from "react-toastify";
import { invoiceAPI } from "../services/api";
import { Invoice } from "../types";
import {
  formatCurrency,
  formatDate,
  formatHours,
  formatClockifyDateTime,
  formatDurationFromHours,
} from "../utils/format";

const InvoiceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [changingStatus, setChangingStatus] = useState(false);
  const [downloadingPDF, setDownloadingPDF] = useState(false);
  const [regeneratingPDF, setRegeneratingPDF] = useState(false);

  useEffect(() => {
    if (id) {
      loadInvoice();
    }
  }, [id]);

  const loadInvoice = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const response = await invoiceAPI.getInvoice(parseInt(id));
      setInvoice(response.data);
    } catch (error: any) {
      toast.error("Failed to load invoice");
      navigate("/invoices");
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: Invoice["status"]) => {
    if (!invoice) return;

    try {
      setChangingStatus(true);
      await invoiceAPI.updateInvoiceStatus(invoice.id, newStatus);
      setInvoice((prev) => (prev ? { ...prev, status: newStatus } : null));
      toast.success("Invoice status updated successfully!");
    } catch (error: any) {
      toast.error("Failed to update invoice status");
    } finally {
      setChangingStatus(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!invoice) return;

    try {
      setDownloadingPDF(true);
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
    } finally {
      setDownloadingPDF(false);
    }
  };

  const handleRegeneratePDF = async () => {
    if (!invoice) return;

    try {
      setRegeneratingPDF(true);
      await invoiceAPI.regenerateInvoicePDF(invoice.id);
      toast.success("PDF regenerated successfully!");
      // Reload invoice to get updated PDF path
      loadInvoice();
    } catch (error: any) {
      toast.error("Failed to regenerate PDF");
    } finally {
      setRegeneratingPDF(false);
    }
  };

  const handleDelete = async () => {
    if (!invoice) return;

    if (
      !window.confirm(
        `Are you sure you want to delete invoice ${invoice.invoice_number}?`
      )
    ) {
      return;
    }

    try {
      await invoiceAPI.deleteInvoice(invoice.id);
      toast.success("Invoice deleted successfully!");
      navigate("/invoices");
    } catch (error: any) {
      toast.error("Failed to delete invoice");
    }
  };

  const getStatusBadge = (status: Invoice["status"]) => {
    const statusStyles = {
      draft: "bg-gray-100 text-gray-800",
      sent: "bg-blue-100 text-blue-800",
      paid: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
    };

    return (
      <span
        className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusStyles[status]}`}
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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900">
          Invoice not found
        </h2>
        <p className="mt-2 text-gray-600">
          The invoice you're looking for doesn't exist.
        </p>
        <Link to="/invoices" className="btn btn-primary mt-4">
          Back to Invoices
        </Link>
      </div>
    );
  }

  const timeEntriesTotal = invoice.time_entries.reduce((sum, entry) => {
    // Calculate: duration_hours * invoice.hourly_rate (rate is at invoice level)
    const hours = parseFloat(entry.duration_hours || "0");
    const rate = invoice.hourly_rate || 0;

    return sum + hours * rate;
  }, 0);
  const manualEntriesTotal = invoice.manual_entries.reduce((sum, entry) => {
    // Calculate total from rate * quantity if total_amount not available
    if (entry.total_amount) {
      return sum + entry.total_amount;
    }

    const rate = entry.rate || 0;
    const quantity = entry.quantity || 0;
    return sum + rate * quantity;
  }, 0);
  const totalHours = invoice.time_entries.reduce((sum, entry) => {
    // Use duration_hours field which contains decimal hours like "0.92"
    const durationHours = entry.duration_hours;
    if (!durationHours) return sum;

    const hours = parseFloat(durationHours);
    return sum + (isNaN(hours) ? 0 : hours);
  }, 0);

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-2xl font-bold text-gray-900">
              {invoice.invoice_number}
            </h1>
            {getStatusBadge(invoice.status)}
          </div>
          <p className="text-gray-600">
            Created on {formatDate(invoice.created_at)}
          </p>
        </div>

        <div className="flex space-x-3">
          <Link to="/invoices" className="btn btn-secondary">
            ← Back to Invoices
          </Link>

          <button
            onClick={handleDownloadPDF}
            disabled={downloadingPDF}
            className="btn btn-primary"
          >
            {downloadingPDF ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Downloading...
              </>
            ) : (
              "Download PDF"
            )}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Invoice Information */}
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Invoice Information
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500">
                    Invoice Date
                  </label>
                  <p className="text-sm text-gray-900">
                    {formatDate(invoice.invoice_date)}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">
                    Hourly Rate
                  </label>
                  <p className="text-sm text-gray-900">
                    {formatCurrency(invoice.hourly_rate || 0, "USD")}/hr
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">
                    Work Period
                  </label>
                  <p className="text-sm text-gray-900">
                    {formatDate(invoice.period_start)} -{" "}
                    {formatDate(invoice.period_end)}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">
                    Total Hours
                  </label>
                  <p className="text-sm text-gray-900">
                    {formatHours(invoice.total_hours || 0)}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Client Information */}
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Client Information
              </h3>
              <div className="space-y-2">
                <div>
                  <label className="block text-sm font-medium text-gray-500">
                    Name
                  </label>
                  <p className="text-sm text-gray-900">{invoice.client.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">
                    Email
                  </label>
                  <p className="text-sm text-gray-900">
                    {invoice.client.email}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">
                    Address
                  </label>
                  <p className="text-sm text-gray-900 whitespace-pre-line">
                    {invoice.client.address || "No address provided"}
                  </p>
                </div>
                {invoice.client.phone && (
                  <div>
                    <label className="block text-sm font-medium text-gray-500">
                      Phone
                    </label>
                    <p className="text-sm text-gray-900">
                      {invoice.client.phone}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Time Entries */}
          {invoice.time_entries.length > 0 && (
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Time Entries ({invoice.time_entries.length} entries)
                </h3>

                <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Total Hours:</span>
                      <div className="text-blue-600 font-bold">
                        {formatHours(totalHours)}
                      </div>
                    </div>
                    <div>
                      <span className="font-medium">Time Entries Total:</span>
                      <div className="text-blue-600 font-bold">
                        {formatCurrency(timeEntriesTotal, "USD")}
                      </div>
                    </div>
                    <div>
                      <span className="font-medium">Billable Entries:</span>
                      <div className="text-blue-600 font-bold">
                        {invoice.time_entries.filter((e) => e.billable).length}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Date
                        </th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Project
                        </th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Description
                        </th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Duration
                        </th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Rate
                        </th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                          Amount
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {invoice.time_entries.map((entry, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {formatClockifyDateTime(entry.start_time)}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {entry.project_name ||
                              entry.task_name ||
                              "No project"}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-600">
                            {entry.description || "No description"}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {formatDurationFromHours(entry.duration_hours)}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {formatCurrency(invoice.hourly_rate || 0, "USD")}/hr
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right">
                            {formatCurrency(
                              parseFloat(entry.duration_hours || "0") *
                                (invoice.hourly_rate || 0),
                              "USD"
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Manual Entries */}
          {invoice.manual_entries.length > 0 && (
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Additional Items ({invoice.manual_entries.length} items)
                </h3>

                <div className="mb-4 p-4 bg-green-50 rounded-lg">
                  <div className="text-sm">
                    <span className="font-medium">Additional Items Total:</span>
                    <div className="text-green-600 font-bold text-lg">
                      {formatCurrency(manualEntriesTotal, "USD")}
                    </div>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Description
                        </th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Quantity
                        </th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Unit Price
                        </th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                          Total
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {invoice.manual_entries.map((entry, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {entry.description}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {entry.quantity}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {formatCurrency(entry.rate || 0, "USD")}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right">
                            {formatCurrency(entry.total_amount || 0, "USD")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Management */}
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Status Management
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Status
                  </label>
                  {getStatusBadge(invoice.status)}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Change Status
                  </label>
                  <div className="space-y-2">
                    {getStatusOptions(invoice.status).map((status) => (
                      <button
                        key={status}
                        onClick={() => handleStatusChange(status)}
                        disabled={changingStatus}
                        className="w-full text-left px-3 py-2 text-sm border border-gray-200 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        Mark as{" "}
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Invoice Summary */}
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Invoice Summary
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal (USD):</span>
                  <span className="font-medium">
                    {formatCurrency(invoice.subtotal_usd || 0, "USD")}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Exchange Rate:</span>
                  <span className="font-medium">
                    1 USD = {invoice.conversion_rate || 15000} IDR
                  </span>
                </div>
                <div className="border-t pt-3">
                  <div className="flex justify-between text-lg font-bold">
                    <span>Total (IDR):</span>
                    <span>{formatCurrency(invoice.total_idr || 0, "IDR")}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Actions
              </h3>
              <div className="space-y-3">
                <button
                  onClick={handleDownloadPDF}
                  disabled={downloadingPDF}
                  className="btn btn-primary w-full"
                >
                  {downloadingPDF ? "Downloading..." : "Download PDF"}
                </button>

                <button
                  onClick={handleRegeneratePDF}
                  disabled={regeneratingPDF}
                  className="btn btn-secondary w-full"
                >
                  {regeneratingPDF ? "Regenerating..." : "Regenerate PDF"}
                </button>

                <div className="border-t pt-3">
                  <button
                    onClick={handleDelete}
                    className="btn btn-danger w-full"
                  >
                    Delete Invoice
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvoiceDetail;
