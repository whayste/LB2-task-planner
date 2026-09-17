import logging
from fastapi import FastAPI
from pydantic import BaseModel

# Кастомное логирование в стиле Дмитрия
logging.basicConfig(level=logging.INFO, format="[NOTIF-CENTER] %(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("NotificationService")

app = FastAPI(title="Notification Service")

class TaskPayload(BaseModel):
    id: str
    title: str
    description: str
    status: str
    created_at: str

@app.post("/api/webhooks/task_created")
async def handle_task_created_webhook(payload: TaskPayload):
    # Эмуляция отправки уведомления через красивую запись в консоль
    logger.info("=" * 50)
    logger.info("🚨 ПОЛУЧЕНО НОВОЕ УВЕДОМЛЕНИЕ О ЗАДАЧЕ!")
    logger.info(f"ID задачи: {payload.id}")
    logger.info(f"Название:  {payload.title}")
    logger.info(f"Статус:    [{payload.status.upper()}]")
    logger.info(f"Создано в: {payload.created_at}")
    logger.info("=" * 50)
    
    return {"status": "success"}
