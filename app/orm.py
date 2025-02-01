from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class TicketSubscription(Base):
    __tablename__ = "ticket_subscription"
    id: Mapped[int] = mapped_column(primary_key=True)
    issue_key: Mapped[str]
    chat_id: Mapped[int]
    message_id: Mapped[int]
