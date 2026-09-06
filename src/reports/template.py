from datetime import datetime
from typing import Dict, Any


def render_stars(rating: int) -> str:
    """Generate visual star icons and numerical label."""
    filled = "★" * rating
    empty = "☆" * (5 - rating)
    return f'<span class="stars">{filled}{empty}</span> <span class="rating-num">({rating}/5)</span>'


def generate_report_html(data: Dict[str, Any], generated_at: datetime = None) -> str:
    """
    Compiles the report data dictionary into an executive-ready HTML document
    with comprehensive print CSS defenses preventing sliced table rows and
    ensuring table headers repeat cleanly across page boundaries.
    """
    if generated_at is None:
        generated_at = datetime.now()

    date_str = generated_at.strftime("%B %d, %Y - %H:%M UTC")

    # Metrics
    total_books = data.get("total_books", 0)
    avg_price = data.get("average_price", 0.0)
    total_value = data.get("total_value", 0.0)
    min_price = data.get("min_price", 0.0)
    max_price = data.get("max_price", 0.0)

    # Top 5 Rows
    top_5_rows_html = ""
    for idx, book in enumerate(data.get("top_5", []), 1):
        top_5_rows_html += f"""
        <tr>
            <td class="text-center font-bold">{idx}</td>
            <td class="font-medium">{book['title']}</td>
            <td class="text-right font-mono font-bold text-indigo">£{book['price']:.2f}</td>
            <td class="text-center">{render_stars(book['rating'])}</td>
        </tr>
        """

    # Rating Breakdown Rows
    rating_rows_html = ""
    for item in data.get("rating_breakdown", []):
        r = item["rating"]
        cnt = item["count"]
        pct = (cnt / total_books * 100) if total_books > 0 else 0
        rating_rows_html += f"""
        <tr>
            <td class="font-medium">{render_stars(r)}</td>
            <td class="text-right font-bold font-mono">{cnt}</td>
            <td class="text-right font-mono text-muted">{pct:.1f}%</td>
            <td class="bar-col">
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: {pct:.1f}%;"></div>
                </div>
            </td>
        </tr>
        """

    # Complete Catalog Rows (forces multi-page output)
    all_books_rows_html = ""
    for idx, book in enumerate(data.get("all_books", []), 1):
        all_books_rows_html += f"""
        <tr>
            <td class="text-center text-muted font-mono">{idx}</td>
            <td class="title-cell">{book['title']}</td>
            <td class="text-right font-mono font-bold">£{book['price']:.2f}</td>
            <td class="text-center">{render_stars(book['rating'])}</td>
            <td class="url-cell text-muted font-mono"><a href="{book['url']}" target="_blank">View Listing</a></td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FlyRank Executive Catalog & Analytics Report</title>
<style>
    /* CSS Reset and Page Setup */
    @page {{
        size: A4;
        margin: 16mm 14mm 16mm 14mm;
    }}
    
    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}

    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #1e293b;
        background-color: #ffffff;
        font-size: 11px;
        line-height: 1.45;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}

    /* Print Break Rules: The Stage 3 Defense Invariants */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }}

    thead {{
        display: table-header-group; /* Repeats table headers on every page */
    }}

    tr {{
        break-inside: avoid; /* Prevents rows from splitting horizontally across pages */
        page-break-inside: avoid;
    }}

    .no-break {{
        break-inside: avoid;
        page-break-inside: avoid;
    }}

    /* Typography & Utilities */
    .font-bold {{ font-weight: 700; }}
    .font-medium {{ font-weight: 500; }}
    .font-mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .text-center {{ text-align: center; }}
    .text-right {{ text-align: right; }}
    .text-muted {{ color: #64748b; }}
    .text-indigo {{ color: #4338ca; }}

    /* Report Header */
    .header {{
        border-bottom: 2px solid #0f172a;
        padding-bottom: 12px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }}

    .brand-title {{
        font-size: 22px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.5px;
    }}

    .brand-subtitle {{
        font-size: 12px;
        color: #64748b;
        margin-top: 3px;
        font-weight: 500;
    }}

    .header-metadata {{
        text-align: right;
    }}

    .badge {{
        display: inline-block;
        padding: 3px 8px;
        font-size: 10px;
        font-weight: 700;
        background: #e0e7ff;
        color: #3730a3;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}

    .timestamp {{
        font-size: 10px;
        color: #64748b;
    }}

    /* Metric Cards */
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 20px;
    }}

    .metric-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px 12px;
        border-left: 4px solid #4f46e5;
    }}

    .metric-label {{
        font-size: 9px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}

    .metric-value {{
        font-size: 18px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
    }}

    .metric-subtext {{
        font-size: 9px;
        color: #94a3b8;
        margin-top: 2px;
    }}

    /* Section Styling */
    .section-title {{
        font-size: 13px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 4px;
    }}

    .two-column {{
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 16px;
        margin-bottom: 20px;
    }}

    /* Table Styles */
    th {{
        background-color: #f1f5f9;
        color: #334155;
        font-weight: 700;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        padding: 7px 9px;
        border: 1px solid #cbd5e1;
    }}

    td {{
        padding: 6px 9px;
        border: 1px solid #e2e8f0;
    }}

    tbody tr:nth-child(even) {{
        background-color: #f8fafc;
    }}

    .stars {{
        color: #f59e0b;
        font-size: 11px;
    }}

    .rating-num {{
        color: #64748b;
        font-size: 9px;
    }}

    /* Progress bar */
    .bar-col {{
        width: 40%;
    }}

    .progress-bar-bg {{
        background-color: #e2e8f0;
        border-radius: 9999px;
        height: 7px;
        width: 100%;
        overflow: hidden;
    }}

    .progress-bar-fill {{
        background-color: #4f46e5;
        height: 100%;
        border-radius: 9999px;
    }}

    .title-cell {{
        max-width: 260px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-weight: 500;
    }}

    .url-cell a {{
        color: #4f46e5;
        text-decoration: none;
        font-size: 9px;
    }}

    /* Footer */
    .footer {{
        margin-top: 20px;
        padding-top: 10px;
        border-top: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        font-size: 9px;
        color: #94a3b8;
    }}
</style>
</head>
<body>

    <!-- Header Section -->
    <div class="header">
        <div>
            <div class="brand-title">FlyRank Intelligence</div>
            <div class="brand-subtitle">Automated Catalog Audit & Price Dispersion Report</div>
        </div>
        <div class="header-metadata">
            <span class="badge">Verified Production Dataset</span>
            <div class="timestamp">Generated: {date_str}</div>
        </div>
    </div>

    <!-- Executive KPI Metrics Cards -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Total Catalog Titles</div>
            <div class="metric-value font-mono">{total_books}</div>
            <div class="metric-subtext">100% verified records</div>
        </div>
        <div class="metric-card" style="border-left-color: #10b981;">
            <div class="metric-label">Average Unit Price</div>
            <div class="metric-value font-mono">£{avg_price:.2f}</div>
            <div class="metric-subtext">Range: £{min_price:.2f} – £{max_price:.2f}</div>
        </div>
        <div class="metric-card" style="border-left-color: #06b6d4;">
            <div class="metric-label">Total Inventory Valuation</div>
            <div class="metric-value font-mono">£{total_value:,.2f}</div>
            <div class="metric-subtext">Sum of catalog items</div>
        </div>
        <div class="metric-card" style="border-left-color: #f59e0b;">
            <div class="metric-label">Top Quartile Premium</div>
            <div class="metric-value font-mono">£{max_price:.2f}</div>
            <div class="metric-subtext">Highest price point</div>
        </div>
    </div>

    <!-- Top 5 and Rating Breakdown Grid -->
    <div class="two-column no-break">
        <!-- Top 5 Most Expensive Books -->
        <div>
            <div class="section-title">Top 5 Most Expensive Titles</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 25px;">#</th>
                        <th>Title</th>
                        <th style="width: 70px;" class="text-right">Price</th>
                        <th style="width: 90px;" class="text-center">Rating</th>
                    </tr>
                </thead>
                <tbody>
                    {top_5_rows_html}
                </tbody>
            </table>
        </div>

        <!-- Rating Breakdown Distribution -->
        <div>
            <div class="section-title">Rating Distribution</div>
            <table>
                <thead>
                    <tr>
                        <th>Stars</th>
                        <th style="width: 40px;" class="text-right">Qty</th>
                        <th style="width: 45px;" class="text-right">Share</th>
                        <th class="bar-col">Share Visual</th>
                    </tr>
                </thead>
                <tbody>
                    {rating_rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Full 60-Book Inventory Catalog (Multi-page Table with Repeat Headers) -->
    <div>
        <div class="section-title">Complete Inventory Catalog ({total_books} Validated Items)</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 30px;" class="text-center">#</th>
                    <th>Book Title</th>
                    <th style="width: 75px;" class="text-right">Price</th>
                    <th style="width: 100px;" class="text-center">Rating</th>
                    <th style="width: 90px;" class="text-center">Source Link</th>
                </tr>
            </thead>
            <tbody>
                {all_books_rows_html}
            </tbody>
        </table>
    </div>

    <!-- Document Footer -->
    <div class="footer">
        <span>FlyRank Internship Backend Track · Milestone W7b (Assignment A8)</span>
        <span>Generated via Headless Chromium PDF Renderer · Store & Link Architecture</span>
    </div>

</body>
</html>
"""
    return html
