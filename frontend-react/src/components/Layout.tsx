import React, { useState } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Settings,
  Users,
  FileText,
  Plus,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import { toast } from "react-toastify";
import { authAPI, authHelpers } from "../services/api";

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      authHelpers.clearTokens();
      toast.success("Logged out successfully");
      navigate("/login");
    } catch (error) {
      // Even if logout fails on server, clear local tokens
      authHelpers.clearTokens();
      navigate("/login");
    }
  };

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Invoices", href: "/invoices", icon: FileText },
    { name: "Clients", href: "/clients", icon: Users },
    { name: "Configuration", href: "/config", icon: Settings },
  ];

  const isActivePath = (path: string) => {
    return (
      location.pathname === path || location.pathname.startsWith(path + "/")
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="fixed inset-0 bg-gray-600 bg-opacity-75"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="relative flex w-full max-w-xs flex-1 flex-col bg-white">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-6 w-6 text-white" />
              </button>
            </div>
            <SidebarContent
              navigation={navigation}
              isActivePath={isActivePath}
              onLogout={handleLogout}
            />
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <SidebarContent
          navigation={navigation}
          isActivePath={isActivePath}
          onLogout={handleLogout}
        />
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <button
              type="button"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate("/invoices/create")}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>Create Invoice</span>
              </button>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

const SidebarContent: React.FC<{
  navigation: Array<{ name: string; href: string; icon: any }>;
  isActivePath: (path: string) => boolean;
  onLogout: () => void;
}> = ({ navigation, isActivePath, onLogout }) => {
  const navigate = useNavigate();

  return (
    <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4">
      <div className="flex h-16 shrink-0 items-center">
        <h1 className="text-xl font-bold text-gray-900">Invoice Manager</h1>
      </div>
      <nav className="flex flex-1 flex-col">
        <ul role="list" className="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" className="-mx-2 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.name}>
                    <button
                      onClick={() => navigate(item.href)}
                      className={`
                        group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold w-full text-left
                        ${
                          isActivePath(item.href)
                            ? "bg-primary-50 text-primary-600"
                            : "text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                        }
                      `}
                    >
                      <Icon className="h-6 w-6 shrink-0" />
                      {item.name}
                    </button>
                  </li>
                );
              })}
            </ul>
          </li>
          <li className="mt-auto">
            <button
              onClick={onLogout}
              className="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-gray-700 hover:bg-gray-50 hover:text-primary-600 w-full text-left"
            >
              <LogOut className="h-6 w-6 shrink-0" />
              Logout
            </button>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Layout;
