from app.core import celery,get_logger

logger = get_logger(__name__)

def main():
    logger.info("staring workers......")
    celery.start(
        argv=[
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "-E",  # Optional: set task routes, time limits, etc.
        ]
    )

if __name__ == "__main__":
    main()
