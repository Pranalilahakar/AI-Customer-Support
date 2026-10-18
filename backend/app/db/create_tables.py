
from app.db.base import Base
from app.db.database import engine
from app.models import User, Ticket, TicketComment


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    print("Tables:", sorted(Base.metadata.tables.keys()))


if __name__ == "__main__":
    create_tables()
