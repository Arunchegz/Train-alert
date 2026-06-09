from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "sqlite:///alerts.db",
    connect_args={"check_same_thread": False}
)

metadata = MetaData()

alerts = Table(
    "alerts",
    metadata,

    Column("id", Integer, primary_key=True),
    Column("train_number", String),
    Column("from_station", String),
    Column("to_station", String),
    Column("journey_date", String),
    Column("class_code", String),
    Column("telegram_chat_id", String),
    Column("notified", Boolean, default=False)
)

metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
