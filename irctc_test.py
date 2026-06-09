from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ]
    )

    page = browser.new_page()

    try:
        page.goto(
            "https://www.irctc.co.in",
            wait_until="domcontentloaded",
            timeout=120000
        )

        print("TITLE:", page.title())

        page.screenshot(path="irctc.png")

    except Exception as e:
        print("ERROR:", e)

    browser.close()
