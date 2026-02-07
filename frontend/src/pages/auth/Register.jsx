import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message;

      if (err.response?.status === 422) {
        if (Array.isArray(errorMsg)) {
          setError(errorMsg.map(e => e.msg || e.message).join(', '));
        } else {
          setError('Please check your input. Password must be at least 8 characters with uppercase, lowercase, number, and special character.');
        }
      } else if (err.response?.status === 409) {
        setError('Username or email already exists. Please use different credentials.');
      } else if (err.response?.status === 429) {
        setError('Too many registration attempts. Please try again later.');
      } else if (typeof errorMsg === 'object') {
        setError(JSON.stringify(errorMsg));
      } else {
        setError(errorMsg || 'Registration failed. Please check your input.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left – Hero Section */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 text-white flex-col justify-between p-12">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight">
            Photo Classification Platform
          </h1>
          <p className="mt-3 text-primary-200 text-lg">
            AI-powered image analysis for everyone
          </p>
        </div>

        <div className="space-y-6">
          <div className="bg-white/10 rounded-xl p-6 backdrop-blur-sm">
            <h3 className="font-semibold text-lg mb-3">Get started in 3 steps</h3>
            <ol className="space-y-3 text-sm text-primary-100">
              <li className="flex items-center gap-3">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-white/20 flex items-center justify-center font-bold text-xs">1</span>
                Create your account with a secure password
              </li>
              <li className="flex items-center gap-3">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-white/20 flex items-center justify-center font-bold text-xs">2</span>
                Upload a photo with subject metadata
              </li>
              <li className="flex items-center gap-3">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-white/20 flex items-center justify-center font-bold text-xs">3</span>
                View ML classification results instantly
              </li>
            </ol>
          </div>

        </div>

      </div>

      {/* Right – Register Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="max-w-md w-full space-y-8">
          <div className="lg:hidden text-center mb-4">
            <h1 className="text-2xl font-bold text-primary-700">Photo Classification Platform</h1>
          </div>

          <div>
            <h2 className="text-3xl font-bold text-gray-900">Create account</h2>
            <p className="mt-2 text-gray-500">Join the platform and start classifying photos</p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  required
                  autoComplete="name"
                  className="input-field mt-1"
                  placeholder="John Doe"
                  value={formData.full_name}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  autoComplete="username"
                  className="input-field mt-1"
                  placeholder="johndoe"
                  value={formData.username}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                autoComplete="email"
                className="input-field mt-1"
                placeholder="john@example.com"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="new-password"
                className="input-field mt-1"
                placeholder="Min 8 characters"
                value={formData.password}
                onChange={handleChange}
              />
              <p className="mt-1 text-xs text-gray-400">
                Uppercase + lowercase + number + special character (!@#$%^&amp;*)
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3 text-base disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                  Creating account...
                </span>
              ) : 'Create account'}
            </button>

            <p className="text-center text-sm text-gray-500">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-500">
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
