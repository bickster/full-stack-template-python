import { Card, Statistic, Row, Col, Typography, Space, Tag } from 'antd';
import {
  UserOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  SafetyOutlined,
} from '@ant-design/icons';
import useAuthStore from '../stores/authStore';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div>
      <div className="mb-6">
        <Title level={2}>Dashboard</Title>
        <Text type="secondary">Welcome back, {user?.username}!</Text>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Account Status"
              value={user?.is_active ? 'Active' : 'Inactive'}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: user?.is_active ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Email Verified"
              value={user?.is_verified ? 'Yes' : 'No'}
              prefix={<SafetyOutlined />}
              valueStyle={{ color: user?.is_verified ? '#3f8600' : '#faad14' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Member Since"
              value={user?.created_at ? formatDate(user.created_at) : 'N/A'}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Account Type"
              value={user?.is_superuser ? 'Admin' : 'User'}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card className="mt-6">
        <Title level={4}>Account Information</Title>
        <Space direction="vertical" size="middle" className="w-full">
          <div>
            <Text strong>Email:</Text>
            <Text className="ml-2">{user?.email}</Text>
            {!user?.is_verified && (
              <Tag color="warning" className="ml-2">Unverified</Tag>
            )}
          </div>
          <div>
            <Text strong>Username:</Text>
            <Text className="ml-2">{user?.username}</Text>
          </div>
          <div>
            <Text strong>Last Login:</Text>
            <Text className="ml-2">
              {user?.last_login_at ? formatDate(user.last_login_at) : 'N/A'}
            </Text>
          </div>
          <div>
            <Text strong>Account Created:</Text>
            <Text className="ml-2">
              {user?.created_at ? formatDate(user.created_at) : 'N/A'}
            </Text>
          </div>
        </Space>
      </Card>

      <Card className="mt-6">
        <Title level={4}>Quick Stats</Title>
        <Row gutter={[16, 16]}>
          <Col span={8}>
            <div className="text-center">
              <Title level={3} className="mb-0">0</Title>
              <Text type="secondary">Projects</Text>
            </div>
          </Col>
          <Col span={8}>
            <div className="text-center">
              <Title level={3} className="mb-0">0</Title>
              <Text type="secondary">Tasks</Text>
            </div>
          </Col>
          <Col span={8}>
            <div className="text-center">
              <Title level={3} className="mb-0">0</Title>
              <Text type="secondary">Activities</Text>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Dashboard;