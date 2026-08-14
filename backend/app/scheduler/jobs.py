from apscheduler.schedulers.background import BackgroundScheduler
import logging
from app.db.session import SessionLocal

logger = logging.getLogger("edunexus_scheduler")
scheduler = BackgroundScheduler()

def daily_risk_scan_job():
    logger.info("Executing scheduled daily student risk scan...")
    db = SessionLocal()
    try:
        from agents.nodes.student_success import scan_at_risk_students
        count = scan_at_risk_students(db=db)
        logger.info(f"Daily risk scan finished. Flagged students count: {count}")
    except Exception as e:
        logger.error(f"Error executing daily risk scan: {e}")
    finally:
        db.close()

def start_scheduler():
    # Schedule daily at 2:00 AM (for demo purposes, runs periodically)
    scheduler.add_job(daily_risk_scan_job, 'interval', hours=24, id='daily_risk_scan')
    scheduler.start()
    logger.info("EduNexus APScheduler initialized.")
