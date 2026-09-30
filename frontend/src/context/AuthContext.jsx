/**
 * Authentication & User Session Context
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('cinematch_token'));
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load current user and summary on mount or token change
  useEffect(() => {
    async function loadUser() {
      if (!token) {
        setUser(null);
        setSummary(null);
        setLoading(false);
        return;
      }
      try {
        const userData = await api.auth.getMe();
        setUser(userData);
        try {
          const sumData = await api.interactions.getSummary();
          setSummary(sumData);
        } catch (e) {
          // ignore summary load error
        }
      } catch (err) {
        console.warn('Session expired or invalid token:', err);
        logout();
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, [token]);

  const refreshSummary = async () => {
    if (!token) return;
    try {
      const sumData = await api.interactions.getSummary();
      setSummary(sumData);
    } catch (e) {
      console.warn('Failed to refresh summary:', e);
    }
  };

  const login = async (usernameOrEmail, password) => {
    const res = await api.auth.login(usernameOrEmail, password);
    localStorage.setItem('cinematch_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    await refreshSummary();
    return res.user;
  };

  const register = async (username, email, password) => {
    const res = await api.auth.register(username, email, password);
    localStorage.setItem('cinematch_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    await refreshSummary();
    return res.user;
  };

  const logout = () => {
    localStorage.removeItem('cinematch_token');
    setToken(null);
    setUser(null);
    setSummary(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        summary,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshSummary,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
