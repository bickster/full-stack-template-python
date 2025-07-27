/**
 * Advanced usage example for the Full-Stack API TypeScript SDK
 */

import {
  FullStackClient,
  LocalStorageTokenStorage,
  SessionStorageTokenStorage,
  Token,
  User,
} from '@fullstack/api-client';

// Custom token storage implementation
class SecureTokenStorage implements TokenStorage {
  private encryptionKey: string;

  constructor(key: string) {
    this.encryptionKey = key;
  }

  private encrypt(data: string): string {
    // In a real implementation, use proper encryption
    return btoa(data);
  }

  private decrypt(data: string): string {
    // In a real implementation, use proper decryption
    return atob(data);
  }

  async getToken(): Promise<Token | null> {
    const encrypted = localStorage.getItem('secure_token');
    if (!encrypted) return null;

    try {
      const decrypted = this.decrypt(encrypted);
      return JSON.parse(decrypted);
    } catch {
      return null;
    }
  }

  async setToken(token: Token): Promise<void> {
    const encrypted = this.encrypt(JSON.stringify(token));
    localStorage.setItem('secure_token', encrypted);
  }

  async removeToken(): Promise<void> {
    localStorage.removeItem('secure_token');
  }
}

// Example: Using custom token storage
async function demonstrateCustomStorage() {
  console.log('Using custom token storage...');

  const client = new FullStackClient({
    baseUrl: 'http://localhost:8000',
    tokenStorage: new SecureTokenStorage('my-secret-key'),
  });

  // Tokens will be encrypted before storage
  await client.auth.login({
    username: 'demo@example.com',
    password: 'DemoPass123!',
  });

  console.log('✓ Tokens stored securely');
}

// Example: Different storage strategies
async function demonstrateStorageStrategies() {
  console.log('\nDemonstrating storage strategies...');

  // Memory storage (default) - tokens lost on page refresh
  const memoryClient = new FullStackClient({
    baseUrl: 'http://localhost:8000',
  });

  // Local storage - tokens persist across sessions
  const localClient = new FullStackClient({
    baseUrl: 'http://localhost:8000',
    tokenStorage: new LocalStorageTokenStorage(),
  });

  // Session storage - tokens persist only for the session
  const sessionClient = new FullStackClient({
    baseUrl: 'http://localhost:8000',
    tokenStorage: new SessionStorageTokenStorage(),
  });

  console.log('✓ Multiple storage strategies configured');
}

// Example: Request/Response interceptors
async function demonstrateInterceptors() {
  console.log('\nDemonstrating interceptors...');

  const client = new FullStackClient({
    baseUrl: 'http://localhost:8000',
  });

  // Add logging interceptor
  const requestLogger = client.addRequestInterceptor((config) => {
    console.log(`→ ${config.method?.toUpperCase()} ${config.url}`);
    console.log('  Headers:', config.headers);
    if (config.data) {
      console.log('  Body:', config.data);
    }
    return config;
  });

  const responseLogger = client.addResponseInterceptor({
    onFulfilled: (response) => {
      console.log(`← ${response.status} ${response.config.url}`);
      console.log('  Data:', response.data);
      return response;
    },
    onRejected: (error) => {
      if (error.response) {
        console.error(`← ${error.response.status} ${error.config.url}`);
        console.error('  Error:', error.response.data);
      }
      return Promise.reject(error);
    },
  });

  // Add performance monitoring
  const performanceInterceptor = client.addRequestInterceptor((config) => {
    config.metadata = { startTime: new Date() };
    return config;
  });

  const performanceLogger = client.addResponseInterceptor({
    onFulfilled: (response) => {
      const duration = new Date().getTime() - response.config.metadata.startTime.getTime();
      console.log(`  Duration: ${duration}ms`);
      return response;
    },
  });

  // Make a request to see interceptors in action
  try {
    await client.auth.login({
      username: 'demo@example.com',
      password: 'DemoPass123!',
    });
  } catch {
    // Ignore errors for demo
  }

  // Clean up interceptors
  client.removeRequestInterceptor(requestLogger);
  client.removeRequestInterceptor(performanceInterceptor);
  client.removeResponseInterceptor(responseLogger);
  client.removeResponseInterceptor(performanceLogger);

  console.log('✓ Interceptors demonstrated');
}

