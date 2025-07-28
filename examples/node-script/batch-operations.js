#!/usr/bin/env node
/**
 * Batch Operations Example
 *
 * Demonstrates efficient batch processing with the FullStack API
 */

import { FullStackClient } from '@fullstack/api-client';
import { config } from 'dotenv';
import winston from 'winston';
import fs from 'fs/promises';

// Load environment variables
config();

// Logger setup
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      return `${timestamp} [${level}]: ${message} ${Object.keys(meta).length ? JSON.stringify(meta, null, 2) : ''}`;
    })
  ),
  transports: [new winston.transports.Console()]
});

const API_URL = process.env.FULLSTACK_API_URL || 'http://localhost:8000';

/**
 * Process users in batches
 */
class BatchProcessor {
  constructor(client, batchSize = 10) {
    this.client = client;
    this.batchSize = batchSize;
    this.stats = {
      total: 0,
      processed: 0,
      succeeded: 0,
      failed: 0,
      startTime: Date.now()
    };
  }

  /**
   * Process a batch of items
   */
  async processBatch(items, processor) {
    const promises = items.map(async (item) => {
      try {
        await processor(item);
        this.stats.succeeded++;
        return { item, success: true };
      } catch (error) {
        this.stats.failed++;
        logger.error(`Failed to process item:`, { item, error: error.message });
        return { item, success: false, error };
      } finally {
        this.stats.processed++;
      }
    });

    return Promise.all(promises);
  }

  /**
   * Process all items in batches
   */
  async processAll(items, processor) {
    this.stats.total = items.length;
    logger.info(`Starting batch processing of ${items.length} items`);

    const results = [];

    for (let i = 0; i < items.length; i += this.batchSize) {
      const batch = items.slice(i, i + this.batchSize);
      const batchNum = Math.floor(i / this.batchSize) + 1;
      const totalBatches = Math.ceil(items.length / this.batchSize);

      logger.info(`Processing batch ${batchNum}/${totalBatches}`);

      const batchResults = await this.processBatch(batch, processor);
      results.push(...batchResults);

      // Progress update
      const progress = (this.stats.processed / this.stats.total * 100).toFixed(1);
      logger.info(`Progress: ${progress}% (${this.stats.processed}/${this.stats.total})`);

      // Rate limiting - wait between batches
      if (i + this.batchSize < items.length) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    // Final stats
    const duration = (Date.now() - this.stats.startTime) / 1000;
    logger.info('Batch processing completed', {
      ...this.stats,
      duration: `${duration}s`,
      rate: `${(this.stats.processed / duration).toFixed(1)} items/sec`
    });

    return results;
  }
}

/**
 * Example: Bulk user creation from CSV
 */
async function bulkCreateUsers() {
  const client = new FullStackClient({
    baseURL: API_URL
  });

  // Sample user data (in real scenario, load from CSV)
  const newUsers = [
    { email: 'user1@example.com', username: 'user1', password: 'Password123!', full_name: 'User One' },
    { email: 'user2@example.com', username: 'user2', password: 'Password123!', full_name: 'User Two' },
    { email: 'user3@example.com', username: 'user3', password: 'Password123!', full_name: 'User Three' },
    // ... more users
  ];

  const processor = new BatchProcessor(client, 5);

  const results = await processor.processAll(newUsers, async (userData) => {
    const user = await client.register(userData);
    logger.info(`Created user: ${user.username}`);
    return user;
  });

  // Save results
  await fs.writeFile(
    'bulk-create-results.json',
    JSON.stringify(results, null, 2)
  );
}

/**
 * Example: Bulk password reset notifications
 */
async function bulkPasswordReset() {
  const client = new FullStackClient({
    baseURL: API_URL
  });

  // Login as admin
  await client.login({
    username: process.env.ADMIN_USERNAME,
    password: process.env.ADMIN_PASSWORD
  });

  // List of emails to send password reset to
  const emails = [
    'user1@example.com',
    'user2@example.com',
    'user3@example.com'
  ];

  const processor = new BatchProcessor(client, 3);

  await processor.processAll(emails, async (email) => {
    await client.requestPasswordReset({ email });
    logger.info(`Password reset sent to: ${email}`);
  });
}

/**
 * Example: Data migration with progress tracking
 */
async function migrateUserData() {
  const client = new FullStackClient({
    baseURL: API_URL
  });

  // Login
  await client.login({
    username: process.env.ADMIN_USERNAME,
    password: process.env.ADMIN_PASSWORD
  });

  // Simulate loading users that need migration
  const usersToMigrate = [
    { id: '1', username: 'user1', data: { oldField: 'value1' } },
    { id: '2', username: 'user2', data: { oldField: 'value2' } },
    // ... more users
  ];

  const processor = new BatchProcessor(client, 10);

  const migrationProcessor = async (user) => {
    // Simulate data transformation
    const newData = {
      full_name: user.data.oldField // Example transformation
    };

    // Update user
    await client.updateCurrentUser(newData);
    logger.info(`Migrated user: ${user.username}`);
  };

  await processor.processAll(usersToMigrate, migrationProcessor);
}

/**
 * Example: Parallel health checks
 */
async function parallelHealthChecks() {
  const endpoints = [
    'http://localhost:8000',
    'http://localhost:8001',
    'http://localhost:8002'
  ];

  logger.info('Running parallel health checks...');

  const healthChecks = endpoints.map(async (url) => {
    const client = new FullStackClient({ baseURL: url });

    try {
      const start = Date.now();
      const health = await client.healthCheck();
      const duration = Date.now() - start;

      return {
        url,
        status: health.status,
        database: health.database,
        version: health.version,
        responseTime: `${duration}ms`,
        success: true
      };
    } catch (error) {
      return {
        url,
        error: error.message,
        success: false
      };
    }
  });

  const results = await Promise.all(healthChecks);

  // Display results
  console.table(results);

  // Save to file
  await fs.writeFile(
    'health-check-results.json',
    JSON.stringify({
      timestamp: new Date().toISOString(),
      results
    }, null, 2)
  );
}

/**
 * Main function
 */
async function main() {
  const operation = process.argv[2];

  try {
    switch (operation) {
      case 'create-users':
        await bulkCreateUsers();
        break;

      case 'password-reset':
        await bulkPasswordReset();
        break;

      case 'migrate':
        await migrateUserData();
        break;

      case 'health-check':
        await parallelHealthChecks();
        break;

      default:
        logger.info('Available operations:');
        logger.info('  node batch-operations.js create-users');
        logger.info('  node batch-operations.js password-reset');
        logger.info('  node batch-operations.js migrate');
        logger.info('  node batch-operations.js health-check');
    }
  } catch (error) {
    logger.error('Operation failed:', error);
    process.exit(1);
  }
}

// Run
main();
