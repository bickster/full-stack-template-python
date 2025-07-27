# Full-Stack Application Template

A production-ready full-stack application template with JWT authentication, FastAPI backend, React frontend, and PostgreSQL database.

## Features

- 🔐 **JWT Authentication** with access/refresh tokens
- 🚀 **FastAPI Backend** with async/await support
- ⚛️ **React 18 + TypeScript** frontend with Vite
- 🗄️ **PostgreSQL** database with SQLAlchemy ORM
- 🐳 **Docker** containerization with docker-compose
- 📦 **Client SDKs** for Python and TypeScript
- 🧪 **Comprehensive Testing** setup with pytest and Jest
- 🔄 **CI/CD Pipeline** with GitHub Actions
- 📊 **Monitoring** with Prometheus metrics
- 🛡️ **Security Best Practices** implemented

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy 2.0
- Alembic (migrations)
- PostgreSQL
- JWT authentication
- Pydantic
- Structlog

### Frontend
- React 18
- TypeScript
- Vite
- Zustand (state management)
- React Router v6
- Axios
- Ant Design + TailwindCSS
- React Hook Form + Zod

### DevOps
- Docker & Docker Compose
- nginx
- GitHub Actions
- Pre-commit hooks

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Make (optional but recommended)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd fullstack-template
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Set up development environment:
```bash
make setup-dev
```

This will:
- Install all dependencies
- Start Docker containers
- Run database migrations
- Set up pre-commit hooks

### Development

Run the backend:
```bash
make serve-api
```

Run the frontend (in another terminal):
```bash
make serve-frontend
```

Access the application:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- API Reference: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

## Project Structure

```
fullstack-template/
├── src/app/              # Backend application
│   ├── api/             # API endpoints
│   ├── core/            # Core functionality
│   ├── db/              # Database models
│   └── cli/             # CLI commands
├── ui/                   # Frontend application
│   ├── src/             # React source code
│   └── public/          # Static assets
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── functional/     # E2E tests
├── docker/              # Docker configurations
├── alembic/             # Database migrations
├── client-sdk/          # Client libraries
│   ├── python/         # Python SDK
│   └── typescript/     # TypeScript SDK
└── scripts/             # Utility scripts
```

## Common Commands

### Development
- `make install-dev` - Install all dependencies
- `make serve-api` - Run backend server
- `make serve-frontend` - Run frontend server
- `make format` - Format code
- `make lint` - Run linters
- `make type-check` - Run type checking

### Testing
- `make test` - Run all tests
- `make test-cov` - Run tests with coverage
- `make test-unit` - Run unit tests only
- `make test-integration` - Run integration tests only

### Database
- `make migrate` - Run migrations
- `make migrate-create` - Create new migration
- `make db-shell` - Open database shell

### Docker
- `make docker-up` - Start all services
- `make docker-down` - Stop all services
- `make docker-logs` - View logs
- `make docker-build` - Build images

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout (revoke refresh token)

### User Management
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete account

## Security

- JWT tokens with short expiration (15 min access, 30 days refresh)
- Password hashing with bcrypt (12 rounds)
- Rate limiting on authentication endpoints
- CORS configuration
- Security headers (CSP, HSTS, etc.)
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy
- XSS protection

## Testing

The project includes comprehensive testing:

- **Unit Tests**: Test individual components
- **Integration Tests**: Test API endpoints
- **Functional Tests**: End-to-end testing

Run tests with coverage:
```bash
make test-cov
```

Coverage requirements:
- Overall: 80% minimum
- Core business logic: 90% minimum
- Security functions: 95% minimum

## Deployment

### Using Docker Compose

1. Build images:
```bash
make docker-build
```

2. Start services:
```bash
make docker-up
```

### Production Deployment

See `docs/deployment.md` for detailed production deployment instructions.

## Implementation Status

This template follows a 10-phase implementation plan. **All phases must be completed** for a production-ready deployment:

### Phase Completion Checklist
- [x] Phase 1: Project Foundation
- [x] Phase 2: Database & Models
- [x] Phase 3: Backend Core & Security
- [x] Phase 4: Authentication API
- [x] Phase 5: Frontend Foundation
- [x] Phase 6: Frontend Auth Features
- [x] Phase 7: Testing Setup
- [x] Phase 8: Development Tools & Code Quality
- [x] Phase 9: Production Deployment
- [x] Phase 10: Client SDKs & Documentation ✅

### Client SDKs

Official SDKs are now available for easy API integration:

#### Python SDK

**Installation:**
```bash
pip install fullstack-api-client
```

**Usage:**
```python
from fullstack_api import Client

# Initialize client
client = Client(base_url="https://api.example.com")

# Login
tokens = client.auth.login(username="user@example.com", password="password")

# Access protected resources
user = client.users.get_current_user()
print(f"Logged in as: {user.email}")
```

**Features:**
- Automatic token management
- Type hints with Pydantic models
- Sync and async support
- Comprehensive error handling

[Full Python SDK Documentation](client-sdk/python/README.md)

#### TypeScript/JavaScript SDK

**Installation:**
```bash
npm install @fullstack/api-client
# or
yarn add @fullstack/api-client
```

**Usage:**
```typescript
import { FullStackClient } from '@fullstack/api-client';

// Initialize client
const client = new FullStackClient({
  baseUrl: 'https://api.example.com'
});

// Login
const tokens = await client.auth.login({
  username: 'user@example.com',
  password: 'password'
});

// Access protected resources
const user = await client.users.getCurrentUser();
console.log(`Logged in as: ${user.email}`);
```

**Features:**
- Full TypeScript support
- Automatic token refresh
- Request/response interceptors
- Multiple storage options

[Full TypeScript SDK Documentation](client-sdk/typescript/README.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details