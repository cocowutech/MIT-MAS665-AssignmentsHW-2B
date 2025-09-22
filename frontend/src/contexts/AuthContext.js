import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Set up axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get('/api/auth/me');
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/login', {
        email,
        password
      });
      
      const { access_token } = response.data;
      // Verify token immediately to avoid race with axios.defaults
      const userResponse = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      setUser(userResponse.data);
      // Only persist token after successful /me
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      toast.success('Login successful!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      // Ensure we don't keep a bad/old token around
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const register = async (email, password, name, age) => {
    try {
      const response = await axios.post('/api/auth/register', {
        email,
        password,
        name,
        age
      });
      
      const { access_token } = response.data;
      const userResponse = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      setUser(userResponse.data);
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      toast.success('Registration successful!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed';
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    toast.success('Logged out successfully');
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
