/**
 * Pulse AI Studio - Worker Service
 * Processes async jobs from SQS queue (video generation, etc.)
 */

import { config } from 'dotenv';
import { SQSWorker } from './services/sqs-worker';
import { VideoProcessor } from './processors/video-processor';
import { DatabaseService } from './services/database';

// Load environment variables
config();

console.log('🚀 Pulse Worker Service starting...');

// Initialize services
const database = new DatabaseService();
const videoProcessor = new VideoProcessor(database);
const sqsWorker = new SQSWorker(videoProcessor);

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('📛 SIGTERM received, shutting down gracefully...');
  sqsWorker.stop();
  await database.close();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('📛 SIGINT received, shutting down gracefully...');
  sqsWorker.stop();
  await database.close();
  process.exit(0);
});

// Start worker
sqsWorker.start().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});

console.log('✅ Worker service started successfully');
