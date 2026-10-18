"""Simple daily scheduler built on the `schedule` library."""
import logging
import time
from typing import Callable

import schedule

log = logging.getLogger(__name__)


def run_daily(at: str, job: Callable[[], None], run_now: bool = False) -> None:
    """Run `job` every day at HH:MM (24h, local time). Blocks until Ctrl+C."""
    if run_now:
        job()
    schedule.every().day.at(at).do(job)
    log.info("Scheduler started: daily at %s. Press Ctrl+C to stop.", at)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Scheduler stopped.")
