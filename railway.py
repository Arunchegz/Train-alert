import requests

URL = "https://trainticketapi.railyatri.in/api/trains-between-station-with-sa.json"

def get_status(
    train_number,
    from_station,
    to_station,
    journey_date,
    class_code
):
    params = {
        "from": from_station,
        "to": to_station,
        "dateOfJourney": journey_date,
        "journey_quota": "GN",
        "device_type_id": "6"
    }

    r = requests.get(URL, params=params, timeout=30)

    data = r.json()

    for train in data.get(
        "train_between_stations",
        []
    ):
        if train["train_number"] != train_number:
            continue

        for cls in train["sa_data"]:
            if cls["booking_class"] == class_code:
                return cls["availibility"]

    return "NOT FOUND"
