"""Data ingestion: CSV file or JSON REST API (e.g. the Task 05 FastAPI service)."""
import logging
from typing import Optional

import pandas as pd
import requests

log = logging.getLogger(__name__)
REQUIRED_COLUMNS = {"category", "amount"}


def fetch_data(source: str, token: Optional[str] = None) -> pd.DataFrame:
    if source.startswith(("http://", "https://")):
        log.info("Fetching data from API: %s", source)
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        resp = requests.get(source, headers=headers, timeout=15)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
    else:
        log.info("Reading CSV: %s", source)
        df = pd.read_csv(source)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Source is missing required columns: {sorted(missing)}")
    return df
