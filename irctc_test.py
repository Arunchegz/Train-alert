from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-http2"
        ]
    )

    page = browser.new_page()

    page.goto(
        "https://www.google.com",
        timeout=60000
    )

    print(page.title())

    browser.close()
