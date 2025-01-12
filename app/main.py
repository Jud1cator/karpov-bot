from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


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


@app.post("/pachca_message")
def pachca_new_message(message: PachcaMessage):
    return message
