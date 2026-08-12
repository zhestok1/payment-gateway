# Payment Processing Service

Сервис для обработки платежей и управления асинхронными операциями. Проект построен на базе Django, Django REST Framework, Celery, Redis и PostgreSQL, упакован в Docker и полностью готов к запуску одной командой.

---

## Требования

Для запуска проекта на чистой машине у вас должны быть установлены:
* **Docker** (с поддержкой Docker Compose)
* **Git**

---

## Инструкция по запуску

1. **Клонируйте репозиторий:**
   ```bash
   git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
   cd <ИМЯ_ПАПКИ_РЕПОЗИТОРИЯ>
   ```
2. **Запустите проект с помощью Docker Compose:**
   ```bash
   docker compose up -d --build
   ```
3. **Примените миграции базы данных:**
   ```bash
   docker compose exec candidate-service python manage.py migrate
   ```
## Некоторые тесты
1. **GET /api/operations/{operation_id}**<br>
   powershell:                                                                                                                                                               
   ```bash
   Invoke-RestMethod -Uri "http://localhost:8080/api/operations/op-test-1" -Method Get 
   ```
   curl:
   ```bash
   curl -X GET http://localhost:8080/api/operations/op-test-1
   ```
2. **GET /api/operations/{operation_id}/events**<br>
   powershell:
   ```bash
   Invoke-RestMethod -Uri "http://localhost:8080/api/operations/op-test-1/events" -Method Get
   ```
   curl:
   ```bash
   curl -X GET http://localhost:8080/api/operations/op-test-1/events
   ```
3. **GET /api/operations**<br>
   powershell:
   ```bash
   Invoke-RestMethod -Uri "http://localhost:8080/api/operations" -Method Get
   ```
   curl:
   ```bash
   curl -X GET http://localhost:8080/api/operations
   ```

   
   
