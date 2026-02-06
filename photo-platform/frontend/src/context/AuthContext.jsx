import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../lib/api';
import { STORAGE_KEYS, USER_ROLES } from '../lib/constants';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    if (token) {
      try {
        const response = await authAPI.getMe();
        // Backend returns: { success, message, data: { id, email, username, role, ... } }
        const userData = response.data?.data || response.data;
        setUser(userData);
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        setUser(null);
      }
    }
    setLoading(false);
  };

  const login = async (username, password) => {
    const response = await authAPI.login({ username, password });
    // Backend returns: { success, message, data: { access_token, refresh_token, ... } }
    const tokens = response.data?.data || response.data;
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access_token);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh_token);
    await checkAuth();
    return response.data;
  };

  const register = async (data) => {
    const response = await authAPI.register(data);
    // Backend returns: { success, message, data: { user, access_token, refresh_token, ... } }
    const payload = response.data?.data || response.data;
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, payload.access_token);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, payload.refresh_token);
    await checkAuth();
    return response.data;
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // Logout should always succeed client-side even if server call fails
      console.error('Logout API error (ignored):', error);
    }
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    setUser(null);
  };

  const isAdmin = user?.role === USER_ROLES.ADMIN;

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
