import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Typography,
  Switch,
  Button,
  Divider,
  Space,
  Modal,
  Alert,
  notification,
} from "antd";
import {
  BellOutlined,
  MailOutlined,
  SecurityScanOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import useAuthStore from "../stores/authStore";

const { Title, Text, Paragraph } = Typography;
const { confirm } = Modal;

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const { user, deleteAccount } = useAuthStore();
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    updates: true,
    marketing: false,
  });

  const handleDeleteAccount = () => {
    confirm({
      title: "Are you sure you want to delete your account?",
      icon: <ExclamationCircleOutlined />,
      content:
        "This action cannot be undone. All your data will be permanently deleted.",
      okText: "Yes, Delete Account",
      okType: "danger",
      cancelText: "Cancel",
      onOk: async () => {
        try {
          await deleteAccount();
          navigate("/login");
        } catch {
          notification.error({
            message: "Failed to delete account",
            description:
              "An error occurred while deleting your account. Please try again.",
          });
        }
      },
    });
  };

  return (
    <div>
      <div className="mb-6">
        <Title level={2}>Settings</Title>
      </div>

      <Space direction="vertical" size="large" className="w-full">
        {/* Notification Settings */}
        <Card>
          <div className="mb-4">
            <Title level={4}>
              <BellOutlined className="mr-2" />
              Notification Preferences
            </Title>
          </div>

          <Space direction="vertical" size="middle" className="w-full">
            <div className="flex items-center justify-between">
              <div>
                <Text strong>Email Notifications</Text>
                <br />
                <Text type="secondary">Receive notifications via email</Text>
              </div>
              <Switch
                checked={notifications.email}
                onChange={(checked) =>
                  setNotifications({ ...notifications, email: checked })
                }
              />
            </div>

            <Divider className="my-2" />

            <div className="flex items-center justify-between">
              <div>
                <Text strong>Push Notifications</Text>
                <br />
                <Text type="secondary">Receive push notifications</Text>
              </div>
              <Switch
                checked={notifications.push}
                onChange={(checked) =>
                  setNotifications({ ...notifications, push: checked })
                }
              />
            </div>

            <Divider className="my-2" />

            <div className="flex items-center justify-between">
              <div>
                <Text strong>Product Updates</Text>
                <br />
                <Text type="secondary">Get notified about new features</Text>
              </div>
              <Switch
                checked={notifications.updates}
                onChange={(checked) =>
                  setNotifications({ ...notifications, updates: checked })
                }
              />
            </div>

            <Divider className="my-2" />

            <div className="flex items-center justify-between">
              <div>
                <Text strong>Marketing Emails</Text>
                <br />
                <Text type="secondary">Receive promotional emails</Text>
              </div>
              <Switch
                checked={notifications.marketing}
                onChange={(checked) =>
                  setNotifications({ ...notifications, marketing: checked })
                }
              />
            </div>
          </Space>
        </Card>

        {/* Security Settings */}
        <Card>
          <div className="mb-4">
            <Title level={4}>
              <SecurityScanOutlined className="mr-2" />
              Security
            </Title>
          </div>

          <Space direction="vertical" size="middle" className="w-full">
            <div>
              <Text strong>Two-Factor Authentication</Text>
              <br />
              <Text type="secondary">
                Add an extra layer of security to your account
              </Text>
              <br />
              <Button type="primary" className="mt-2" disabled>
                Enable 2FA (Coming Soon)
              </Button>
            </div>

            <Divider className="my-2" />

            <div>
              <Text strong>Active Sessions</Text>
              <br />
              <Text type="secondary">
                Manage your active sessions across devices
              </Text>
              <br />
              <Button className="mt-2" disabled>
                View Sessions (Coming Soon)
              </Button>
            </div>
          </Space>
        </Card>

        {/* Account Settings */}
        <Card>
          <div className="mb-4">
            <Title level={4}>
              <MailOutlined className="mr-2" />
              Account
            </Title>
          </div>

          <Space direction="vertical" size="middle" className="w-full">
            <div>
              <Text strong>Email Verification</Text>
              <br />
              <Text type="secondary">
                Status: {user?.is_verified ? "Verified" : "Not Verified"}
              </Text>
              {!user?.is_verified && (
                <Button type="link" className="p-0 mt-1" disabled>
                  Resend Verification Email (Coming Soon)
                </Button>
              )}
            </div>

            <Divider className="my-2" />

            <div>
              <Text strong>Export Data</Text>
              <br />
              <Text type="secondary">Download a copy of your data</Text>
              <br />
              <Button className="mt-2" disabled>
                Request Data Export (Coming Soon)
              </Button>
            </div>
          </Space>
        </Card>

        {/* Danger Zone */}
        <Card>
          <Alert
            message="Danger Zone"
            description="The following actions are permanent and cannot be undone."
            type="error"
            showIcon
            className="mb-4"
          />

          <div>
            <Title level={5}>
              <DeleteOutlined className="mr-2" />
              Delete Account
            </Title>
            <Paragraph type="secondary">
              Once you delete your account, there is no going back. Please be
              certain.
            </Paragraph>
            <Button danger onClick={handleDeleteAccount}>
              Delete Account
            </Button>
          </div>
        </Card>
      </Space>
    </div>
  );
};

export default Settings;
