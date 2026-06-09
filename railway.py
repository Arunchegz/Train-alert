import logging
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

logger = logging.getLogger("train-alert")

# IRCTC seat availability API — intercepted from browser network tab
# No login required for availability checks
AVAIL_API = "availabilityAndFarenquiry"

def get_status(
    train_number: str,
    from_station: str,
    to_station: str,
    journey_date: str,   # YYYYMMDD
    class_code: str,
    quota: str = "GN"
) -> str:
    """
    Opens IRCTC train search in a stealth Playwright browser,
    intercepts the availability JSON, and returns the seat status string.

    Returns status like "AVAILABLE-42", "WL/12/WL8", "REGRET", etc.
    Returns "ERROR" or "TIMEOUT" on failure.
    """
    url = (
        f"https://www.irctc.co.in/eticketing/protected/mapps1/"
        f"availabilityAndFarenquiry/{train_number}/"
        f"{from_station}/{to_station}/{journey_date}/{class_code}/{quota}WL"
    )

    # The page we navigate to — train search triggers the API call
    search_url = (
        f"https://www.irctc.co.in/nget/train-search"
    )

    captured = {}

    def handle_response(response):
        if AVAIL_API in response.url and response.status == 200:
            try:
                captured["data"] = response.json()
                captured["url"] = response.url
            except Exception:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            viewport={"width": 1366, "height": 768},
            # Mask automation signals
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
                "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
                "sec-ch-ua-platform": '"Windows"',
            }
        )

        # Remove webdriver property
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en'] });
        """)

        page = context.new_page()
        page.on("response", handle_response)

        try:
            logger.info(f"Navigating to IRCTC for {train_number} {from_station}→{to_station} {journey_date} {class_code}")
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            # Directly fetch the availability API URL within the browser context
            # This carries the same cookies/session as IRCTC loaded above
            page.evaluate(f"""
                fetch("{url}", {{
                    headers: {{
                        "Accept": "application/json",
                        "greq": "1"
                    }},
                    credentials: "include"
                }})
            """)

            # Wait for the intercepted response
            page.wait_for_timeout(6000)

        except PWTimeout:
            logger.warning(f"Timeout for {train_number}")
            browser.close()
            return "TIMEOUT"
        except Exception as e:
            logger.exception(f"Playwright error: {e}")
            browser.close()
            return "ERROR"

        browser.close()

    if not captured:
        logger.warning(f"No availability data captured for {train_number} {class_code}")
        return "NOT FOUND"

    logger.info(f"Captured URL: {captured.get('url')}")
    return _parse_availability(captured["data"], class_code)


def _parse_availability(data: dict, class_code: str) -> str:
    """
    Parse IRCTC availability JSON response.
    Returns the availability string for the requested class.
    """
    try:
        # IRCTC returns a list of availability objects
        avail_list = data.get("avlDayList") or data.get("availabilityList") or []

        if not avail_list:
            # Some responses wrap differently
            if isinstance(data, list):
                avail_list = data

        if not avail_list:
            logger.warning(f"Empty availability list. Raw: {str(data)[:300]}")
            return "NOT FOUND"

        # Return the first (earliest quota) availability status
        first = avail_list[0]
        status = (
            first.get("availablityStatus")
            or first.get("availability")
            or first.get("status")
            or "UNKNOWN"
        )
        return str(status).strip()

    except Exception as e:
        logger.exception(f"Parse error: {e} | data: {str(data)[:300]}")
        return "ERROR"
