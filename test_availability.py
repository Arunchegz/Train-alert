"""
Run this on your VPS to test seat availability before starting the full app.
Usage: python test_availability.py
"""
from railway import get_status

# Edit these to match your route
TEST_CASES = [
    {
        "train_number": "12075",  # Jan Shatabdi ERS→CLT
        "from_station": "ERS",
        "to_station":   "CLT",
        "journey_date": "20260620",
        "class_code":   "CC",
        "quota":        "GN",
    },
    {
        "train_number": "16307",  # Alleppey Express
        "from_station": "ERS",
        "to_station":   "CLT",
        "journey_date": "20260620",
        "class_code":   "SL",
        "quota":        "GN",
    },
]

for tc in TEST_CASES:
    print(f"\nChecking {tc['train_number']} | {tc['class_code']} | {tc['journey_date']}")
    status = get_status(**tc)
    print(f"  → Status: {status}")
