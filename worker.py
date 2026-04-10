import os
import redis
from redis import Redis
from rq import Worker, Queue, Connection
from app.jobs import send_due_soon_reminder

conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(Queue())
        worker.work()