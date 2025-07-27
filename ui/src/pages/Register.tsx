import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Divider, Alert } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import useAuthStore from '../stores/authStore';
import { registerSchema } from '../utils/validation';
import type { RegisterFormData } from '../utils/validation';

const { Title, Text } = Typography;

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading, isAuthenticated, clearError } = useAuthStore();

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      username: '',
      password: '',
      confirmPassword: '',
    },
  });

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    clearError();
  }, [clearError]);

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await register({
        email: data.email,
        username: data.username,
        password: data.password,
      });
      // Redirect to login page after successful registration
      navigate('/login');
    } catch {
      // Error is handled by the store
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-sm" style={{ maxWidth: '360px' }}>
        <div className="text-center mb-6">
          <Title level={2} className="mb-2">Create Account</Title>
          <Text type="secondary">Sign up for a new account</Text>
        </div>

        <Alert
          message="Password Requirements"
          description="At least 8 characters with uppercase, lowercase, and numbers"
          type="info"
          showIcon
          className="mb-4"
        />

        <Form
          layout="vertical"
          onFinish={handleSubmit(onSubmit)}
          autoComplete="off"
        >
          <Controller
            name="email"
            control={control}
            render={({ field }) => (
              <Form.Item
                label="Email"
                validateStatus={errors.email ? 'error' : ''}
                help={errors.email?.message}
              >
                <Input
                  {...field}
                  prefix={<MailOutlined />}
                  placeholder="Enter your email"
                  size="large"
                  autoComplete="email"
                />
              </Form.Item>
            )}
          />

          <Controller
            name="username"
            control={control}
            render={({ field }) => (
              <Form.Item
                label="Username"
                validateStatus={errors.username ? 'error' : ''}
                help={errors.username?.message}
              >
                <Input
                  {...field}
                  prefix={<UserOutlined />}
                  placeholder="Choose a username"
                  size="large"
                  autoComplete="username"
                />
              </Form.Item>
            )}
          />

          <Controller
            name="password"
            control={control}
            render={({ field }) => (
              <Form.Item
                label="Password"
                validateStatus={errors.password ? 'error' : ''}
                help={errors.password?.message}
              >
                <Input.Password
                  {...field}
                  prefix={<LockOutlined />}
                  placeholder="Create a password"
                  size="large"
                  autoComplete="new-password"
                />
              </Form.Item>
            )}
          />

          <Controller
            name="confirmPassword"
            control={control}
            render={({ field }) => (
              <Form.Item
                label="Confirm Password"
                validateStatus={errors.confirmPassword ? 'error' : ''}
                help={errors.confirmPassword?.message}
              >
                <Input.Password
                  {...field}
                  prefix={<LockOutlined />}
                  placeholder="Confirm your password"
                  size="large"
                  autoComplete="new-password"
                />
              </Form.Item>
            )}
          />

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={isLoading}
              block
              size="large"
            >
              Sign Up
            </Button>
          </Form.Item>

          <Divider plain>OR</Divider>

          <div className="text-center">
            <Text>
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-500">
                Sign in
              </Link>
            </Text>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default Register;