# FullStack React Example

This is a complete example React application demonstrating how to use the FullStack API client.

## Features

- ✅ User registration and login
- ✅ Automatic token refresh
- ✅ Protected routes
- ✅ Profile management
- ✅ Password change
- ✅ Account deletion
- ✅ API health monitoring
- ✅ Error handling
- ✅ Form validation

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

3. Build the TypeScript SDK (from root directory):
```bash
cd ../../sdk/typescript
npm install
npm run build
```

4. Start the development server:
```bash
npm run dev
```

## Project Structure

```
src/
├── components/         # React components
│   ├── Login.tsx      # Login form
│   ├── Register.tsx   # Registration form
│   ├── Dashboard.tsx  # User dashboard
│   └── Profile.tsx    # Profile management
├── App.tsx            # Main application
├── App.css            # Styles
└── main.tsx          # Entry point
```

## Key Concepts

### API Client Setup

The API client is initialized once and shared via React Context:

```typescript
const apiClient = new FullStackClient({
  baseURL: import.meta.env.VITE_API_URL
}, new LocalStorageTokenStorage());

export const ApiContext = React.createContext(apiClient);
```

### Authentication State

Authentication state is managed at the App level:

```typescript
const [user, setUser] = useState<User | null>(null);

// Check auth on mount
useEffect(() => {
  if (apiClient.isAuthenticated()) {
    apiClient.getCurrentUser()
      .then(setUser)
      .catch(() => apiClient.clearTokens());
  }
}, []);
```

### Protected Routes

Routes are protected using conditional rendering:

```typescript
<Route 
  path="/dashboard" 
  element={
    user ? <Dashboard user={user} /> : <Navigate to="/login" />
  } 
/>
```

### Error Handling

All API errors are caught and displayed to users:

```typescript
try {
  await apiClient.login({ username, password });
} catch (err) {
  if (err instanceof AxiosError) {
    const errorData = err.response?.data;
    setError(errorData?.error || 'Login failed');
  }
}
```

### Form Validation

Client-side validation provides immediate feedback:

```typescript
if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
  errors.email = 'Invalid email address';
}

if (formData.password.length < 8) {
  errors.password = 'Password must be at least 8 characters';
}
```

## Components

### Login Component
- Username/password authentication
- Error handling with specific messages
- Rate limit detection
- Link to registration

### Register Component
- Full registration form with validation
- Password strength requirements
- Auto-login after registration
- Field-specific error messages

### Dashboard Component
- User information display
- API health status
- Quick action links
- Technical details view

### Profile Component
- Tabbed interface
- Profile information editing
- Password change functionality
- Account deletion with confirmation

## Styling

Basic CSS is provided in `App.css`. The application uses:
- CSS Grid for dashboard layout
- Flexbox for forms
- CSS custom properties for theming
- Responsive design patterns

## Best Practices Demonstrated

1. **Centralized API client** - Single instance shared via context
2. **Token persistence** - Using LocalStorage for demo (use secure storage in production)
3. **Automatic token refresh** - Handled by the SDK
4. **Loading states** - Show feedback during API calls
5. **Error boundaries** - Graceful error handling
6. **Form validation** - Client-side validation before API calls
7. **Type safety** - Full TypeScript support

## Production Considerations

For production use:
1. Use secure token storage (httpOnly cookies)
2. Implement proper error boundaries
3. Add analytics and monitoring
4. Implement lazy loading for routes
5. Add comprehensive testing
6. Use environment-specific configurations
7. Implement proper logging