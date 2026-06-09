from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models import engine, alerts
from sqlalchemy import insert

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
