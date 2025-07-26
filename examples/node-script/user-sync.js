#!/usr/bin/env node
/**
 * User Synchronization Script
 * 
 * This script demonstrates how to sync users from FullStack API
 * to another system (e.g., CRM, mailing list, etc.)
 */

import { FullStackClient, MemoryTokenStorage } from '@fullstack/api-client';
import winston from 'winston';
import { config } from 'dotenv';
import fs from 'fs/promises';
import path from 'path';

// Load environment variables
config();

// Configure logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    new winston.transports.File({ 
      filename: 'user-sync.log' 
    })
  ]
});

// Configuration
const API_URL = process.env.FULLSTACK_API_URL || 'http://localhost:8000';
const ADMIN_USERNAME = process.env.ADMIN_USERNAME;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
const SYNC_FILE = './synced-users.json';

/**
 * Load previously synced users
 */
async function loadSyncedUsers() {
  try {
    const data = await fs.readFile(SYNC_FILE, 'utf-8');
    return new Set(JSON.parse(data));
  } catch (error) {
    return new Set();
  }
}

/**
 * Save synced users
 */
async function saveSyncedUsers(syncedUsers) {
  await fs.writeFile(
    SYNC_FILE, 
    JSON.stringify([...syncedUsers], null, 2)
  );
}

/**
 * Sync user to external system
 */
async function syncUserToExternalSystem(user) {
  // Simulate syncing to external system
  logger.info(`Syncing user to external system`, {
    userId: user.id,
    username: user.username,
    email: user.email
  });
  
  // In a real implementation, you would:
  // 1. Connect to your external API/database
  // 2. Create or update the user record
  // 3. Handle any mapping of fields
  // 4. Return success/failure status
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // Example: Add to mailing list
  // await mailchimpClient.lists.addListMember(listId, {
  //   email_address: user.email,
  //   status: 'subscribed',
  //   merge_fields: {
  //     FNAME: user.full_name?.split(' ')[0] || '',
  //     LNAME: user.full_name?.split(' ')[1] || ''
  //   }
  // });
  
  return true;
}

/**
 * Main sync function
 */
async function syncUsers() {
  const client = new FullStackClient({
    baseURL: API_URL
  }, new MemoryTokenStorage());
  
  try {
    // Login as admin
    logger.info('Logging in to FullStack API...');
    await client.login({
      username: ADMIN_USERNAME,
      password: ADMIN_PASSWORD
    });
    
    // For this example, we'll sync the current user
    // In a real scenario with admin access, you'd fetch all users
    const currentUser = await client.getCurrentUser();
    
    // Load previously synced users
    const syncedUsers = await loadSyncedUsers();
    
    // Check if user needs syncing
    if (!syncedUsers.has(currentUser.id)) {
      logger.info(`New user found: ${currentUser.username}`);
      
      try {
        // Sync to external system
        const success = await syncUserToExternalSystem(currentUser);
        
        if (success) {
          syncedUsers.add(currentUser.id);
          await saveSyncedUsers(syncedUsers);
          logger.info(`Successfully synced user: ${currentUser.username}`);
        } else {
          logger.error(`Failed to sync user: ${currentUser.username}`);
        }
      } catch (error) {
        logger.error(`Error syncing user ${currentUser.username}:`, error);
      }
    } else {
      logger.info(`User already synced: ${currentUser.username}`);
      
      // Check if user needs update
      // You could store and compare updated_at timestamps
      const userUpdatedAt = new Date(currentUser.updated_at);
      logger.info(`User last updated: ${userUpdatedAt}`);
    }
    
    // Logout
    await client.logout();
    
    // Summary
    logger.info(`Sync completed. Total synced users: ${syncedUsers.size}`);
    
  } catch (error) {
    logger.error('Sync failed:', error);
    process.exit(1);
  }
}

/**
 * Run as scheduled job
 */
function scheduleSync() {
  // Run immediately
  syncUsers();
  
  // Run every hour
  setInterval(() => {
    logger.info('Starting scheduled sync...');
    syncUsers();
  }, 60 * 60 * 1000);
  
  logger.info('User sync scheduler started. Running every hour.');
}

// Check if credentials are provided
if (!ADMIN_USERNAME || !ADMIN_PASSWORD) {
  logger.error('Please set ADMIN_USERNAME and ADMIN_PASSWORD environment variables');
  process.exit(1);
}

// Run based on command line argument
const mode = process.argv[2];

if (mode === '--daemon') {
  scheduleSync();
} else {
  // Run once and exit
  syncUsers().then(() => {
    process.exit(0);
  }).catch(() => {
    process.exit(1);
  });
}