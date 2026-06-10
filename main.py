import asyncio
import logging
import threading
from datetime import datetime

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import insert, select, update

from models import engine, alerts
from railway import get_status
from telegram_bot import send_alert, build_application
from scheduler import scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train-alert")

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# ── Alert checker (unchanged logic) ──────────────────────────────────────────
def check_alerts():
    logger.info("=" * 50)
    logger.info(
        f"Checking alerts at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    logger.info("=" * 50)

    with engine.connect() as conn:
        rows = conn.execute(select(alerts)).fetchall()

    logger.info(f"Found {len(rows)} alerts")

    for row in rows:
        logger.info(f"Checking alert ID {row.id}")
        if row.notified:
            logger.info("Already notified, skipping")
            continue

        try:
            status = get_status(
                row.train_number,
                row.from_station,
                row.to_station,
                row.journey_date,
                row.class_code,
            )
            logger.info(
                f"Train={row.train_number} Class={row.class_code} Status={status}"
            )

            status = str(status).strip().upper()
            if status not in [
                "REGRET",
                "NOT AVAILABLE",
                "TRAIN DEPARTED",
                "NOT FOUND",
                "TIMEOUT",
                "ERROR",
            ]:
                logger.info("Bookable status found, sending Telegram alert")
                send_alert(
                    row.telegram_chat_id,
                    f"🚆 Train Booking Alert!\n\n"
                    f"Train: {row.train_number}\n"
                    f"Route: {row.from_station} → {row.to_station}\n"
                    f"Class: {row.class_code}\n"
                    f"Status: {status}\n",
                )

                with engine.connect() as conn:
                    conn.execute(
                        update(alerts)
                        .where(alerts.c.id == row.id)
                        .values(notified=True)
                    )
                    conn.commit()

                logger.info(f"Notification sent for alert {row.id}")

        except Exception as e:
            logger.exception(f"Error checking alert {row.id}: {e}")


# ── Telegram bot thread ───────────────────────────────────────────────────────
def _run_bot():
    """
    Run the bot in a background thread without run_polling().
    run_polling() installs signal handlers which require the main thread;
    instead we drive the async machinery directly.
    """
    async def _start_polling(bot_app):
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)
        # Keep the loop alive until the daemon thread is killed on app exit
        while True:
            await asyncio.sleep(3600)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_app = build_application()
    try:
        loop.run_until_complete(_start_polling(bot_app))
    except Exception as exc:
        logger.exception("Telegram bot thread crashed: %s", exc)


# ── FastAPI lifecycle ─────────────────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    # Start scheduler
    logger.info("Starting APScheduler…")
    scheduler.add_job(
        check_alerts,
        "interval",
        minutes=10,
        id="train_alert_checker",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started")

    # Start Telegram bot in background thread
    logger.info("Starting Telegram bot thread…")
    bot_thread = threading.Thread(target=_run_bot, daemon=True, name="telegram-bot")
    bot_thread.start()
    logger.info("Telegram bot thread started")


# ── Web routes ────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/add-alert")
def add_alert_web(
    train_number: str = Form(...),
    from_station: str = Form(...),
    to_station: str = Form(...),
    journey_date: str = Form(...),
    class_code: str = Form(...),
    telegram_chat_id: str = Form(...),
):
    with engine.connect() as conn:
        conn.execute(
            insert(alerts).values(
                train_number=train_number,
                from_station=from_station,
                to_station=to_station,
                journey_date=journey_date,
                class_code=class_code,
                telegram_chat_id=telegram_chat_id,
                notified=False,
            )
        )
        conn.commit()
    return {"success": True, "message": "Alert saved"}


@app.get("/test-check")
def test_check():
    check_alerts()
    return {"success": True, "message": "Manual check completed"}
