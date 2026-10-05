import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('edunexus_token') || null);
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('edunexus_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(false);

  const login = (tokenData) => {
    const tokenStr = tokenData.access_token;
    const userData = {
      user_id: tokenData.user_id,
      email: tokenData.email,
      full_name: tokenData.full_name,
      role: tokenData.role
    };

    setToken(tokenStr);
    setUser(userData);
    localStorage.setItem('edunexus_token', tokenStr);
    localStorage.setItem('edunexus_user', JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('edunexus_token');
    localStorage.removeItem('edunexus_user');
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, loading, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
