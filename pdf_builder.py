"""PDF generation with ReportLab."""
from datetime import datetime
from pathlib import Path

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _chart(by_category) -> Drawing:
    top = by_category.head(8)
    d = Drawing(440, 200)
    chart = VerticalBarChart()
    chart.x, chart.y, chart.width, chart.height = 40, 30, 380, 150
    chart.data = [list(top["total"])]
    chart.categoryAxis.categoryNames = [str(c)[:12] for c in top["category"]]
    chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.labels.fontSize = 7
    chart.bars[0].fillColor = colors.HexColor("#2563eb")
    d.add(chart)
    return d


def build_pdf(summary: dict, out_path: str, title: str = "Automated Report") -> str:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(out), pagesize=A4, title=title,
                            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)

    story = [
        Paragraph(title, styles["Title"]),
        Paragraph(f"Generated on {datetime.now():%d %b %Y, %H:%M}", styles["Normal"]),
        Spacer(1, 16),
        Paragraph("Key metrics", styles["Heading2"]),
    ]

    metrics = [
        ["Total records", f"{summary['records']:,}"],
        ["Total amount", f"{summary['total']:,.2f}"],
        ["Average amount", f"{summary['average']:,.2f}"],
        ["Top category", summary["top_category"]],
    ]
    t = Table(metrics, colWidths=[6 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
    ]))
    story += [t, Spacer(1, 16), Paragraph("Totals by category", styles["Heading2"])]

    if len(summary["by_category"]):
        story += [_chart(summary["by_category"]), Spacer(1, 10)]
        rows = [["Category", "Count", "Total", "Average"]]
        for _, r in summary["by_category"].iterrows():
            rows.append([r["category"], int(r["count"]), f"{r['total']:,.2f}", f"{r['average']:,.2f}"])
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No data available.", styles["Normal"]))

    doc.build(story)
    return str(out)
