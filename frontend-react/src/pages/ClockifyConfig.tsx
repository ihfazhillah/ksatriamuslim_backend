import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { toast } from "react-toastify";
import { invoiceAPI } from "../services/api";
import { ClockifyConfigFormData } from "../types";

const schema = yup.object({
  api_key: yup.string().required("API Key is required"),
  workspace_id: yup.string().required("Workspace ID is required"),
  clockify_user_id: yup.string().required("User ID is required"),
  hourly_rate: yup
    .number()
    .positive("Must be positive")
    .required("Hourly rate is required"),
  conversion_rate: yup
    .number()
    .positive("Must be positive")
    .required("Conversion rate is required"),
  company_name: yup.string().required("Company name is required"),
  company_address: yup.string().required("Company address is required"),
  company_phone: yup.string().required("Company phone is required"),
  company_email: yup
    .string()
    .email("Invalid email")
    .required("Company email is required"),
  bank_name: yup.string().required("Bank name is required"),
  bank_account_number: yup.string().required("Bank account number is required"),
  bank_account_name: yup.string().required("Bank account name is required"),
});

const ClockifyConfig: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [isConfigured, setIsConfigured] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isDirty },
  } = useForm<ClockifyConfigFormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      hourly_rate: 25,
      conversion_rate: 16258,
      tax_rate: 11,
    },
  });

  const watchedValues = watch(["api_key", "workspace_id", "clockify_user_id"]);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await invoiceAPI.getClockifyConfig();
      reset(response.data);
      setIsConfigured(true);
    } catch (error: any) {
      if (error.response?.status !== 404) {
        toast.error("Failed to load configuration");
      }
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data: ClockifyConfigFormData) => {
    try {
      setLoading(true);
      const response = await invoiceAPI.createOrUpdateClockifyConfig(data);
      reset(response.data);
      setIsConfigured(true);
      toast.success("Configuration saved successfully!");
    } catch (error: any) {
      toast.error(
        error.response?.data?.message || "Failed to save configuration"
      );
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    const [api_key, workspace_id, clockify_user_id] = watchedValues;

    if (!api_key || !workspace_id || !clockify_user_id) {
      toast.error("Please fill in API Key, Workspace ID, and User ID first");
      return;
    }

    try {
      setTesting(true);
      const response = await invoiceAPI.testClockifyConnection({
        api_key,
        workspace_id,
        clockify_user_id,
      });

      if (response.data.success) {
        toast.success(
          `Connection successful! Found ${response.data.entries_count} time entries`
        );
      } else {
        toast.error(response.data.message);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.message || "Connection test failed");
    } finally {
      setTesting(false);
    }
  };

  if (loading && !isConfigured) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Clockify Configuration
        </h1>
        {isConfigured && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            ✓ Configured
          </span>
        )}
      </div>

      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Clockify API Settings */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Clockify API Settings
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    API Key
                  </label>
                  <input
                    type="password"
                    {...register("api_key")}
                    className="input"
                    placeholder="Your Clockify API Key"
                  />
                  {errors.api_key && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.api_key.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Workspace ID
                  </label>
                  <input
                    type="text"
                    {...register("workspace_id")}
                    className="input"
                    placeholder="Your Workspace ID"
                  />
                  {errors.workspace_id && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.workspace_id.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    User ID
                  </label>
                  <input
                    type="text"
                    {...register("clockify_user_id")}
                    className="input"
                    placeholder="Your Clockify User ID"
                  />
                  {errors.clockify_user_id && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.clockify_user_id.message}
                    </p>
                  )}
                </div>

                <div className="flex items-end">
                  <button
                    type="button"
                    onClick={testConnection}
                    disabled={testing}
                    className="btn btn-secondary w-full"
                  >
                    {testing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Testing...
                      </>
                    ) : (
                      "Test Connection"
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Rate Settings */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Rate Settings
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hourly Rate (USD)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    {...register("hourly_rate")}
                    className="input"
                    placeholder="25.00"
                  />
                  {errors.hourly_rate && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.hourly_rate.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    USD to IDR Conversion Rate
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    {...register("conversion_rate")}
                    className="input"
                    placeholder="16258.00"
                  />
                  {errors.conversion_rate && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.conversion_rate.message}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Company Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Company Information
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company Name
                  </label>
                  <input
                    type="text"
                    {...register("company_name")}
                    className="input"
                    placeholder="Your Company Name"
                  />
                  {errors.company_name && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.company_name.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company Address
                  </label>
                  <textarea
                    {...register("company_address")}
                    rows={3}
                    className="input"
                    placeholder="Your company address"
                  />
                  {errors.company_address && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.company_address.message}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone
                    </label>
                    <input
                      type="text"
                      {...register("company_phone")}
                      className="input"
                      placeholder="+62 xxx xxx xxx"
                    />
                    {errors.company_phone && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.company_phone.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      {...register("company_email")}
                      className="input"
                      placeholder="company@example.com"
                    />
                    {errors.company_email && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.company_email.message}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Bank Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Bank Information
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bank Name
                  </label>
                  <input
                    type="text"
                    {...register("bank_name")}
                    className="input"
                    placeholder="Bank name"
                  />
                  {errors.bank_name && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.bank_name.message}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Account Number
                    </label>
                    <input
                      type="text"
                      {...register("bank_account_number")}
                      className="input"
                      placeholder="Account number"
                    />
                    {errors.bank_account_number && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.bank_account_number.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Account Name
                    </label>
                    <input
                      type="text"
                      {...register("bank_account_name")}
                      className="input"
                      placeholder="Account holder name"
                    />
                    {errors.bank_account_name && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.bank_account_name.message}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-4 pt-6 border-t">
              <button
                type="button"
                onClick={() => reset()}
                disabled={!isDirty || loading}
                className="btn btn-secondary"
              >
                Reset
              </button>
              <button
                type="submit"
                disabled={loading || !isDirty}
                className="btn btn-primary"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Saving...
                  </>
                ) : (
                  "Save Configuration"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ClockifyConfig;
