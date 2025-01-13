from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import re
import os
import dotenv

import sqlite3

from app.pachca_client import PachcaClient

dotenv.load_dotenv()

app = FastAPI()

conn = sqlite3.connect("bot.db")
db = conn.cursor()
db.execute(
    """
    CREATE TABLE IF NOT EXISTS tickets (
        issue_key TEXT PRIMARY KEY,
        chat_id INT,
        message_id INT
    )
    """
)


class ThreadInfo(BaseModel):
    message_id: int
    message_chat_id: int


class PachcaMessage(BaseModel):
    type: str
    id: int
    event: str
    entity_type: str
    entity_id: int
    content: str
    user_id: int
    created_at: datetime
    chat_id: int
    parent_message_id: int | None
    thread: ThreadInfo | None


class TrackerTicket(BaseModel):
    issue_key: str
    status: str


@app.post("/pachca_message")
def pachca_new_message(message: PachcaMessage):
    issue_key = re.findall(r"TEST-\d+", message.content)
    if len(issue_key) == 0:
        raise ValueError("No issue key found")
    issue_key = issue_key[0]
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute(
        f"""
        INSERT INTO tickets VALUES ('{issue_key}', {message.chat_id}, {message.id})
        ON CONFLICT (issue_key) DO UPDATE SET
            chat_id=excluded.chat_id,
            message_id=excluded.message_id;
        """
    )
    conn.commit()
    pachca_client = PachcaClient(token=os.getenv("PACHCA_TOKEN"))
    pachca_client.send_message(
        chat_id=message.chat_id,
        text=f"Я сообщу вам об изменении статуса тикета {issue_key}",
        parent_message_id=message.id,
    )


@app.post("/tracker_ticket")
def tracker_ticket(ticket: TrackerTicket):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    issue_info = cur.execute(
        f"SELECT chat_id, message_id FROM tickets WHERE issue_key = '{ticket.issue_key}'"
    ).fetchone()
    if issue_info is None:
        return f"Issue {ticket.issue_key} is not tracked"
    chat_id, message_id = issue_info
    pachca_client = PachcaClient(token=os.getenv("PACHCA_TOKEN"))
    pachca_client.send_message(
        chat_id=chat_id,
        text=f"Тикет {ticket.issue_key} был переведён в статус {ticket.status}",
        parent_message_id=message_id,
    )
