import React, { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { User } from '@fullstack/api-client';
import { ApiContext } from '../App';

interface DashboardProps {
  user: User;
}

export function Dashboard({ user }: DashboardProps) {
  const apiClient = useContext(ApiContext);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const healthData = await apiClient.healthCheck();
      setHealth(healthData);
    } catch (error) {
      console.error('Health check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>User Information</h3>
          <dl>
            <dt>Username:</dt>
            <dd>{user.username}</dd>

            <dt>Email:</dt>
            <dd>{user.email}</dd>

            <dt>Full Name:</dt>
            <dd>{user.full_name || 'Not set'}</dd>

            <dt>Account Status:</dt>
            <dd>
              <span className={`status ${user.is_active ? 'active' : 'inactive'}`}>
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </dd>

            <dt>Email Verified:</dt>
            <dd>
              <span className={`status ${user.is_verified ? 'verified' : 'unverified'}`}>
                {user.is_verified ? 'Yes' : 'No'}
              </span>
            </dd>

            <dt>Member Since:</dt>
            <dd>{new Date(user.created_at).toLocaleDateString()}</dd>
          </dl>

          <Link to="/profile" className="button">Edit Profile</Link>
        </div>

        <div className="dashboard-card">
          <h3>API Status</h3>
          {loading ? (
            <p>Checking API health...</p>
          ) : health ? (
            <dl>
              <dt>Status:</dt>
              <dd>
                <span className={`status ${health.status === 'healthy' ? 'active' : 'inactive'}`}>
                  {health.status}
                </span>
              </dd>

              <dt>Database:</dt>
              <dd>
                <span className={`status ${health.database === 'connected' ? 'active' : 'inactive'}`}>
                  {health.database}
                </span>
              </dd>

              <dt>Version:</dt>
              <dd>{health.version}</dd>
            </dl>
          ) : (
            <p>Unable to fetch API status</p>
          )}
        </div>

        <div className="dashboard-card">
          <h3>Quick Actions</h3>
          <ul className="quick-actions">
            <li>
              <Link to="/profile">Update Profile</Link>
            </li>
            <li>
              <Link to="/profile#password">Change Password</Link>
            </li>
            <li>
              <a href="/api/docs" target="_blank" rel="noopener noreferrer">
                API Documentation
              </a>
            </li>
          </ul>
        </div>

        <div className="dashboard-card">
          <h3>Authentication Info</h3>
          <p>Your session is active and secure.</p>
          <p className="info-text">
            Access tokens expire every 15 minutes and are automatically refreshed.
          </p>
          <details>
            <summary>Technical Details</summary>
            <dl>
              <dt>User ID:</dt>
              <dd className="mono">{user.id}</dd>

              <dt>Is Superuser:</dt>
              <dd>{user.is_superuser ? 'Yes' : 'No'}</dd>

              <dt>Last Updated:</dt>
              <dd>{new Date(user.updated_at).toLocaleString()}</dd>
            </dl>
          </details>
        </div>
      </div>
    </div>
  );
}
