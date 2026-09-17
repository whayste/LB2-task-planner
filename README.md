# Проект: Умный планировщик задач

## Запуск проекта:
1. Запуск Task Service (Порт 8001): `python -m uvicorn task_service.main:app --port 8001 --reload`
2. Запуск Notification Service (Порт 8002): `python -m uvicorn notification_service.main:app --port 8002 --reload`
3. `http://127.0.0.1:8001`

