import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout({ children }) {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navLink = (to, label) => {
    const active = location.pathname === to;
    return (
      <Link
        key={to}
        to={to}
        onClick={() => setMobileOpen(false)}
        className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          active
            ? 'bg-primary-50 text-primary-700'
            : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
        }`}
      >
        {label}
      </Link>
    );
  };

  const userLinks = [
    ['/dashboard', 'Dashboard'],
    ['/upload', 'Upload'],
  ];

  const adminLinks = [
    ['/admin/submissions', 'Submissions'],
    ['/admin/analytics', 'Analytics'],
    ['/admin/audit-logs', 'Audit Logs'],
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Left: logo + desktop links */}
            <div className="flex items-center">
              <Link to="/dashboard" className="flex items-center gap-2 mr-8">
                <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                </div>
                <span className="text-lg font-bold text-gray-900 hidden sm:inline">Photo Platform</span>
              </Link>

              <div className="hidden md:flex items-center space-x-1">
                {userLinks.map(([to, label]) => navLink(to, label))}
                {isAdmin && (
                  <>
                    <span className="mx-2 h-5 w-px bg-gray-200" />
                    {adminLinks.map(([to, label]) => navLink(to, label))}
                  </>
                )}
              </div>
            </div>

            {/* Right: user info + logout */}
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">
                  {user?.full_name || user?.username}
                </span>
                {isAdmin && (
                  <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-primary-100 text-primary-700 rounded">
                    Admin
                  </span>
                )}
              </div>
              <button onClick={handleLogout} className="btn-secondary text-sm">
                Logout
              </button>

              {/* Mobile hamburger */}
              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="md:hidden p-2 rounded-md text-gray-500 hover:bg-gray-100"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {mobileOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden border-t border-gray-100 px-4 py-3 space-y-1 bg-white shadow-lg">
            {userLinks.map(([to, label]) => navLink(to, label))}
            {isAdmin && (
              <>
                <div className="border-t border-gray-100 my-2" />
                {adminLinks.map(([to, label]) => navLink(to, label))}
              </>
            )}
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
