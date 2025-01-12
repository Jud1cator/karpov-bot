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
db.execute("CREATE TABLE IF NOT EXISTS tickets (issue_key, chat_id, message_id)")


class ThreadInfo(BaseModel):
    message_id: int
    message_chat_id: int


class PachcaMessage(BaseModel):
    """
    {
    "type": "message", //тип объекта
    "id": 4062313533, //идентификатор объекта
    "event": "new", //тип события (new,update или delete)
    "entity_type": "thread", //тип сущности, к которой относится объект (discussion, thread или user)
    "entity_id": 14904221, //идентификатор сущности, к которой относится объект
    "content": "/new разработка чата", //текст сообщения
    "user_id": 18531312, //идентификатор отправителя
    "created_at": "2023-01-26T15:25:16.000Z", //время создания сообщения
    "chat_id": 34876123, //идентификатор чата, в котором находится сообщение
    "parent_message_id": 4062313532, //идентификатор сообщения, к которому написан ответ (или null, если сообщение не является ответом)
    "thread": { //объект с параметрами треда (или null, если это сообщение не относится к треду)
        "message_id": 5631128658, //идентификатор сообщения, к которому был создан тред
        "message_chat_id": 38926752 //идентификатор чата сообщения, к которому был создан тред
        }
    }
    """

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


@app.post("/pachca_message")
def pachca_new_message(message: PachcaMessage):
    issue_key = re.findall(r"TEST-\d+", message.content)
    if len(issue_key) > 0:
        issue_key = issue_key[0]
        conn = sqlite3.connect("bot.db")
        cur = conn.cursor()
        cur.execute(f"INSERT INTO tickets VALUES ('{issue_key}', {message.chat_id}, {message.id})")
        conn.commit()
    else:
        raise ValueError("No issue key found")

@app.post("/tracker_ticket")
def tracker_ticket(ticket: TrackerTicket):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    issue_info = cur.execute(f"SELECT chat_id, message_id FROM tickets WHERE issue_key = '{ticket.issue_key}'").fetchone()
    if issue_info is None:
        return f"Issue {ticket.issue_key} is not tracked"
    chat_id, message_id = issue_info
    pachca_client = PachcaClient(token=os.getenv("PACHCA_TOKEN"))
    pachca_client.send_message(
        chat_id=chat_id,
        text=f"Ticket {ticket.issue_key} is closed!",
        parent_message_id=message_id,
    )
