from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled"
        ]
    )

    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        )
    )

    page.goto(
        "https://www.irctc.co.in",
        wait_until="domcontentloaded",
        timeout=120000
    )

    page.screenshot(path="irctc.png")

    print(page.title())

    browser.close()
