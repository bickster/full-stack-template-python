/**
 * Basic usage example for the Full-Stack API TypeScript SDK
 */

import { FullStackClient, AuthError, ValidationError } from '@fullstack/api-client';

async function main() {
  // Initialize client
  const client = new FullStackClient({
    baseUrl: 'http://localhost:8000',
  });

  try {
    // Register a new user
    console.log('Registering new user...');
    try {
      const user = await client.auth.register({
        email: 'demo@example.com',
        username: 'demo_user',
        password: 'DemoPass123!',
        fullName: 'Demo User',
      });
      console.log(`✓ Registered user: ${user.username} (${user.email})`);
    } catch (error) {
      if (error instanceof ValidationError) {
        console.log(`✗ Registration failed: ${error.message}`);
        // User might already exist, continue to login
      } else {
        throw error;
      }
    }

    // Login
    console.log('\nLogging in...');
    const tokens = await client.auth.login({
      username: 'demo@example.com', // Can use email or username
      password: 'DemoPass123!',
    });
    console.log('✓ Logged in successfully');
    console.log(`  Access token expires in: ${tokens.expiresIn} seconds`);

    // Get current user
    console.log('\nFetching user profile...');
    const me = await client.users.getCurrentUser();
    console.log(`✓ Current user: ${me.fullName} (${me.email})`);
    console.log(`  Account created: ${me.createdAt}`);
    console.log(`  Email verified: ${me.isVerified}`);

    // Update profile
    console.log('\nUpdating profile...');
    const updated = await client.users.updateProfile({
      fullName: 'Demo User Updated',
    });
    console.log(`✓ Profile updated: ${updated.fullName}`);

    // Add custom interceptor
    console.log('\nAdding request logger...');
    const interceptorId = client.addRequestInterceptor((config) => {
      console.log(`  → ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    });

    // Make another request to see the interceptor in action
    await client.users.getCurrentUser();

    // Remove interceptor
    client.removeRequestInterceptor(interceptorId);

    // Logout
    console.log('\nLogging out...');
    await client.auth.logout();
    console.log('✓ Logged out successfully');

  } catch (error) {
    if (error instanceof AuthError) {
      console.error(`✗ Authentication failed: ${error.message}`);
    } else if (error instanceof ValidationError) {
      console.error(`✗ Validation failed: ${error.message}`);
      if (error.errors.length > 0) {
        console.error('  Errors:');
        error.errors.forEach(err => {
          console.error(`    - ${err.field}: ${err.message}`);
        });
      }
    } else {
      console.error(`✗ Error: ${error}`);
    }
  }
}

// Run the example
main().catch(console.error);