// Example: Token refresh callback
async function demonstrateTokenRefreshCallback() {
  console.log('\nDemonstrating token refresh callback...');

  let refreshCount = 0;

  const client = new FullStackClient({
    baseUrl: 'http://localhost:8000',
    onTokenRefresh: (tokens) => {
      refreshCount++;
      console.log(`✓ Token refreshed (${refreshCount} times)`);
      console.log(`  New access token expires in: ${tokens.expiresIn}s`);
      
      // You could sync tokens to other tabs/windows here
      window.postMessage({ type: 'token-refresh', tokens }, '*');
    },
  });

  // Login
  await client.auth.login({
    username: 'demo@example.com',
    password: 'DemoPass123!',
  });

  // Manually trigger refresh
  await client.auth.refreshToken();

  console.log(`✓ Total refreshes: ${refreshCount}`);
}

// Example: Parallel requests
async function demonstrateParallelRequests() {
  console.log('\nDemonstrating parallel requests...');

  const client = new FullStackClient({
    baseUrl: 'http://localhost:8000',
  });

  await client.auth.login({
    username: 'demo@example.com',
    password: 'DemoPass123!',
  });

  console.time('parallel');
  
  // Make multiple requests in parallel
  const [user1, user2, user3] = await Promise.all([
    client.users.getCurrentUser(),
    client.users.getCurrentUser(),
    client.users.getCurrentUser(),
  ]);

  console.timeEnd('parallel');
  console.log('✓ Made 3 parallel requests');
}

// Example: Request cancellation with cleanup
async function demonstrateAdvancedCancellation() {
  console.log('\nDemonstrating advanced cancellation...');

  const client = new FullStackClient({
    baseUrl: 'http://localhost:8000',
  });

  // Create multiple abort controllers
  const controllers = Array.from({ length: 5 }, () => new AbortController());

  // Start multiple requests
  const promises = controllers.map((controller, i) =>
    client.users.getCurrentUser({
      signal: controller.signal,
    }).catch(error => {
      if (error.name === 'CanceledError') {
        console.log(`  Request ${i + 1} cancelled`);
      }
      return null;
    })
  );

  // Cancel some requests
  controllers[0].abort();
  controllers[2].abort();
  controllers[4].abort();

  // Wait for all to complete/cancel
  await Promise.all(promises);

  console.log('✓ Selective cancellation completed');
}

// Example: Type-safe error handling
async function demonstrateTypeSafeErrorHandling() {
  console.log('\nDemonstrating type-safe error handling...');

  const client = new FullStackClient({
    baseUrl: 'http://localhost:8000',
  });

  // Helper function with proper typing
  async function loginSafe(
    username: string,
    password: string
  ): Promise<{ success: true; tokens: Token } | { success: false; error: string }> {
    try {
      const tokens = await client.auth.login({ username, password });
      return { success: true, tokens };
    } catch (error) {
      if (error instanceof Error) {
        return { success: false, error: error.message };
      }
      return { success: false, error: 'Unknown error' };
    }
  }

  const result = await loginSafe('demo@example.com', 'wrong-password');
  
  if (result.success) {
    console.log('✓ Login successful');
  } else {
    console.log(`✓ Login failed safely: ${result.error}`);
  }
}

async function main() {
  console.log('Advanced Usage Examples');
  console.log('='.repeat(50));

  try {
    await demonstrateCustomStorage();
    await demonstrateStorageStrategies();
    await demonstrateInterceptors();
    await demonstrateTokenRefreshCallback();
    await demonstrateParallelRequests();
    await demonstrateAdvancedCancellation();
    await demonstrateTypeSafeErrorHandling();
  } catch (error) {
    console.error(`\n✗ Unexpected error: ${error}`);
  }

  console.log('\n✓ Advanced examples completed');
}

// Run the example
main().catch(console.error);