import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { toast } from "react-toastify";
import { invoiceAPI } from "../services/api";
import { Client, ClientFormData } from "../types";
import { formatDate, formatClientAddress } from "../utils/format";

const schema = yup.object({
  name: yup.string().required("Name is required"),
  email: yup.string().email("Invalid email").required("Email is required"),
  address_line1: yup.string().required("Address line 1 is required"),
  address_line2: yup.string(),
  address_line3: yup.string(),
  address_line4: yup.string(),
  phone: yup.string(),
});

const Clients: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ClientFormData>({
    resolver: yupResolver(schema),
  });

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      setLoading(true);
      const response = await invoiceAPI.getClients();
      setClients(response.data);
    } catch (error: any) {
      toast.error("Failed to load clients");
    } finally {
      setLoading(false);
    }
  };

  const openModal = (client?: Client) => {
    setEditingClient(client || null);
    reset(client || {});
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingClient(null);
    reset({});
  };

  const onSubmit = async (data: ClientFormData) => {
    try {
      setSubmitting(true);

      if (editingClient) {
        const response = await invoiceAPI.updateClient(editingClient.id, data);
        setClients((prev) =>
          prev.map((client) =>
            client.id === editingClient.id ? response.data : client
          )
        );
        toast.success("Client updated successfully!");
      } else {
        const response = await invoiceAPI.createClient(data);
        setClients((prev) => [...prev, response.data]);
        toast.success("Client created successfully!");
      }

      closeModal();
    } catch (error: any) {
      toast.error(
        error.response?.data?.message ||
          `Failed to ${editingClient ? "update" : "create"} client`
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (client: Client) => {
    if (!window.confirm(`Are you sure you want to delete "${client.name}"?`)) {
      return;
    }

    try {
      await invoiceAPI.deleteClient(client.id);
      setClients((prev) => prev.filter((c) => c.id !== client.id));
      toast.success("Client deleted successfully!");
    } catch (error: any) {
      toast.error("Failed to delete client");
    }
  };

  const filteredClients = clients.filter(
    (client) =>
      client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      client.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Clients</h1>
        <button onClick={() => openModal()} className="btn btn-primary">
          + Add Client
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Search clients by name or email..."
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

      {/* Clients Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredClients.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-500 mb-4">
                {searchTerm
                  ? "No clients found matching your search."
                  : "No clients yet."}
              </div>
              {!searchTerm && (
                <button onClick={() => openModal()} className="btn btn-primary">
                  Add Your First Client
                </button>
              )}
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Phone
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredClients.map((client) => (
                  <tr key={client.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {client.name}
                        </div>
                        <div className="text-sm text-gray-500 max-w-xs truncate">
                          {formatClientAddress(client)}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {client.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {client.phone || "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(client.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => openModal(client)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(client)}
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

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                {editingClient ? "Edit Client" : "Add New Client"}
              </h3>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name *
                  </label>
                  <input
                    type="text"
                    {...register("name")}
                    className="input"
                    placeholder="Client name"
                  />
                  {errors.name && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.name.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    {...register("email")}
                    className="input"
                    placeholder="client@example.com"
                  />
                  {errors.email && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.email.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <input
                    type="text"
                    {...register("phone")}
                    className="input"
                    placeholder="+62 xxx xxx xxx"
                  />
                  {errors.phone && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.phone.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address Line 1 *
                  </label>
                  <input
                    type="text"
                    {...register("address_line1")}
                    className="input"
                    placeholder="Street address"
                  />
                  {errors.address_line1 && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.address_line1.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address Line 2
                  </label>
                  <input
                    type="text"
                    {...register("address_line2")}
                    className="input"
                    placeholder="Suite, unit, etc."
                  />
                  {errors.address_line2 && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.address_line2.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address Line 3
                  </label>
                  <input
                    type="text"
                    {...register("address_line3")}
                    className="input"
                    placeholder="City, State"
                  />
                  {errors.address_line3 && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.address_line3.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address Line 4
                  </label>
                  <input
                    type="text"
                    {...register("address_line4")}
                    className="input"
                    placeholder="Country"
                  />
                  {errors.address_line4 && (
                    <p className="text-red-600 text-sm mt-1">
                      {errors.address_line4.message}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={closeModal}
                  disabled={submitting}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn-primary"
                >
                  {submitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      {editingClient ? "Updating..." : "Creating..."}
                    </>
                  ) : editingClient ? (
                    "Update Client"
                  ) : (
                    "Create Client"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Clients;
