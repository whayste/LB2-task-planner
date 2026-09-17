import os
import logging
from uuid import uuid4
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List
from fastapi import FastAPI, status, HTTPException, Path, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [TaskService] - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Task Service")

# Ссылка на вебхук (localhost для стабильности в Windows)
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8002/api/webhooks/task_created")

tasks_db: Dict[str, dict] = {}

class TaskStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"

class TaskCreate(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.new

class TaskUpdate(BaseModel):
    title: str
    description: str
    status: TaskStatus

class Task(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus
    created_at: str

async def send_notification_webhook(task_data: dict):
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Попытка отправки вебхука для задачи {task_data['id']}...")
            response = await client.post(NOTIFICATION_SERVICE_URL, json=task_data, timeout=3.0)
            if response.status_code == 200:
                logger.info(f"Вебхук для задачи {task_data['id']} успешно доставлен.")
        except httpx.RequestError as exc:
            logger.critical(f"Локальная точка отказа! Не удалось связаться с Notification Service: {exc}.")

# ==========================================
# 🌟 ИСПРАВЛЕННЫЙ ВЕБ-ИНТЕРФЕЙС
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def UI_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Умный планировщик задач</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .form-group { display: flex; flex-direction: column; gap: 10px; margin-bottom: 25px; background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
            input, textarea, select { padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 15px; }
            button { background: #3b82f6; color: white; border: none; padding: 12px 20px; border-radius: 6px; font-size: 15px; cursor: pointer; font-weight: bold; transition: 0.2s; }
            button:hover { background: #2563eb; }
            .task-list { display: flex; flex-direction: column; gap: 15px; }
            .task-card { background: white; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); position: relative; }
            .task-title { font-size: 18px; font-weight: bold; color: #1e293b; margin-bottom: 5px; }
            .task-desc { color: #64748b; margin-bottom: 15px; font-size: 15px; }
            .badge { display: inline-block; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; }
            .badge-new { background: #dbeafe; color: #1e40af; }
            .badge-in_progress { background: #fef3c7; color: #92400e; }
            .badge-done { background: #dcfce7; color: #14532d; }
            .actions { display: flex; gap: 10px; margin-top: 15px; }
            .btn-delete { background: #ef4444; }
            .btn-delete:hover { background: #dc2626; }
            .btn-status { background: #10b981; }
            .btn-status:hover { background: #059669; }
            .time { font-size: 11px; color: #94a3b8; float: right; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Умный планировщик задач</h1>
            
            <div class="form-group">
                <h3>➕ Создать новую задачу</h3>
                <input type="text" id="title" placeholder="Что нужно сделать?">
                <textarea id="description" rows="3" placeholder="Добавьте подробности или описание..."></textarea>
                <button onclick="createTask()">Добавить задачу</button>
            </div>

            <h3>📋 Список текущих задач</h3>
            <div id="tasks" class="task-list"></div>
        </div>

        <script>
            // Исправлен синтаксис JavaScript (вместо async def теперь правильный async function)
            async function loadTasks() {
                const response = await fetch('/api/tasks');
                const tasks = await response.json();
                const container = document.getElementById('tasks');
                container.innerHTML = tasks.length === 0 ? '<p style="color: #94a3b8; text-align:center;">Задач пока нет. Создайте первую!</p>' : '';
                
                tasks.forEach(task => {
                    let badgeClass = 'badge-' + task.status;
                    let statusText = task.status === 'new' ? 'Новая' : task.status === 'in_progress' ? 'В работе' : 'Выполнено';
                    
                    container.innerHTML += `
                        <div class="task-card">
                            <span class="time">${task.created_at}</span>
                            <div class="task-title">${task.title}</div>
                            <div class="task-desc">${task.description}</div>
                            <span class="badge ${badgeClass}">${statusText}</span>
                            
                            <div class="actions">
                                ${task.status !== 'done' ? `<button class="btn-status" onclick="nextStatus('\({task.id}', '\){task.title}', '\({task.description}', '\){task.status}')">Продвинуть статус</button>` : ''}
                                <button class="btn-delete" onclick="deleteTask('${task.id}')">Удалить</button>
                            </div>
                        </div>
                    `;
                });
            }

            async function createTask() {
                const title = document.getElementById('title').value;
                const description = document.getElementById('description').value;
                if(!title) return alert('Введите название задачи!');

                await fetch('/api/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description, status: 'new' })
                });

                document.getElementById('title').value = '';
                document.getElementById('description').value = '';
                loadTasks();
            }

            async function nextStatus(id, title, description, currentStatus) {
                let nextStatus = currentStatus === 'new' ? 'in_progress' : 'done';
                await fetch(`/api/tasks/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description, status: nextStatus })
                });
                loadTasks();
            }

            async function deleteTask(id) {
                if(confirm('Удалить эту задачу?')) {
                    await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
                    loadTasks();
                }
            }

            loadTasks();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ==========================================
# API ЭНДПОИНТЫ
# ==========================================
@app.post("/api/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate):
    task_id = str(uuid4())
    created_at_str = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M:%S")
    
    new_task = {
        "id": task_id, "title": task_in.title, "description": task_in.description,
        "status": task_in.status.value, "created_at": created_at_str
    }
    tasks_db[task_id] = new_task
    logger.info(f"Задача {task_id} успешно создана в памяти.")
    await send_notification_webhook(new_task)
    return new_task

@app.get("/api/tasks", response_model=List[Task])
async def get_all_tasks():
    return list(tasks_db.values())

@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Не найдено")
    return tasks_db[task_id]

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_in: TaskUpdate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Не найдено")
    tasks_db[task_id]["title"] = task_in.title
    tasks_db[task_id]["description"] = task_in.description
    tasks_db[task_id]["status"] = task_in.status.value
    return tasks_db[task_id]

@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Не найдено")
    del tasks_db[task_id]
    return None
