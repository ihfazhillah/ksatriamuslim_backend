import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { toast } from "react-toastify";
import { UserPlus, Eye, EyeOff } from "lucide-react";
import { authAPI } from "../services/api";
import { RegisterRequest } from "../types";

const schema = yup.object({
  username: yup.string().required("Username is required"),
  email: yup.string().email("Invalid email").required("Email is required"),
  first_name: yup.string().required("First name is required"),
  last_name: yup.string().required("Last name is required"),
  password1: yup
    .string()
    .min(8, "Password must be at least 8 characters")
    .required("Password is required"),
  password2: yup
    .string()
    .oneOf([yup.ref("password1")], "Passwords must match")
    .required("Confirm password is required"),
});

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterRequest>({
    resolver: yupResolver(schema),
  });

  const onSubmit = async (data: RegisterRequest) => {
    try {
      setLoading(true);
      await authAPI.register(data);
      toast.success("Registration successful! Please log in.");
      navigate("/login");
    } catch (error: any) {
      const message =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Registration failed. Please try again.";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center">
            <UserPlus className="h-8 w-8 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Join us to manage your invoices with Clockify integration
          </p>
        </div>

        <div className="bg-white py-8 px-6 shadow-md rounded-lg">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="first_name"
                  className="block text-sm font-medium text-gray-700"
                >
                  First Name *
                </label>
                <input
                  {...register("first_name")}
                  type="text"
                  className={`mt-1 input ${
                    errors.first_name ? "input-error" : ""
                  }`}
                  placeholder="John"
                />
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.first_name.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="last_name"
                  className="block text-sm font-medium text-gray-700"
                >
                  Last Name *
                </label>
                <input
                  {...register("last_name")}
                  type="text"
                  className={`mt-1 input ${
                    errors.last_name ? "input-error" : ""
                  }`}
                  placeholder="Doe"
                />
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.last_name.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700"
              >
                Username *
              </label>
              <input
                {...register("username")}
                type="text"
                className={`mt-1 input ${errors.username ? "input-error" : ""}`}
                placeholder="johndoe"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.username.message}
                </p>
              )}
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                Email *
              </label>
              <input
                {...register("email")}
                type="email"
                className={`mt-1 input ${errors.email ? "input-error" : ""}`}
                placeholder="john@example.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div>
              <label
                htmlFor="password1"
                className="block text-sm font-medium text-gray-700"
              >
                Password *
              </label>
              <div className="relative mt-1">
                <input
                  {...register("password1")}
                  type={showPassword ? "text" : "password"}
                  className={`input pr-10 ${
                    errors.password1 ? "input-error" : ""
                  }`}
                  placeholder="Create a strong password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password1 && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.password1.message}
                </p>
              )}
            </div>

            <div>
              <label
                htmlFor="password2"
                className="block text-sm font-medium text-gray-700"
              >
                Confirm Password *
              </label>
              <div className="relative mt-1">
                <input
                  {...register("password2")}
                  type={showConfirmPassword ? "text" : "password"}
                  className={`input pr-10 ${
                    errors.password2 ? "input-error" : ""
                  }`}
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password2 && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.password2.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary flex justify-center py-3"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Creating account...
                </div>
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          <div className="mt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Already have an account?{" "}
                <Link
                  to="/login"
                  className="font-medium text-primary-600 hover:text-primary-500"
                >
                  Sign in here
                </Link>
              </p>
            </div>
          </div>
        </div>

        <div className="text-center">
          <p className="text-xs text-gray-500">
            By creating an account, you agree to our Terms of Service and
            Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
