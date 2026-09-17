# Контракт API — Сервис «Умный планировщик задач»

## 1. Схема данных Task (Объект задачи)
```json
{
  "id": "UUIDv4 (string)",
  "title": "string",
  "description": "string",
  "status": "string (enum: new, in_progress, done)",
  "created_at": "string (ISO8601 UTC)"
}
```

## 2. Эндпоинты

### Endpoint 1: Task Service (Создание задачи)
* **Метод:** POST
* **Путь:** /api/tasks
* **Тело запроса (JSON):**
  ```json
  {
    "title": "Купить молоко",
    "description": "В магазине у дома",
    "status": "new"
  }
  ```
* **Ответ:** Код 201 Created
* **Тело ответа (JSON):** Полный объект Task (включая сгенерированные id и created_at).

### Endpoint 2: Notification Service (Вебхук создания задачи)
* **Метод:** POST
* **Путь:** /api/webhooks/task_created
* **Тело запроса (JSON):** Полный объект Task, отправленный из Task Service.
* **Ответ:** Код 200 OK
* **Тело ответа (JSON):**
  ```json
  {
    "status": "success"
  }
  ```
