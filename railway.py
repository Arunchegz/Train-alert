import requests
from datetime import datetime

def get_availability(
    train_no: str,
    journey_date: str,
    source: str,
    destination: str,
    travel_class: str,
    quota: str = "GN"
):
    """
    journey_date format: YYYY-M-D
    Example: 2026-6-11
    """

    url = (
        f"https://sa.railyatri.in/api/seat/enquiry/"
        f"{train_no}/{journey_date}/"
        f"{source}/{destination}/"
        f"{travel_class}/{quota}.json"
    )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            return {
                "success": False,
                "error": data.get("error", "Unknown error")
            }

        availability = data["seat_availibility"][0]

        return {
            "success": True,
            "status": availability.get("seat_avl_text"),
            "count": availability.get("seat_avl"),
            "raw_status": availability.get("availablity_status"),
            "fare": availability.get("ticket_fare"),
            "last_updated": availability.get("last_updated_at"),
            "full_data": availability
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    result = get_availability(
        train_no="12076",
        journey_date="2026-6-11",
        source="ERS",
        destination="CLT",
        travel_class="CC",
        quota="GN"
    )

    print(result)
