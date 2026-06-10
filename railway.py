import requests


def get_status(
    train_no,
    source,
    destination,
    journey_date,
    travel_class,
    quota="GN"
):
    """
    Returns:
        AVAILABLE
        WAITLIST
        RAC
        REGRET
        NOT AVAILABLE
        TRAIN DEPARTED
        ERROR
    """

    try:

        url = (
            f"https://sa.railyatri.in/api/seat/enquiry/"
            f"{train_no}/{journey_date}/"
            f"{source}/{destination}/"
            f"{travel_class}/{quota}.json"
        )

        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            return "ERROR"

        seat = data["seat_availibility"][0]

        status = seat.get(
            "seat_avl_text",
            "ERROR"
        )

        return str(status).upper()

    except Exception:
        return "ERROR"
