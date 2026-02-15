"""
Database setup script for NIRBHAYA application
Creates database, enables PostGIS extension, and runs migrations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from backend.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """
    Set up database with PostGIS extension
    """
    try:
        # Connect to database
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Enable PostGIS extension
            logger.info("Enabling PostGIS extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            conn.commit()
            
            logger.info("PostGIS extension enabled successfully")
            
            # Verify PostGIS is working
            result = conn.execute(text("SELECT PostGIS_Version();"))
            version = result.fetchone()[0]
            logger.info(f"PostGIS version: {version}")
            
        logger.info("Database setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
