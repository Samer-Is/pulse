/**
 * Database Service - PostgreSQL connection for worker
 */

import { Pool, PoolClient } from 'pg';

export class DatabaseService {
  private pool: Pool;
  
  constructor() {
    const databaseUrl = process.env.DATABASE_URL || process.env.POSTGRES_URL;
    
    if (!databaseUrl) {
      throw new Error('DATABASE_URL or POSTGRES_URL environment variable is required');
    }
    
    this.pool = new Pool({
      connectionString: databaseUrl,
      max: 5,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });
    
    console.log('🗄️  Database service initialized');
  }
  
  async query(text: string, params?: any[]): Promise<any> {
    try {
      const result = await this.pool.query(text, params);
      return result;
    } catch (error) {
      console.error('❌ Database query error:', error);
      throw error;
    }
  }
  
  async getClient(): Promise<PoolClient> {
    return await this.pool.connect();
  }
  
  async updateJobStatus(
    jobId: string,
    status: string,
    resultUrl?: string,
    errorMessage?: string
  ): Promise<void> {
    const updateFields: string[] = ['status = $2', 'updated_at = NOW()'];
    const params: any[] = [jobId, status];
    let paramIndex = 3;
    
    if (status === 'processing' && !resultUrl && !errorMessage) {
      updateFields.push(`started_at = NOW()`);
    } else if (status === 'completed' || status === 'failed') {
      updateFields.push(`completed_at = NOW()`);
    }
    
    if (resultUrl) {
      updateFields.push(`result_url = $${paramIndex}`);
      params.push(resultUrl);
      paramIndex++;
    }
    
    if (errorMessage) {
      updateFields.push(`error_message = $${paramIndex}`);
      params.push(errorMessage);
      paramIndex++;
    }
    
    const query = `
      UPDATE jobs
      SET ${updateFields.join(', ')}
      WHERE id = $1
    `;
    
    await this.query(query, params);
  }
  
  async recordUsage(
    userId: string,
    jobId: string,
    eventType: string,
    metadata: Record<string, any>
  ): Promise<void> {
    const query = `
      INSERT INTO usage_events (id, user_id, job_id, event_type, tokens, event_metadata, created_at, updated_at)
      VALUES (gen_random_uuid(), $1, $2, $3, 0, $4, NOW(), NOW())
    `;
    
    await this.query(query, [userId, jobId, eventType, JSON.stringify(metadata)]);
  }
  
  async updateSubscriptionVideoUsage(userId: string, videoSeconds: number): Promise<void> {
    const query = `
      UPDATE subscriptions
      SET videos_generated = videos_generated + 1,
          updated_at = NOW()
      WHERE user_id = $1
    `;
    
    await this.query(query, [userId]);
  }
  
  async close(): Promise<void> {
    await this.pool.end();
    console.log('🗄️  Database connection closed');
  }
}

