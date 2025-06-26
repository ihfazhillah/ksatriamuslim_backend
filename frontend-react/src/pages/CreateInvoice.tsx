import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useForm, useFieldArray } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { toast } from "react-toastify";
import { invoiceAPI } from "../services/api";
import {
  Client,
  CreateInvoiceRequest,
  CreateManualEntryRequest,
  TimeEntriesPreview,
  ClockifyTimeEntry,
} from "../types";
import { formatCurrency, formatDate, formatHours } from "../utils/format";

const schema = yup.object({
  client_id: yup.number().required("Client is required"),
  invoice_number: yup.string().required("Invoice number is required"),
  period_start: yup.string().required("Start date is required"),
  period_end: yup.string().required("End date is required"),
  invoice_date: yup.string().required("Invoice date is required"),
  due_date: yup.string().required("Due date is required"),
  tax_rate: yup.number().min(0).max(100).required("Tax rate is required"),
  conversion_rate: yup
    .number()
    .positive("Must be positive")
    .required("Conversion rate is required"),
  manual_entries: yup.array().of(
    yup.object({
      description: yup.string().required("Description is required"),
      quantity: yup
        .number()
        .positive("Must be positive")
        .required("Quantity is required"),
      unit_price: yup
        .number()
        .positive("Must be positive")
        .required("Unit price is required"),
    })
  ),
});

type FormData = {
  client_id: number;
  invoice_number: string;
  period_start: string;
  period_end: string;
  invoice_date: string;
  due_date: string;
  tax_rate: number;
  conversion_rate: number;
  manual_entries: CreateManualEntryRequest[];
};

