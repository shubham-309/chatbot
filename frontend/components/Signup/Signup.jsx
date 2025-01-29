import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";

const Signup = ({ toggleMode }) => {
  const { register, googleLogin } = useAuth(); // Assuming AuthContext contains register logic
  const [formData, setFormData] = useState({ username: "", email: "", password: "" });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Something went wrong");

      // alert("Registration successful! Please log in.");
      toggleMode();
    } catch (error) {
      console.log("Error:", error.message);
      alert(error.message);
    }
  };

  const handleOAuthLogin = () => {
    googleLogin(); // Use googleLogin from context
  };

  return (
    <div className="w-full max-w-md p-8 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-semibold">Sign up with free trial</h1>
        <p className="text-gray-600 text-sm">Empower your experience, sign up for a free account today</p>
      </div>
      <form className="space-y-4" onSubmit={handleFormSubmit}>
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 text-left">Username*</label>
          <input
            type="text"
            id="username"
            name="username"
            placeholder="Enter your username"
            value={formData.username}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 text-left">Email Address*</label>
          <input
            type="email"
            id="email"
            name="email"
            placeholder="an.email@domain.com"
            value={formData.email}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 text-left">Password*</label>
          <input
            type="password"
            id="password"
            name="password"
            placeholder="Enter password"
            value={formData.password}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2"
        >
          Sign Up
        </button>
      </form>
      <div className="text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{" "}
          <a href="#" className="text-indigo-600" onClick={(e) => toggleMode(e)}>Login</a>
        </p>
        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with Google</span>
          </div>
        </div>
        <button onClick={handleOAuthLogin} className="w-full py-2 px-4 border border-gray-300 rounded-full shadow-sm bg-white text-gray-700 font-semibold flex items-center justify-center hover:bg-gray-50 gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            <path d="M1 1h22v22H1z" fill="none" />
          </svg>
          Continue with Google
        </button>
      </div>
    </div>
  );
};

export default Signup;
