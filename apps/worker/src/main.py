"""
Worker service main entry point.

This service processes async jobs:
- Payment webhook processing
- Video generation finalization
- Daily analytics aggregation
- File cleanup and maintenance
"""

import asyncio
import signal
from datetime import datetime

from .jobs import payments_webhooks, video_finalize, analytics, cleanup


class Worker:
    """Async worker service."""
    
    def __init__(self):
        self.running = False
        self.tasks = []
    
    async def start(self):
        """Start worker service."""
        self.running = True
        print(f"[Worker] Starting at {datetime.utcnow()}")
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self.process_queue()),
            asyncio.create_task(self.daily_analytics()),
            asyncio.create_task(self.hourly_cleanup())
        ]
        
        # Wait for all tasks
        await asyncio.gather(*self.tasks)
    
    async def stop(self):
        """Stop worker service."""
        print("[Worker] Stopping...")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        print("[Worker] Stopped")
    
    async def process_queue(self):
        """Process job queue."""
        print("[Worker] Queue processor started")
        
        while self.running:
            try:
                # In production: Poll SQS queue or Redis queue
                # message = await queue.receive()
                
                # For now, just sleep
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Worker] Queue processing error: {str(e)}")
                await asyncio.sleep(5)
    
    async def daily_analytics(self):
        """Run daily analytics aggregation."""
        print("[Worker] Daily analytics task started")
        
        while self.running:
            try:
                # Run at midnight
                now = datetime.utcnow()
                # TODO: Calculate next midnight
                # next_run = ...
                # sleep_seconds = (next_run - now).total_seconds()
                
                # For now, run every hour
                await asyncio.sleep(3600)
                
                # Run aggregation for yesterday
                yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
                await analytics.aggregate_daily_analytics(yesterday)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Worker] Analytics error: {str(e)}")
                await asyncio.sleep(60)
    
    async def hourly_cleanup(self):
        """Run hourly cleanup tasks."""
        print("[Worker] Cleanup task started")
        
        while self.running:
            try:
                # Run every hour
                await asyncio.sleep(3600)
                
                # Clean up expired files
                await cleanup.cleanup_expired_files(retention_days=30)
                
                # Send quota warnings
                await cleanup.send_quota_warnings()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Worker] Cleanup error: {str(e)}")
                await asyncio.sleep(60)


# Global worker instance
worker = Worker()


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print(f"[Worker] Received signal {sig}")
    asyncio.create_task(worker.stop())


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run worker
    asyncio.run(worker.start())
