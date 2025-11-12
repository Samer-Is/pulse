/**
 * Pulse AI Studio - Worker Service
 * Handles async jobs (video generation, long-running exports)
 */
import { config } from 'dotenv';

config();

console.log('Pulse AI Studio Worker starting...');
console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);

// Worker will poll SQS queue for jobs
async function startWorker() {
  console.log('Worker initialized - ready to process jobs');
  // TODO: Implement SQS polling in Phase 5
}

startWorker().catch((error) => {
  console.error('Worker failed to start:', error);
  process.exit(1);
});

