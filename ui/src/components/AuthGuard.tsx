import { Navigate, useLocation } from "react-router-dom";
import { Spin } from "antd";
import useAuthStore from "../stores/authStore";

interface AuthGuardProps {
  children: React.ReactNode;
  requireVerified?: boolean;
}

const AuthGuard: React.FC<AuthGuardProps> = ({
  children,
  requireVerified = false,
}) => {
  const location = useLocation();
  const { isAuthenticated, user, isLoading } = useAuthStore();

  // Show loading spinner while checking auth state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check email verification if required
  if (requireVerified && !user.is_verified) {
    return <Navigate to="/verify-email" replace />;
  }

  return <>{children}</>;
};

export default AuthGuard;
