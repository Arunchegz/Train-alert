from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import insert, select, update

from models import engine, alerts
from railway import get_status
from telegram_bot import send_alert
from scheduler import scheduler

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/add-alert")
def add_alert(
    train_number: str = Form(...),
    from_station: str = Form(...),
    to_station: str = Form(...),
    journey_date: str = Form(...),
    class_code: str = Form(...),
    telegram_chat_id: str = Form(...)
):

    conn = engine.connect()

    conn.execute(
        insert(alerts).values(
            train_number=train_number,
            from_station=from_station,
            to_station=to_station,
            journey_date=journey_date,
            class_code=class_code,
            telegram_chat_id=telegram_chat_id,
            notified=False
        )
    )

    conn.commit()

    return {
        "success": True,
        "message": "Alert saved"
    }


def check_alerts():

    print("Checking alerts...")

    conn = engine.connect()

    rows = conn.execute(
        select(alerts)
    ).fetchall()

    for row in rows:

        if row.notified:
            continue

        try:

            status = get_status(
                row.train_number,
                row.from_station,
                row.to_station,
                row.journey_date,
                row.class_code
            )

            print(
                f"Train={row.train_number} "
                f"Class={row.class_code} "
                f"Status={status}"
            )

            if (
                status
                and isinstance(status, str)
                and status.startswith("AVAILABLE")
            ):

                send_alert(
                    row.telegram_chat_id,
                    f"""🚆 Seat Available!

Train: {row.train_number}
Route: {row.from_station} → {row.to_station}

Class: {row.class_code}

Status: {status}
"""
                )

                conn.execute(
                    update(alerts)
                    .where(alerts.c.id == row.id)
                    .values(notified=True)
                )

                conn.commit()

                print(
                    f"Notification sent for alert {row.id}"
                )

        except Exception as e:

            print(
                f"Error checking alert {row.id}: {e}"
            )


scheduler.add_job(
    check_alerts,
    "interval",
    minutes=1
)

scheduler.start()
