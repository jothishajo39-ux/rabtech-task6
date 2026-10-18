"""Command line interface: `report generate` and `report schedule`."""
import logging
from datetime import datetime
from pathlib import Path

import click

from . import __version__
from .fetcher import fetch_data
from .pdf_builder import build_pdf
from .processor import summarize
from .scheduler import run_daily

log = logging.getLogger("report_tool")


def _setup_logging(log_file: str) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
    )


def _run_pipeline(source: str, out: str, token: str, title: str) -> str:
    df = fetch_data(source, token)
    summary = summarize(df)
    path = build_pdf(summary, out, title)
    log.info("Report created: %s (%d records)", path, summary["records"])
    return path


@click.group()
@click.version_option(__version__)
@click.option("--log-file", default="report.log", show_default=True, help="Execution log file.")
def main(log_file):
    """Automated PDF report generator."""
    _setup_logging(log_file)


@main.command()
@click.option("--source", "-s", required=True, help="CSV path or JSON API URL.")
@click.option("--out", "-o", default="report.pdf", show_default=True, help="Output PDF path.")
@click.option("--token", envvar="REPORT_API_TOKEN", help="Bearer token for API sources.")
@click.option("--title", default="Automated Report", show_default=True)
def generate(source, out, token, title):
    """Generate a PDF report once."""
    try:
        _run_pipeline(source, out, token, title)
    except Exception as exc:
        log.error("Report failed: %s", exc)
        raise click.ClickException(str(exc))


@main.command()
@click.option("--source", "-s", required=True, help="CSV path or JSON API URL.")
@click.option("--daily", "at", required=True, help="Time of day, HH:MM (24h).")
@click.option("--out-dir", default="reports", show_default=True)
@click.option("--token", envvar="REPORT_API_TOKEN")
@click.option("--title", default="Automated Report", show_default=True)
@click.option("--run-now", is_flag=True, help="Also generate one report immediately.")
def schedule(source, at, out_dir, token, title, run_now):
    """Generate a timestamped report every day."""

    def job():
        out = Path(out_dir) / f"report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        try:
            _run_pipeline(source, str(out), token, title)
        except Exception as exc:  # keep the scheduler alive
            log.error("Scheduled run failed: %s", exc)

    run_daily(at, job, run_now=run_now)


if __name__ == "__main__":
    main()
