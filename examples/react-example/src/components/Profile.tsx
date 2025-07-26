import React, { useState, useContext } from 'react';
import { User, UpdateUserRequest, ChangePasswordRequest, AxiosError } from '@fullstack/api-client';
import { ApiContext } from '../App';

interface ProfileProps {
  user: User;
  onUpdate: () => void;
}

export function Profile({ user, onUpdate }: ProfileProps) {
  const apiClient = useContext(ApiContext);
  const [activeTab, setActiveTab] = useState('info');
  
  // Profile form state
  const [profileData, setProfileData] = useState({
    email: user.email,
    username: user.username,
    fullName: user.full_name || ''
  });
  
  // Password form state
  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      const updateData: UpdateUserRequest = {};
      
      if (profileData.email !== user.email) {
        updateData.email = profileData.email;
      }
      if (profileData.username !== user.username) {
        updateData.username = profileData.username;
      }
      if (profileData.fullName !== (user.full_name || '')) {
        updateData.full_name = profileData.fullName || undefined;
      }

      if (Object.keys(updateData).length === 0) {
        setMessage('No changes to save');
        setLoading(false);
        return;
      }

      await apiClient.updateCurrentUser(updateData);
      setMessage('Profile updated successfully');
      onUpdate(); // Refresh user data
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.error || 'Update failed');
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    setMessage('');
    setError('');

    try {
      await apiClient.changePassword({
        old_password: passwordData.oldPassword,
        new_password: passwordData.newPassword
      });
      
      setMessage('Password changed successfully');
      setPasswordData({
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (err) {
      if (err instanceof AxiosError) {
        const errorData = err.response?.data;
        if (errorData?.code === 'INVALID_PASSWORD') {
          setError('Current password is incorrect');
        } else {
          setError(errorData?.error || 'Password change failed');
        }
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    const password = prompt('Please enter your password to confirm account deletion:');
    if (!password) return;

    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    try {
      await apiClient.deleteAccount(password);
      window.location.href = '/';
    } catch (err) {
      if (err instanceof AxiosError) {
        alert(err.response?.data?.error || 'Account deletion failed');
      } else {
        alert('An unexpected error occurred');
      }
      setLoading(false);
    }
  };

  return (
    <div className="profile">
      <h2>Profile Settings</h2>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          Profile Information
        </button>
        <button 
          className={`tab ${activeTab === 'password' ? 'active' : ''}`}
          onClick={() => setActiveTab('password')}
        >
          Change Password
        </button>
        <button 
          className={`tab ${activeTab === 'danger' ? 'active' : ''}`}
          onClick={() => setActiveTab('danger')}
        >
          Danger Zone
        </button>
      </div>

      {message && <div className="success-message">{message}</div>}
      {error && <div className="error-message">{error}</div>}

      {activeTab === 'info' && (
        <form onSubmit={handleProfileSubmit} className="profile-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={profileData.email}
              onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={profileData.username}
              onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              id="fullName"
              type="text"
              value={profileData.fullName}
              onChange={(e) => setProfileData({ ...profileData, fullName: e.target.value })}
              disabled={loading}
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      )}

      {activeTab === 'password' && (
        <form onSubmit={handlePasswordSubmit} className="profile-form">
          <div className="form-group">
            <label htmlFor="oldPassword">Current Password</label>
            <input
              id="oldPassword"
              type="password"
              value={passwordData.oldPassword}
              onChange={(e) => setPasswordData({ ...passwordData, oldPassword: e.target.value })}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">New Password</label>
            <input
              id="newPassword"
              type="password"
              value={passwordData.newPassword}
              onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
              required
              disabled={loading}
            />
            <small>Must be at least 8 characters with uppercase, lowercase, number, and special character</small>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={passwordData.confirmPassword}
              onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
              required
              disabled={loading}
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      )}

      {activeTab === 'danger' && (
        <div className="danger-zone">
          <h3>Delete Account</h3>
          <p>
            Once you delete your account, there is no going back. Please be certain.
          </p>
          <button 
            className="danger-button" 
            onClick={handleDeleteAccount}
            disabled={loading}
          >
            Delete Account
          </button>
        </div>
      )}
    </div>
  );
}