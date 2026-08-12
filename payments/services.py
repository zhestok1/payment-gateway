from django.db import transaction
from .models import Operation
# Импортируем нашу Celery-задачу (напишем её чуть позже)
from .tasks import send_operation_to_provider 

class OperationService:

    @staticmethod
    @transaction.atomic
    def create_operation(validated_data: dict) -> Operation:
        """
        Создает операцию, записывает первое событие (CREATED) 
        и инициирует отправку платежа во внешнюю систему через Celery.
        """
        # 1. Создаем саму операцию в базе данных
        operation = Operation.objects.create(
            status=Operation.OperationStatus.CREATED,
            **validated_data
        )

        # 2. Логируем начальный статус через метод модели log_event
        operation.log_event(
            from_status="",
            to_status=Operation.OperationStatus.CREATED,
            message="Operation created"
        )

        # 3. Гарантированно отправляем задачу в Celery ТОЛЬКО после фиксации транзакции в БД
        transaction.on_commit(lambda: send_operation_to_provider.delay(operation.operation_id))

        return operation