const CreateInvoice: React.FC = () => {
  const navigate = useNavigate();
  const [clients, setClients] = useState<Client[]>([]);
  const [timePreview, setTimePreview] = useState<TimeEntriesPreview | null>(
    null
  );
  const [excludedEntries, setExcludedEntries] = useState<Set<string>>(
    new Set()
  );
  const [sortBy, setSortBy] = useState<
    "date" | "start_time" | "project" | "duration"
  >("start_time");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [filterDate, setFilterDate] = useState<string>("");
  const [loadingClients, setLoadingClients] = useState(true);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Debounce timer for API calls
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const currentRequest = useRef<AbortController | null>(null);

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      invoice_number: `INV-${new Date().getFullYear()}-${String(
        Date.now()
      ).slice(-6)}`,
      tax_rate: 0,
      conversion_rate: 15000, // Default IDR exchange rate
      invoice_date: new Date().toISOString().split("T")[0],
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split("T")[0],
      manual_entries: [],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "manual_entries",
  });

  const period_start = watch("period_start");
  const period_end = watch("period_end");

  useEffect(() => {
    loadClients();

    // Cleanup function to cancel any pending requests on component unmount
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
      if (currentRequest.current) {
        currentRequest.current.abort();
      }
    };
  }, []);

  useEffect(() => {
    // Clear previous timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    // Cancel previous request if still pending
    if (currentRequest.current) {
      currentRequest.current.abort();
    }

    if (period_start && period_end) {
      // Debounce API call by 1000ms
      debounceTimer.current = setTimeout(() => {
        loadTimeEntriesPreview();
      }, 1000);
    } else {
      // Clear preview if dates are not set
      setTimePreview(null);
    }
  }, [period_start, period_end]);

  const loadClients = async () => {
    try {
      setLoadingClients(true);
      const response = await invoiceAPI.getClients();
      setClients(response.data);
    } catch (error: any) {
      toast.error("Failed to load clients");
    } finally {
      setLoadingClients(false);
    }
  };

  const loadTimeEntriesPreview = async () => {
    const period_start = watch("period_start");
    const period_end = watch("period_end");

    if (!period_start || !period_end) return;

    try {
      setLoadingPreview(true);

      // Create abort controller for this request
      const abortController = new AbortController();
      currentRequest.current = abortController;

      // Convert date strings to proper datetime format for Django
      // Add time component to make it a proper datetime
      const startDateTime = `${period_start}T00:00:00Z`; // Start of day
      const endDateTime = `${period_end}T23:59:59Z`; // End of day

      const response = await invoiceAPI.previewTimeEntries(
        {
          period_start: startDateTime,
          period_end: endDateTime,
        },
        {
          signal: abortController.signal,
        }
      );

      // Only update state if request wasn't aborted
      if (!abortController.signal.aborted) {
        setTimePreview(response.data);
        // Reset excluded entries when new data is loaded
        setExcludedEntries(new Set());
      }
    } catch (error: any) {
      // Don't handle errors for aborted requests
      if (error.name === "AbortError") {
        return;
      }

      setTimePreview(null);
      console.error("Time entries preview error:", error);

      // Handle specific error cases
      if (error.response?.status === 400) {
        const errorData = error.response.data;
        if (errorData.error === "Clockify configuration not found") {
          toast.error(
            "Please configure your Clockify settings first in Settings"
          );
          return;
        }

        // Check for validation errors
        if (errorData.period_start || errorData.period_end) {
          const validationError =
            errorData.period_start?.[0] || errorData.period_end?.[0];
          toast.error(`Date validation error: ${validationError}`);
          return;
        }

        // Check for non_field_errors
        if (errorData.non_field_errors) {
          toast.error(errorData.non_field_errors[0]);
          return;
        }

        // Generic error from backend
        if (errorData.error) {
          toast.error(errorData.error);
          return;
        }

        // Show validation errors if any
        if (Object.keys(errorData).length > 0) {
          const firstError = Object.values(errorData)[0];
          const errorMessage = Array.isArray(firstError)
            ? firstError[0]
            : firstError;
          toast.error(`Validation error: ${errorMessage}`);
          return;
        }
      }

      // Don't show error for 404 - means no time entries found
      if (error.response?.status !== 404) {
        console.error(
          "Time entries preview error:",
          error.response?.data || error.message
        );
        toast.error("Failed to load time entries preview");
      }
    } finally {
      setLoadingPreview(false);
      currentRequest.current = null;
    }
  };

  const onSubmit = async (data: FormData) => {
    try {
      setSubmitting(true);

      // Format datetime fields to include timezone
      const formatDateTimeForDjango = (dateString: string) => {
        if (!dateString) return null;
        // Convert date to datetime with timezone (using WIB timezone)
        const date = new Date(dateString + "T00:00:00+07:00");
        return date.toISOString();
      };

      // Prepare request data with excluded entries and formatted dates
      const requestData: CreateInvoiceRequest = {
        ...data,
        period_start: formatDateTimeForDjango(data.period_start),
        period_end: formatDateTimeForDjango(data.period_end),
        excluded_entries: Array.from(excludedEntries),
      };

      const response = await invoiceAPI.createInvoice(requestData);
      toast.success("Invoice created successfully!");
      navigate(`/invoices/${response.data.id}`);
    } catch (error: any) {
      toast.error(error.response?.data?.message || "Failed to create invoice");
    } finally {
      setSubmitting(false);
    }
  };

  const addManualEntry = () => {
    append({
      description: "",
      quantity: 1,
      unit_price: 0,
    });
  };

  const getSortedEntries = () => {
    if (!timePreview) return [];

    let filtered = [...timePreview.entries];

    // Filter by date if specified
    if (filterDate) {
      filtered = filtered.filter((entry) => {
        const entryDate = new Date(entry.start_time)
          .toISOString()
          .split("T")[0];
        return entryDate === filterDate;
      });
    }

    const sorted = filtered.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case "date":
        case "start_time":
          comparison =
            new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
          break;
        case "project":
          comparison = a.project_name.localeCompare(b.project_name);
          break;
        case "duration":
          const aDuration = parseFloat(a.duration.replace("h", ""));
          const bDuration = parseFloat(b.duration.replace("h", ""));
          comparison = aDuration - bDuration;
          break;
      }

      return sortOrder === "asc" ? comparison : -comparison;
    });

    return sorted;
  };

  const getIncludedEntries = () => {
    const sortedEntries = getSortedEntries();
    return sortedEntries.filter(
      (entry) => !excludedEntries.has(entry.clockify_id)
    );
  };

  const getSubtotal = () => {
    // Calculate time entries total in USD using form's conversion rate
    const conversionRate = watch("conversion_rate") || 15000;
    const includedEntries = getIncludedEntries();
    const timeTotal = includedEntries.reduce((sum, entry) => {
      return sum + entry.total_amount / conversionRate;
    }, 0);

    const manualTotal = fields.reduce((sum, _, index) => {
      const quantity = watch(`manual_entries.${index}.quantity`) || 0;
      const price = watch(`manual_entries.${index}.unit_price`) || 0;
      return sum + quantity * price;
    }, 0);
    return timeTotal + manualTotal;
  };

  const toggleEntryExclusion = (entryId: string) => {
    const newExcluded = new Set(excludedEntries);
    if (newExcluded.has(entryId)) {
      newExcluded.delete(entryId);
    } else {
      newExcluded.add(entryId);
    }
    setExcludedEntries(newExcluded);
  };

  const getTaxAmount = () => {
    const subtotal = getSubtotal();
    const taxRate = watch("tax_rate") || 0;
    return (subtotal * taxRate) / 100;
  };

  const getTotal = () => {
    return getSubtotal() + getTaxAmount();
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Create Invoice</h1>
        <button
          onClick={() => navigate("/invoices")}
          className="btn btn-secondary"
        >
          Cancel
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Invoice Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Client Selection & Invoice Number */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Invoice Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Client *
                    </label>
                    {loadingClients ? (
                      <div className="input bg-gray-50">Loading clients...</div>
                    ) : (
                      <select {...register("client_id")} className="input">
                        <option value="">Select a client</option>
                        {clients.map((client) => (
                          <option key={client.id} value={client.id}>
                            {client.name} - {client.email}
                          </option>
                        ))}
                      </select>
                    )}
                    {errors.client_id && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.client_id.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Invoice Number *
                    </label>
                    <input
                      type="text"
                      {...register("invoice_number")}
                      className="input"
                      placeholder="INV-2024-001"
                    />
                    {errors.invoice_number && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.invoice_number.message}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Invoice Dates */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Invoice Dates
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Work Period Start *
                    </label>
                    <input
                      type="date"
                      {...register("period_start")}
                      className="input"
                    />
                    {errors.period_start && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.period_start.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Work Period End *
                    </label>
                    <input
                      type="date"
                      {...register("period_end")}
                      className="input"
                    />
                    {errors.period_end && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.period_end.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Invoice Date *
                    </label>
                    <input
                      type="date"
                      {...register("invoice_date")}
                      className="input"
                    />
                    {errors.invoice_date && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.invoice_date.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Due Date *
                    </label>
                    <input
                      type="date"
                      {...register("due_date")}
                      className="input"
                    />
                    {errors.due_date && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.due_date.message}
                      </p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tax Rate (%) *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="100"
                      {...register("tax_rate", { valueAsNumber: true })}
                      className="input"
                    />
                    {errors.tax_rate && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.tax_rate.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Exchange Rate (USD to IDR) *
                    </label>
                    <input
                      type="number"
                      step="1"
                      min="1"
                      placeholder="15000"
                      {...register("conversion_rate", { valueAsNumber: true })}
                      className="input"
                    />
                    {errors.conversion_rate && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.conversion_rate.message}
                      </p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      Current rate: 1 USD = {watch("conversion_rate") || 15000}{" "}
                      IDR
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Time Entries Preview */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Time Entries from Clockify
                </h3>
                {loadingPreview ? (
                  <div className="flex justify-center items-center h-24">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="ml-2">Loading time entries...</span>
                  </div>
                ) : timePreview ? (
                  timePreview.entries.length > 0 ? (
                    <div>
                      {/* Summary */}
                      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Total Entries:</span>
                            <div className="text-blue-600 font-bold">
                              {timePreview.entries.length}
                            </div>
                          </div>
                          <div>
                            <span className="font-medium">Included:</span>
                            <div className="text-green-600 font-bold">
                              {getIncludedEntries().length}
                            </div>
                          </div>
                          <div>
                            <span className="font-medium">Total Hours:</span>
                            <div className="text-blue-600 font-bold">
                              {formatHours(
                                getIncludedEntries().reduce(
                                  (sum, entry) =>
                                    sum +
                                    parseFloat(entry.duration.replace("h", "")),
                                  0
                                )
                              )}
                            </div>
                          </div>
                          <div>
                            <span className="font-medium">Total Amount:</span>
                            <div className="text-blue-600 font-bold">
                              {formatCurrency(
                                getIncludedEntries().reduce(
                                  (sum, entry) =>
                                    sum +
                                    entry.total_amount /
                                      (watch("conversion_rate") || 15000),
                                  0
                                ),
                                "USD"
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="mb-4 flex flex-wrap gap-2 items-center">
                        <button
                          type="button"
                          onClick={() => setExcludedEntries(new Set())}
                          className="btn btn-secondary text-sm"
                        >
                          Select All
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            setExcludedEntries(
                              new Set(
                                timePreview.entries.map((e) => e.clockify_id)
                              )
                            )
                          }
                          className="btn btn-secondary text-sm"
                        >
                          Exclude All
                        </button>

                        {/* Filter and Sorting Controls */}
                        <div className="flex flex-wrap items-center gap-2 ml-4">
                          <label className="text-sm font-medium text-gray-700">
                            Filter by date:
                          </label>
                          <input
                            type="date"
                            value={filterDate}
                            onChange={(e) => setFilterDate(e.target.value)}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          />
                          {filterDate && (
                            <button
                              type="button"
                              onClick={() => setFilterDate("")}
                              className="text-sm text-red-600 hover:text-red-800"
                            >
                              Clear
                            </button>
                          )}

                          <div className="border-l border-gray-300 pl-2 ml-2">
                            <label className="text-sm font-medium text-gray-700">
                              Sort by:
                            </label>
                            <select
                              value={sortBy}
                              onChange={(e) => setSortBy(e.target.value as any)}
                              className="text-sm border border-gray-300 rounded px-2 py-1 ml-1"
                            >
                              <option value="start_time">Start Time</option>
                              <option value="project">Project</option>
                              <option value="duration">Duration</option>
                            </select>
                            <button
                              type="button"
                              onClick={() =>
                                setSortOrder(
                                  sortOrder === "asc" ? "desc" : "asc"
                                )
                              }
                              className="text-sm text-blue-600 hover:text-blue-800 px-2 py-1 border border-blue-300 rounded ml-1"
                            >
                              {sortOrder === "asc" ? "↑ ASC" : "↓ DESC"}
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Time Entries Table */}
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Include
                              </th>
                              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Date
                              </th>
                              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Start Time
                              </th>
                              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                End Time
                              </th>
                              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Project
                              </th>
                              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Description
                              </th>
                              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Duration
                              </th>
                              <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                                Amount (USD)
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {getSortedEntries().map((entry, index) => {
                              const isExcluded = excludedEntries.has(
                                entry.clockify_id
                              );

                              // Format start and end times
                              const startTime = new Date(entry.start_time);
                              const endTime = new Date(entry.end_time);

                              const formatTime = (date: Date) => {
                                return date.toLocaleTimeString("id-ID", {
                                  hour: "2-digit",
                                  minute: "2-digit",
                                  hour12: false,
                                });
                              };

                              const formatDateOnly = (date: Date) => {
                                return date.toLocaleDateString("id-ID", {
                                  day: "2-digit",
                                  month: "2-digit",
                                  year: "numeric",
                                });
                              };

                              return (
                                <tr
                                  key={index}
                                  className={`hover:bg-gray-50 ${
                                    isExcluded ? "opacity-50 bg-gray-100" : ""
                                  }`}
                                >
                                  <td className="px-2 py-2">
                                    <input
                                      type="checkbox"
                                      checked={!isExcluded}
                                      onChange={() =>
                                        toggleEntryExclusion(entry.clockify_id)
                                      }
                                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                    />
                                  </td>
                                  <td className="px-2 py-2 text-sm text-gray-900">
                                    {formatDateOnly(startTime)}
                                  </td>
                                  <td className="px-2 py-2 text-sm text-gray-900 font-mono">
                                    {formatTime(startTime)}
                                  </td>
                                  <td className="px-2 py-2 text-sm text-gray-900 font-mono">
                                    {formatTime(endTime)}
                                  </td>
                                  <td className="px-2 py-2 text-sm text-gray-900">
                                    <div
                                      className="max-w-20 truncate"
                                      title={entry.project_name}
                                    >
                                      {entry.project_name}
                                    </div>
                                  </td>
                                  <td className="px-2 py-2 text-sm text-gray-600">
                                    <div
                                      className="max-w-32 truncate"
                                      title={entry.description}
                                    >
                                      {entry.description}
                                    </div>
                                  </td>
                                  <td className="px-2 py-2 text-sm text-gray-900 font-mono">
                                    {entry.duration}
                                  </td>
                                  <td className="px-2 py-2 text-sm text-gray-900 text-right font-mono">
                                    {formatCurrency(
                                      entry.total_amount /
                                        (watch("conversion_rate") || 15000),
                                      "USD"
                                    )}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <p className="text-yellow-800">
                          <strong>No time entries found</strong>
                          <br />
                          Tidak ada time entries untuk periode yang dipilih.
                        </p>
                        <p className="text-yellow-600 text-sm mt-2">
                          Pastikan Anda memiliki time entries di Clockify untuk
                          periode ini, atau periksa konfigurasi Clockify Anda.
                        </p>
                      </div>
                    </div>
                  )
                ) : period_start && period_end ? (
                  <div className="text-center py-8 text-gray-500">
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <p>
                        Pilih periode waktu untuk melihat time entries dari
                        Clockify
                      </p>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>

            {/* Manual Entries */}
            <div className="card">
              <div className="card-body">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Additional Items
                  </h3>
                  <button
                    type="button"
                    onClick={addManualEntry}
                    className="btn btn-secondary"
                  >
                    + Add Item
                  </button>
                </div>

                {fields.length === 0 ? (
                  <div className="text-center py-6 text-gray-500">
                    <p>No additional items added.</p>
                    <button
                      type="button"
                      onClick={addManualEntry}
                      className="btn btn-primary mt-2"
                    >
                      Add First Item
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {fields.map((field, index) => (
                      <div
                        key={field.id}
                        className="p-4 border border-gray-200 rounded-lg"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Description *
                            </label>
                            <input
                              {...register(
                                `manual_entries.${index}.description`
                              )}
                              className="input"
                              placeholder="Item description"
                            />
                            {errors.manual_entries?.[index]?.description && (
                              <p className="text-red-600 text-sm mt-1">
                                {
                                  errors.manual_entries[index]?.description
                                    ?.message
                                }
                              </p>
                            )}
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Quantity *
                            </label>
                            <input
                              type="number"
                              step="0.01"
                              {...register(`manual_entries.${index}.quantity`)}
                              className="input"
                              placeholder="1"
                            />
                            {errors.manual_entries?.[index]?.quantity && (
                              <p className="text-red-600 text-sm mt-1">
                                {
                                  errors.manual_entries[index]?.quantity
                                    ?.message
                                }
                              </p>
                            )}
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Unit Price (IDR) *
                            </label>
                            <input
                              type="number"
                              step="0.01"
                              {...register(
                                `manual_entries.${index}.unit_price`
                              )}
                              className="input"
                              placeholder="0.00"
                            />
                            {errors.manual_entries?.[index]?.unit_price && (
                              <p className="text-red-600 text-sm mt-1">
                                {
                                  errors.manual_entries[index]?.unit_price
                                    ?.message
                                }
                              </p>
                            )}
                          </div>
                        </div>

                        <div className="mt-4 flex justify-between items-center">
                          <div className="text-sm text-gray-600">
                            Total:{" "}
                            {formatCurrency(
                              (watch(`manual_entries.${index}.quantity`) || 0) *
                                (watch(`manual_entries.${index}.unit_price`) ||
                                  0),
                              "IDR"
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => remove(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Invoice Summary */}
          <div className="space-y-6">
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
                      {formatCurrency(getSubtotal(), "USD")}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">
                      Tax ({watch("tax_rate") || 0}%):
                    </span>
                    <span className="font-medium">
                      {formatCurrency(getTaxAmount(), "USD")}
                    </span>
                  </div>
                  <div className="border-t pt-3">
                    <div className="flex justify-between text-lg font-bold">
                      <span>Total (USD):</span>
                      <span>{formatCurrency(getTotal(), "USD")}</span>
                    </div>
                    <div className="flex justify-between text-sm text-gray-600 mt-1">
                      <span>Total (IDR):</span>
                      <span>
                        {formatCurrency(
                          getTotal() * (watch("conversion_rate") || 15000),
                          "IDR"
                        )}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 space-y-3">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="btn btn-primary w-full"
                  >
                    {submitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Creating Invoice...
                      </>
                    ) : (
                      "Create Invoice"
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate("/invoices")}
                    disabled={submitting}
                    className="btn btn-secondary w-full"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default CreateInvoice;
