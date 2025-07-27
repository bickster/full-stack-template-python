import { useState } from 'react';
import { Card, Form, Input, Button, Typography, message, Tabs } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined } from '@ant-design/icons';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import useAuthStore from '../stores/authStore';
import {
  updateProfileSchema,
  changePasswordSchema,
  UpdateProfileFormData,
  ChangePasswordFormData,
} from '../utils/validation';

const { Title } = Typography;
const { TabPane } = Tabs;

const Profile: React.FC = () => {
  const { user, updateUser, changePassword, isLoading } = useAuthStore();
  const [activeTab, setActiveTab] = useState('1');

  // Profile form
  const {
    control: profileControl,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
  } = useForm<UpdateProfileFormData>({
    resolver: zodResolver(updateProfileSchema),
    defaultValues: {
      email: user?.email || '',
      username: user?.username || '',
    },
  });

  // Password form
  const {
    control: passwordControl,
    handleSubmit: handlePasswordSubmit,
    reset: resetPasswordForm,
    formState: { errors: passwordErrors },
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
  });

  const onProfileSubmit = async (data: UpdateProfileFormData) => {
    try {
      await updateUser(data);
      message.success('Profile updated successfully');
    } catch {
      // Error is handled by the store
    }
  };

  const onPasswordSubmit = async (data: ChangePasswordFormData) => {
    try {
      await changePassword({
        current_password: data.currentPassword,
        new_password: data.newPassword,
      });
      resetPasswordForm();
      message.success('Password changed successfully');
    } catch {
      // Error is handled by the store
    }
  };

  return (
    <div>
      <div className="mb-6">
        <Title level={2}>Profile</Title>
      </div>

      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="Profile Information" key="1">
            <Form
              layout="vertical"
              onFinish={handleProfileSubmit(onProfileSubmit)}
              className="max-w-md"
            >
              <Controller
                name="email"
                control={profileControl}
                render={({ field }) => (
                  <Form.Item
                    label="Email"
                    validateStatus={profileErrors.email ? 'error' : ''}
                    help={profileErrors.email?.message}
                  >
                    <Input
                      {...field}
                      prefix={<MailOutlined />}
                      placeholder="Enter your email"
                      size="large"
                    />
                  </Form.Item>
                )}
              />

              <Controller
                name="username"
                control={profileControl}
                render={({ field }) => (
                  <Form.Item
                    label="Username"
                    validateStatus={profileErrors.username ? 'error' : ''}
                    help={profileErrors.username?.message}
                  >
                    <Input
                      {...field}
                      prefix={<UserOutlined />}
                      placeholder="Enter your username"
                      size="large"
                    />
                  </Form.Item>
                )}
              />

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isLoading}
                  size="large"
                >
                  Update Profile
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="Change Password" key="2">
            <Form
              layout="vertical"
              onFinish={handlePasswordSubmit(onPasswordSubmit)}
              className="max-w-md"
            >
              <Controller
                name="currentPassword"
                control={passwordControl}
                render={({ field }) => (
                  <Form.Item
                    label="Current Password"
                    validateStatus={passwordErrors.currentPassword ? 'error' : ''}
                    help={passwordErrors.currentPassword?.message}
                  >
                    <Input.Password
                      {...field}
                      prefix={<LockOutlined />}
                      placeholder="Enter current password"
                      size="large"
                    />
                  </Form.Item>
                )}
              />

              <Controller
                name="newPassword"
                control={passwordControl}
                render={({ field }) => (
                  <Form.Item
                    label="New Password"
                    validateStatus={passwordErrors.newPassword ? 'error' : ''}
                    help={passwordErrors.newPassword?.message}
                  >
                    <Input.Password
                      {...field}
                      prefix={<LockOutlined />}
                      placeholder="Enter new password"
                      size="large"
                    />
                  </Form.Item>
                )}
              />

              <Controller
                name="confirmPassword"
                control={passwordControl}
                render={({ field }) => (
                  <Form.Item
                    label="Confirm New Password"
                    validateStatus={passwordErrors.confirmPassword ? 'error' : ''}
                    help={passwordErrors.confirmPassword?.message}
                  >
                    <Input.Password
                      {...field}
                      prefix={<LockOutlined />}
                      placeholder="Confirm new password"
                      size="large"
                    />
                  </Form.Item>
                )}
              />

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isLoading}
                  size="large"
                >
                  Change Password
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default Profile;