import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { FullStackClient, LocalStorageTokenStorage, User } from '@fullstack/api-client';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { Dashboard } from './components/Dashboard';
import { Profile } from './components/Profile';
import './App.css';

// Create API client
const apiClient = new FullStackClient({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
}, new LocalStorageTokenStorage());

// API Context
export const ApiContext = React.createContext(apiClient);

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    checkAuth();
  }, []);

  const checkAuth = async () => {
    if (apiClient.isAuthenticated()) {
      try {
        const currentUser = await apiClient.getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error('Auth check failed:', error);
        apiClient.clearTokens();
      }
    }
    setLoading(false);
  };

  const handleLogin = async (username: string, password: string) => {
    await apiClient.login({ username, password });
    const currentUser = await apiClient.getCurrentUser();
    setUser(currentUser);
  };

  const handleLogout = async () => {
    await apiClient.logout();
    setUser(null);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <ApiContext.Provider value={apiClient}>
      <Router>
        <div className="app">
          <header className="app-header">
            <h1>FullStack API Example</h1>
            {user && (
              <div className="user-info">
                <span>Welcome, {user.username}!</span>
                <button onClick={handleLogout}>Logout</button>
              </div>
            )}
          </header>

          <main className="app-main">
            <Routes>
              <Route
                path="/login"
                element={
                  user ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />
                }
              />
              <Route
                path="/register"
                element={
                  user ? <Navigate to="/dashboard" /> : <Register onRegister={handleLogin} />
                }
              />
              <Route
                path="/dashboard"
                element={
                  user ? <Dashboard user={user} /> : <Navigate to="/login" />
                }
              />
              <Route
                path="/profile"
                element={
                  user ? <Profile user={user} onUpdate={checkAuth} /> : <Navigate to="/login" />
                }
              />
              <Route
                path="/"
                element={<Navigate to={user ? "/dashboard" : "/login"} />}
              />
            </Routes>
          </main>
        </div>
      </Router>
    </ApiContext.Provider>
  );
}

export default App;
