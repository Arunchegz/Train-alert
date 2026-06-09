from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    page.goto(
        "https://www.irctc.co.in/nget/train-search",
        wait_until="networkidle",
        timeout=60000
    )

    print(page.title())

    browser.close()
