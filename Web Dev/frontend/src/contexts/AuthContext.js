import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerUser, logoutUser, getCurrentUser } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const userData = await getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (err) {
      console.error('Auth status check failed:', err);
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      const { token, user: userData } = await loginUser(email, password);
      localStorage.setItem('token', token);
      setUser(userData);
      setIsAuthenticated(true);
      return userData;
    } catch (err) {
      setError(err.message || 'Login failed');
      throw err;
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      const { token, user: newUser } = await registerUser(userData);
      localStorage.setItem('token', token);
      setUser(newUser);
      setIsAuthenticated(true);
      return newUser;
    } catch (err) {
      setError(err.message || 'Registration failed');
      throw err;
    }
  };

  const logout = async () => {
    try {
      await logoutUser();
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  const updateUser = (updatedUserData) => {
    setUser(prev => ({ ...prev, ...updatedUserData }));
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
}; 