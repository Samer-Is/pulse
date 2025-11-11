"""
Seed database with initial data (3 plans).
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.db import SessionLocal
from src.models import Plan
from decimal import Decimal

def seed_plans():
    """Create the 3 subscription plans."""
    db = SessionLocal()
    
    try:
        # Check if plans already exist
        existing = db.query(Plan).count()
        if existing > 0:
            print(f"✅ Plans already exist ({existing} plans found). Skipping seed.")
            return
        
        plans = [
            {
                "name": "Starter",
                "price_jod": Decimal("3.00"),
                "token_limit": 150000,
                "image_limit": 10,
                "video_limit": 2,
                "features_json": {
                    "chat": True,
                    "cv_maker": True,
                    "slides_maker": False,
                    "image_editor": True,
                    "video_editor": False,
                    "priority_support": False
                }
            },
            {
                "name": "Pro",
                "price_jod": Decimal("5.00"),
                "token_limit": 400000,
                "image_limit": 30,
                "video_limit": 5,
                "features_json": {
                    "chat": True,
                    "cv_maker": True,
                    "slides_maker": True,
                    "image_editor": True,
                    "video_editor": True,
                    "priority_support": False
                }
            },
            {
                "name": "Creator",
                "price_jod": Decimal("7.00"),
                "token_limit": 1000000,
                "image_limit": 60,
                "video_limit": 10,
                "features_json": {
                    "chat": True,
                    "cv_maker": True,
                    "slides_maker": True,
                    "image_editor": True,
                    "video_editor": True,
                    "priority_support": True
                }
            }
        ]
        
        for plan_data in plans:
            plan = Plan(**plan_data)
            db.add(plan)
        
        db.commit()
        
        print("✅ Successfully seeded 3 plans:")
        for plan in db.query(Plan).all():
            print(f"   - {plan.name}: {plan.price_jod} JD/month ({plan.token_limit} tokens, {plan.image_limit} images, {plan.video_limit} videos)")
        
    except Exception as e:
        print(f"❌ Error seeding plans: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding database with plans...")
    seed_plans()
    print("✅ Seed complete!")

