import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '../test/utils';
import { Navigate } from 'react-router-dom';
import AuthGuard from './AuthGuard';
import useAuthStore from '../stores/authStore';
import { mockUser } from '../test/utils';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Navigate: vi.fn(() => null),
    useLocation: () => ({ pathname: '/dashboard' }),
  };
});

// Mock the auth store
vi.mock('../stores/authStore');

describe('AuthGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show loading spinner when loading', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: false,
      user: null,
      isLoading: true,
    } as ReturnType<typeof useAuthStore>);

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    );

    // Ant Design Spin component has aria-busy and ant-spin class
    const spinner = document.querySelector('[aria-busy="true"]');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('ant-spin-spinning');
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should redirect to login when not authenticated', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: false,
      user: null,
      isLoading: false,
    } as ReturnType<typeof useAuthStore>);

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    );

    expect(Navigate).toHaveBeenCalledWith(
      {
        to: '/login',
        replace: true,
        state: { from: { pathname: '/dashboard' } }
      },
      undefined
    );
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should render children when authenticated', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: true,
      user: mockUser,
      isLoading: false,
    } as ReturnType<typeof useAuthStore>);

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(Navigate).not.toHaveBeenCalled();
  });

  it('should redirect to verify email when email not verified and required', () => {
    const unverifiedUser = { ...mockUser, is_verified: false };
    
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: true,
      user: unverifiedUser,
      isLoading: false,
    } as ReturnType<typeof useAuthStore>);

    render(
      <AuthGuard requireVerified={true}>
        <div>Protected Content</div>
      </AuthGuard>
    );

    expect(Navigate).toHaveBeenCalledWith(
      {
        to: '/verify-email',
        replace: true,
      },
      undefined
    );
  });

  it('should render children when email not verified but not required', () => {
    const unverifiedUser = { ...mockUser, is_verified: false };
    
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: true,
      user: unverifiedUser,
      isLoading: false,
    } as ReturnType<typeof useAuthStore>);

    render(
      <AuthGuard requireVerified={false}>
        <div>Protected Content</div>
      </AuthGuard>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(Navigate).not.toHaveBeenCalled();
  });
});