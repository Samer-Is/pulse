/**
 * Video Processor - Handles video generation jobs
 */

import axios from 'axios';
import AWS from 'aws-sdk';
import { DatabaseService } from '../services/database';
import { JobMessage } from '../services/sqs-worker';

export class VideoProcessor {
  private database: DatabaseService;
  private s3: AWS.S3;
  private bucketName: string;
  
  constructor(database: DatabaseService) {
    this.database = database;
    
    // Configure AWS S3
    const endpoint = process.env.AWS_ENDPOINT_URL;
    this.s3 = new AWS.S3({
      region: process.env.AWS_REGION || 'eu-central-1',
      ...(endpoint && { endpoint, s3ForcePathStyle: true }),
    });
    
    this.bucketName = process.env.S3_BUCKET_NAME || 'pulse-dev-exports';
    
    console.log('🎬 Video Processor initialized');
  }
  
  async process(job: JobMessage): Promise<void> {
    console.log(`🎬 Processing video job ${job.job_id}`);
    
    try {
      // Update job status to processing
      await this.database.updateJobStatus(job.job_id, 'processing');
      
      // Generate video based on provider
      let videoUrl: string;
      
      if (job.provider === 'runway') {
        videoUrl = await this.generateWithRunway(job);
      } else if (job.provider === 'pika') {
        videoUrl = await this.generateWithPika(job);
      } else {
        throw new Error(`Unsupported provider: ${job.provider}`);
      }
      
      // Update job status to completed
      await this.database.updateJobStatus(job.job_id, 'completed', videoUrl);
      
      // Record usage
      await this.database.recordUsage(
        job.user_id,
        job.job_id,
        'video_generation',
        {
          provider: job.provider,
          duration: job.duration,
          style: job.style,
        }
      );
      
      // Update subscription usage
      await this.database.updateSubscriptionVideoUsage(job.user_id, job.duration);
      
      console.log(`✅ Video job ${job.job_id} completed successfully`);
    } catch (error: any) {
      console.error(`❌ Video job ${job.job_id} failed:`, error);
      
      // Update job status to failed
      await this.database.updateJobStatus(
        job.job_id,
        'failed',
        undefined,
        error.message || 'Unknown error'
      );
    }
  }
  
  private async generateWithRunway(job: JobMessage): Promise<string> {
    console.log(`🚀 Generating video with Runway for job ${job.job_id}`);
    
    const apiKey = process.env.RUNWAY_API_KEY;
    
    if (!apiKey || apiKey === 'your-runway-key') {
      // Mock implementation for development
      return await this.mockVideoGeneration(job, 'runway');
    }
    
    // Real Runway implementation (when API key is available)
    // This is a placeholder - actual Runway API integration would go here
    try {
      // Example Runway API call structure (adjust based on actual API)
      const response = await axios.post(
        'https://api.runwayml.com/v1/generate',
        {
          prompt: job.prompt,
          duration: job.duration,
          style: job.style,
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      // Poll for completion
      const videoUrl = await this.pollRunwayJob(response.data.id, apiKey);
      
      // Upload to S3
      return await this.uploadVideoToS3(videoUrl, job.job_id, job.user_id);
    } catch (error) {
      console.error('Runway API error:', error);
      throw error;
    }
  }
  
  private async generateWithPika(job: JobMessage): Promise<string> {
    console.log(`🎨 Generating video with Pika for job ${job.job_id}`);
    
    const apiKey = process.env.PIKA_API_KEY;
    
    if (!apiKey || apiKey === 'your-pika-key') {
      // Mock implementation for development
      return await this.mockVideoGeneration(job, 'pika');
    }
    
    // Real Pika implementation (when API key is available)
    // This is a placeholder - actual Pika API integration would go here
    try {
      const response = await axios.post(
        'https://api.pika.art/v1/generate',
        {
          prompt: job.prompt,
          duration: job.duration,
          style: job.style,
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      // Poll for completion
      const videoUrl = await this.pollPikaJob(response.data.id, apiKey);
      
      // Upload to S3
      return await this.uploadVideoToS3(videoUrl, job.job_id, job.user_id);
    } catch (error) {
      console.error('Pika API error:', error);
      throw error;
    }
  }
  
  private async mockVideoGeneration(job: JobMessage, provider: string): Promise<string> {
    console.log(`🎭 Using mock video generation (${provider}) for development`);
    
    // Simulate processing time (2-5 seconds per duration second)
    const processingTime = job.duration * 2000 + Math.random() * job.duration * 3000;
    await new Promise(resolve => setTimeout(resolve, processingTime));
    
    // Create a mock video URL (in real scenario, this would be actual video from provider)
    // For now, we'll use a placeholder or generate a simple video
    const mockVideoKey = `videos/${job.user_id}/${job.job_id}/video.mp4`;
    
    // Generate presigned URL (even though video doesn't exist, this simulates the flow)
    const presignedUrl = this.s3.getSignedUrl('getObject', {
      Bucket: this.bucketName,
      Key: mockVideoKey,
      Expires: 86400, // 24 hours
    });
    
    console.log(`✨ Mock video generated: ${mockVideoKey}`);
    
    return presignedUrl;
  }
  
  private async pollRunwayJob(jobId: string, apiKey: string): Promise<string> {
    // Placeholder for Runway job polling
    // In real implementation, poll until job is complete
    const maxAttempts = 60;
    let attempt = 0;
    
    while (attempt < maxAttempts) {
      try {
        const response = await axios.get(
          `https://api.runwayml.com/v1/jobs/${jobId}`,
          {
            headers: { 'Authorization': `Bearer ${apiKey}` },
          }
        );
        
        if (response.data.status === 'completed') {
          return response.data.video_url;
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        attempt++;
      } catch (error) {
        console.error('Error polling Runway job:', error);
        throw error;
      }
    }
    
    throw new Error('Runway job timed out');
  }
  
  private async pollPikaJob(jobId: string, apiKey: string): Promise<string> {
    // Placeholder for Pika job polling
    // Similar structure to Runway polling
    const maxAttempts = 60;
    let attempt = 0;
    
    while (attempt < maxAttempts) {
      try {
        const response = await axios.get(
          `https://api.pika.art/v1/jobs/${jobId}`,
          {
            headers: { 'Authorization': `Bearer ${apiKey}` },
          }
        );
        
        if (response.data.status === 'completed') {
          return response.data.video_url;
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        attempt++;
      } catch (error) {
        console.error('Error polling Pika job:', error);
        throw error;
      }
    }
    
    throw new Error('Pika job timed out');
  }
  
  private async uploadVideoToS3(
    videoUrl: string,
    jobId: string,
    userId: string
  ): Promise<string> {
    try {
      // Download video from provider
      const response = await axios.get(videoUrl, { responseType: 'arraybuffer' });
      const videoBuffer = Buffer.from(response.data);
      
      // Upload to S3
      const key = `videos/${userId}/${jobId}/video.mp4`;
      
      await this.s3.putObject({
        Bucket: this.bucketName,
        Key: key,
        Body: videoBuffer,
        ContentType: 'video/mp4',
        Metadata: {
          user_id: userId,
          job_id: jobId,
        },
      }).promise();
      
      // Generate presigned URL
      const presignedUrl = this.s3.getSignedUrl('getObject', {
        Bucket: this.bucketName,
        Key: key,
        Expires: 86400, // 24 hours
      });
      
      console.log(`📤 Video uploaded to S3: ${key}`);
      
      return presignedUrl;
    } catch (error) {
      console.error('Error uploading video to S3:', error);
      throw error;
    }
  }
}

