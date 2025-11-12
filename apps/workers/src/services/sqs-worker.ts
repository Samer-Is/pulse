/**
 * SQS Worker - Polls SQS queue and processes messages
 */

import AWS from 'aws-sdk';
import { VideoProcessor } from '../processors/video-processor';

export interface JobMessage {
  job_id: string;
  user_id: string;
  job_type: string;
  prompt: string;
  provider: string;
  duration: number;
  style?: string;
  parameters?: Record<string, any>;
}

export class SQSWorker {
  private sqs: AWS.SQS;
  private queueUrl: string;
  private isRunning: boolean = false;
  private videoProcessor: VideoProcessor;
  
  constructor(videoProcessor: VideoProcessor) {
    this.videoProcessor = videoProcessor;
    
    // Configure AWS SDK
    const endpoint = process.env.AWS_ENDPOINT_URL;
    this.sqs = new AWS.SQS({
      region: process.env.AWS_REGION || 'eu-central-1',
      ...(endpoint && { endpoint }),
    });
    
    this.queueUrl = process.env.SQS_QUEUE_URL || '';
    
    if (!this.queueUrl) {
      throw new Error('SQS_QUEUE_URL environment variable is required');
    }
    
    console.log(`📬 SQS Worker configured with queue: ${this.queueUrl}`);
  }
  
  async start(): Promise<void> {
    this.isRunning = true;
    console.log('🔄 Starting SQS message polling...');
    
    // Start polling loop
    this.poll();
  }
  
  stop(): void {
    this.isRunning = false;
    console.log('⏹️  Stopping SQS worker...');
  }
  
  private async poll(): Promise<void> {
    while (this.isRunning) {
      try {
        const params: AWS.SQS.ReceiveMessageRequest = {
          QueueUrl: this.queueUrl,
          MaxNumberOfMessages: 1,
          WaitTimeSeconds: 20, // Long polling
          VisibilityTimeout: 300, // 5 minutes
          MessageAttributeNames: ['All'],
        };
        
        const result = await this.sqs.receiveMessage(params).promise();
        
        if (result.Messages && result.Messages.length > 0) {
          for (const message of result.Messages) {
            await this.processMessage(message);
          }
        }
      } catch (error) {
        console.error('❌ Error polling SQS:', error);
        // Wait a bit before retrying
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }
  
  private async processMessage(message: AWS.SQS.Message): Promise<void> {
    if (!message.Body) {
      console.warn('⚠️  Received message without body');
      return;
    }
    
    try {
      const jobMessage: JobMessage = JSON.parse(message.Body);
      console.log(`📨 Processing job: ${jobMessage.job_id} (${jobMessage.job_type})`);
      
      // Route to appropriate processor
      if (jobMessage.job_type === 'video') {
        await this.videoProcessor.process(jobMessage);
      } else {
        console.warn(`⚠️  Unknown job type: ${jobMessage.job_type}`);
      }
      
      // Delete message from queue on success
      if (message.ReceiptHandle) {
        await this.deleteMessage(message.ReceiptHandle);
        console.log(`✅ Job ${jobMessage.job_id} completed and removed from queue`);
      }
    } catch (error) {
      console.error('❌ Error processing message:', error);
      // Message will become visible again after visibility timeout
    }
  }
  
  private async deleteMessage(receiptHandle: string): Promise<void> {
    try {
      await this.sqs.deleteMessage({
        QueueUrl: this.queueUrl,
        ReceiptHandle: receiptHandle,
      }).promise();
    } catch (error) {
      console.error('❌ Error deleting message from SQS:', error);
    }
  }
}

