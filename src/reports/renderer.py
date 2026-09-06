from pathlib import Path
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright


async def render_pdf(html_content: str, output_path: str | Path) -> str:
    """
    Renders an HTML string into an A4 PDF document using Playwright headless Chromium.
    Applies background colors/graphics and saves to output_path.
    """
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            # Set content and ensure network idle
            await page.set_content(html_content, wait_until="networkidle")
            # Print to PDF with true backgrounds and standard A4 sizing
            await page.pdf(
                path=str(path_obj),
                format="A4",
                print_background=True,
                margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"}
            )
        finally:
            await browser.close()

    return str(path_obj)


def render_pdf_sync(html_content: str, output_path: str | Path) -> str:
    """
    Synchronous helper for rendering HTML to PDF via Playwright.
    Useful for standalone CLI scripts and synchronous test runners.
    """
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content(html_content, wait_until="networkidle")
            page.pdf(
                path=str(path_obj),
                format="A4",
                print_background=True,
                margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"}
            )
        finally:
            browser.close()

    return str(path_obj)
