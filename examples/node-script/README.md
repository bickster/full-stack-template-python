# FullStack Node.js Script Examples

Production-ready Node.js scripts demonstrating advanced FullStack API integration patterns.

## Features

- 🔄 **User Synchronization**: Sync users to external systems
- 📦 **Batch Operations**: Efficient bulk processing with rate limiting
- 🪝 **Webhook Server**: Handle real-time events from the API
- 📊 **Progress Tracking**: Monitor long-running operations
- 🚦 **Rate Limiting**: Respect API limits automatically
- 📝 **Comprehensive Logging**: Winston-based structured logging

## Setup

1. Install dependencies:
```bash
npm install
```

2. Build the TypeScript SDK:
```bash
cd ../../sdk/typescript
npm install
npm run build
```

3. Configure environment:
```bash
# Create .env file
cat > .env << EOF
FULLSTACK_API_URL=http://localhost:8000
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin_password
EOF
```

## Scripts

### User Synchronization (`user-sync.js`)

Synchronizes users from FullStack API to external systems (CRM, mailing lists, etc.).

#### Features
- Tracks synchronized users to avoid duplicates
- Detects updated users for re-sync
- Configurable for one-time or scheduled execution
- Comprehensive logging

#### Usage
```bash
# Run once
node user-sync.js

# Run as daemon (hourly sync)
node user-sync.js --daemon
```

#### Example Output
```
2024-01-15T10:30:00.123Z [info]: Logging in to FullStack API...
2024-01-15T10:30:01.456Z [info]: New user found: john_doe
2024-01-15T10:30:01.789Z [info]: Syncing user to external system {
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "username": "john_doe",
  "email": "john@example.com"
}
2024-01-15T10:30:02.123Z [info]: Successfully synced user: john_doe
2024-01-15T10:30:02.456Z [info]: Sync completed. Total synced users: 1
```

### Batch Operations (`batch-operations.js`)

Handles bulk operations efficiently with batching and rate limiting.

#### Operations

1. **Bulk User Creation**
   ```bash
   node batch-operations.js create-users
   ```

2. **Bulk Password Reset**
   ```bash
   node batch-operations.js password-reset
   ```

3. **Data Migration**
   ```bash
   node batch-operations.js migrate
   ```

4. **Parallel Health Checks**
   ```bash
   node batch-operations.js health-check
   ```

#### Batch Processing Features
- Configurable batch size
- Rate limiting between batches
- Progress tracking
- Error recovery
- Results logging

#### Example Output
```
2024-01-15T10:35:00.123Z [info]: Starting batch processing of 50 items
2024-01-15T10:35:00.456Z [info]: Processing batch 1/5
2024-01-15T10:35:02.789Z [info]: Progress: 20.0% (10/50)
2024-01-15T10:35:03.123Z [info]: Processing batch 2/5
2024-01-15T10:35:05.456Z [info]: Progress: 40.0% (20/50)
...
2024-01-15T10:35:15.789Z [info]: Batch processing completed {
  "total": 50,
  "processed": 50,
  "succeeded": 48,
  "failed": 2,
  "duration": "15.666s",
  "rate": "3.2 items/sec"
}
```

### Webhook Server (`webhook-server.js`)

Receives and processes webhooks from the FullStack API.

```bash
# Start webhook server
node webhook-server.js
```

## Code Examples

### Custom Batch Processor

```javascript
import { BatchProcessor } from './batch-operations.js';

const processor = new BatchProcessor(client, batchSize = 10);

// Define your processing function
const processItem = async (item) => {
  // Your processing logic
  await someAsyncOperation(item);
  return result;
};

// Process items
const results = await processor.processAll(items, processItem);
```

### Error Handling Pattern

```javascript
try {
  await client.someOperation();
} catch (error) {
  if (error.code === 'RATE_LIMIT_EXCEEDED') {
    logger.warn(`Rate limit hit. Retry after ${error.details.retry_after}s`);
    await sleep(error.details.retry_after * 1000);
    // Retry
  } else if (error.code === 'VALIDATION_ERROR') {
    logger.error('Validation failed:', error.details.errors);
    // Handle validation errors
  } else {
    logger.error('Unexpected error:', error);
    throw error;
  }
}
```

### Scheduled Tasks

```javascript
import cron from 'node-cron';

// Run every day at 2 AM
cron.schedule('0 2 * * *', async () => {
  logger.info('Starting scheduled task...');
  await performDailySync();
});

// Run every 15 minutes
cron.schedule('*/15 * * * *', async () => {
  await checkApiHealth();
});
```

## Best Practices

### 1. Rate Limiting
Always implement rate limiting for bulk operations:
```javascript
// Wait between batches
await new Promise(resolve => setTimeout(resolve, 1000));
```

### 2. Error Recovery
Implement retry logic for transient failures:
```javascript
async function retryOperation(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(Math.pow(2, i) * 1000); // Exponential backoff
    }
  }
}
```

### 3. Progress Tracking
For long operations, provide progress updates:
```javascript
const total = items.length;
let processed = 0;

for (const item of items) {
  await processItem(item);
  processed++;
  
  if (processed % 10 === 0) {
    const percent = (processed / total * 100).toFixed(1);
    logger.info(`Progress: ${percent}% (${processed}/${total})`);
  }
}
```

### 4. Structured Logging
Use structured logging for better debugging:
```javascript
logger.info('Operation completed', {
  operation: 'user_sync',
  duration: endTime - startTime,
  itemsProcessed: count,
  errors: errorCount,
  metadata: { source: 'api', destination: 'crm' }
});
```

## Monitoring

### Log Files
- `user-sync.log` - User synchronization logs
- `batch-operations.log` - Batch processing logs
- `webhook-server.log` - Webhook processing logs

### Metrics to Track
- Operation duration
- Success/failure rates
- Items processed per second
- API response times
- Error frequency

## Production Deployment

### SystemD Service (Linux)
```ini
[Unit]
Description=FullStack User Sync Service
After=network.target

[Service]
Type=simple
User=nodejs
WorkingDirectory=/opt/fullstack-sync
ExecStart=/usr/bin/node user-sync.js --daemon
Restart=always
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

### PM2 Configuration
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'fullstack-sync',
    script: './user-sync.js',
    args: '--daemon',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["node", "user-sync.js", "--daemon"]
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check credentials in `.env`
   - Verify API URL is correct
   - Ensure user has necessary permissions

2. **Rate Limiting**
   - Reduce batch size
   - Increase delay between batches
   - Implement exponential backoff

3. **Memory Issues**
   - Process data in smaller batches
   - Use streams for large datasets
   - Monitor memory usage

4. **Network Timeouts**
   - Increase client timeout settings
   - Implement retry logic
   - Check network connectivity