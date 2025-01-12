from yandex_tracker_client import TrackerClient
import os
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    client = TrackerClient(token=os.getenv("TRACKER_TOKEN"), org_id="7787140")
    for s in client.statuses:
        print(s, type(s), s.id, s.key, s.name)
    for i in client.issues:
        print(i, i.status, i.status.id, i.status.key, i.status.name)