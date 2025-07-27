/**
 * Error handling example for the Full-Stack API TypeScript SDK
 */

import {
  FullStackClient,
  ApiError,
  AuthError,
  ValidationError,
  NotFoundError,
  RateLimitError,
  NetworkError,
  TimeoutError,
} from '@fullstack/api-client';

async function demonstrateValidationErrors(client: FullStackClient) {
  console.log('Testing validation errors...');

  // Invalid email
  try {
    await client.auth.register({
      email: 'not-an-email',
      username: 'test',
      password: 'pass',
    });
  } catch (error) {
    if (error instanceof ValidationError) {
      console.log(`✓ Caught validation error: ${error.message}`);
      if (error.errors.length > 0) {
        console.log('  Validation errors:');
        error.errors.forEach(err => {
          console.log(`    - ${err.field}: ${err.message}`);
        });
      }
    }
  }

  // Weak password
  try {
    await client.auth.register({
      email: 'test@example.com',
      username: 'test',
      password: 'weak',
    });
  } catch (error) {
    if (error instanceof ValidationError) {
      console.log(`✓ Caught weak password: ${error.message}`);
    }
  }
}

async function demonstrateAuthErrors(client: FullStackClient) {
  console.log('\nTesting authentication errors...');

  // Invalid credentials
  try {
    await client.auth.login({
      username: 'nonexistent@example.com',
      password: 'wrongpassword',
    });
  } catch (error) {
    if (error instanceof AuthError) {
      console.log(`✓ Caught auth error: ${error.message}`);
    }
  }

  // Accessing protected endpoint without auth
  try {
    await client.users.getCurrentUser();
  } catch (error) {
    if (error instanceof AuthError) {
      console.log(`✓ Caught unauthorized access: ${error.message}`);
    }
  }
}

async function demonstrateRateLimiting(client: FullStackClient) {
  console.log('\nTesting rate limiting...');

  // Make rapid requests
  let attempt = 0;
  while (attempt < 10) {
    try {
      attempt++;
      await client.auth.login({
        username: 'test@example.com',
        password: 'wrong',
      });
    } catch (error) {
      if (error instanceof RateLimitError) {
        console.log(`✓ Rate limited after ${attempt} attempts`);
        console.log(`  Message: ${error.message}`);
        if (error.retryAfter) {
          console.log(`  Retry after: ${error.retryAfter} seconds`);
        }
        break;
      } else if (error instanceof AuthError) {
        // Expected for wrong password
        continue;
      }
    }
  }
}

async function demonstrateErrorRecovery(client: FullStackClient) {
  console.log('\nDemonstrating error recovery...');

  // Pattern 1: Retry with exponential backoff
  async function retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries: number = 3
  ): Promise<T> {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await fn();
      } catch (error) {
        if (error instanceof ApiError || error instanceof NetworkError) {
          if (i === maxRetries - 1) throw error;
          const waitTime = Math.pow(2, i) * 1000; // Exponential backoff
          console.log(`  Retry ${i + 1}/${maxRetries} after ${waitTime}ms...`);
          await new Promise(resolve => setTimeout(resolve, waitTime));
        } else {
          throw error;
        }
      }
    }
    throw new Error('Max retries exceeded');
  }

  // Pattern 2: Fallback behavior
  async function getUserSafe(client: FullStackClient) {
    try {
      return await client.users.getCurrentUser();
    } catch (error) {
      if (error instanceof AuthError) {
        console.log('  Not authenticated, using guest mode');
        return null;
      } else if (error instanceof ApiError) {
        console.log(`  API error, using cached data: ${error.message}`);
        return {
          id: 'cached',
          username: 'cached_user',
          email: 'cached@example.com',
        };
      }
      throw error;
    }
  }

  // Pattern 3: Circuit breaker
  class CircuitBreaker {
    private failures = 0;
    private lastFailureTime?: Date;
    private isOpen = false;

    constructor(
      private failureThreshold: number = 3,
      private recoveryTimeout: number = 60000 // 60 seconds
    ) {}

    async call<T>(fn: () => Promise<T>): Promise<T> {
      if (this.isOpen) {
        const now = new Date();
        if (
          this.lastFailureTime &&
          now.getTime() - this.lastFailureTime.getTime() > this.recoveryTimeout
        ) {
          this.isOpen = false;
          this.failures = 0;
        } else {
          throw new ApiError('Circuit breaker is open');
        }
      }

      try {
        const result = await fn();
        this.failures = 0;
        return result;
      } catch (error) {
        if (error instanceof ApiError) {
          this.failures++;
          this.lastFailureTime = new Date();
          if (this.failures >= this.failureThreshold) {
            this.isOpen = true;
            console.log(`  Circuit breaker opened after ${this.failures} failures`);
          }
        }
        throw error;
      }
    }
  }

  console.log('✓ Error recovery patterns demonstrated');
}

async function demonstrateTimeoutHandling(client: FullStackClient) {
  console.log('\nTesting timeout handling...');

  // Create a client with very short timeout
  const timeoutClient = new FullStackClient({
    baseUrl: 'http://localhost:8000',
    timeout: 1, // 1ms timeout - will definitely timeout
  });

  try {
    await timeoutClient.users.getCurrentUser();
  } catch (error) {
    if (error instanceof TimeoutError) {
      console.log(`✓ Caught timeout error: ${error.message}`);
    } else if (error instanceof NetworkError) {
      console.log(`✓ Caught network error: ${error.message}`);
    }
  }
}

async function demonstrateCancellation(client: FullStackClient) {
  console.log('\nTesting request cancellation...');

  // Create abort controller
  const controller = new AbortController();

  // Start request
  const promise = client.users.getCurrentUser({
    signal: controller.signal,
  });

  // Cancel immediately
  controller.abort();

  try {
    await promise;
  } catch (error: any) {
    if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
      console.log('✓ Request was cancelled');
    }
  }
}

async function main() {
  console.log('Error Handling Examples');
  console.log('=' .repeat(50));

  const client = new FullStackClient({
    baseUrl: 'http://localhost:8000',
  });

  try {
    await demonstrateValidationErrors(client);
    await demonstrateAuthErrors(client);
    await demonstrateRateLimiting(client);
    await demonstrateErrorRecovery(client);
    await demonstrateTimeoutHandling(client);
    await demonstrateCancellation(client);
  } catch (error) {
    console.error(`\n✗ Unexpected error: ${error}`);
  }

  console.log('\n✓ Error handling examples completed');
}

// Run the example
main().catch(console.error);