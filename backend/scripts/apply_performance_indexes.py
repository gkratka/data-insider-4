#!/usr/bin/env python3
"""
Apply performance indexes for database optimization
Run this script to add indexes that improve query performance
"""
import os
import sys
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database import engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_indexes():
    """Apply performance indexes from SQL file"""
    sql_file = backend_dir / "migrations" / "add_performance_indexes.sql"
    
    if not sql_file.exists():
        logger.error(f"SQL file not found: {sql_file}")
        return False
    
    try:
        with engine.connect() as conn:
            # Read and execute the SQL file
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            # Split by semicolons to execute individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement and not statement.startswith('--'):
                    try:
                        logger.info(f"Executing: {statement[:50]}...")
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Statement failed (might already exist): {str(e)}")
                        continue
            
            logger.info("Successfully applied performance indexes")
            return True
            
    except Exception as e:
        logger.error(f"Failed to apply indexes: {str(e)}")
        return False

def check_indexes():
    """Check which indexes exist"""
    try:
        with engine.connect() as conn:
            # Query to check existing indexes
            result = conn.execute(text("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexname LIKE 'idx_%'
                ORDER BY tablename, indexname;
            """))
            
            indexes = result.fetchall()
            logger.info("Existing performance indexes:")
            for index in indexes:
                logger.info(f"  {index.tablename}: {index.indexname}")
            
            return len(indexes)
            
    except Exception as e:
        logger.error(f"Failed to check indexes: {str(e)}")
        return 0

if __name__ == "__main__":
    logger.info("Database Performance Index Application")
    logger.info("=" * 50)
    
    # Check current indexes
    current_count = check_indexes()
    logger.info(f"Found {current_count} existing performance indexes")
    
    # Apply new indexes
    logger.info("Applying performance indexes...")
    success = apply_indexes()
    
    if success:
        # Check indexes again
        new_count = check_indexes()
        added = new_count - current_count
        logger.info(f"Added {added} new indexes. Total: {new_count}")
    else:
        logger.error("Failed to apply indexes")
        sys.exit(1)