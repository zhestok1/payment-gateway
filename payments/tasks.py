import os
import requests
from celery import shared_task
from django.db import transaction
from .models import Operation

PROVIDER_URL = os.getenv('PROVIDER_URL', 'http://provider-simulator:8081')

@shared_task(bind=True, max_retries=5, default_retry_delay=5)
def send_operation_to_provider(self, operation_id):
    try:
        with transaction.atomic():
            operation = Operation.objects.select_for_update().get(operation_id=operation_id)
            
            # Если операция уже в финальном статусе, прекращаем попытки
            if operation.status in [Operation.OperationStatus.COMPLETED, Operation.OperationStatus.REJECTED]:
                return

            # Убедимся, что она в PROCESSING
            if operation.status != Operation.OperationStatus.PROCESSING:
                old_status = operation.status
                operation.status = Operation.OperationStatus.PROCESSING
                operation.save(update_fields=['status', 'updated_at'])
                operation.log_event(
                    from_status=old_status,
                    to_status=Operation.OperationStatus.PROCESSING,
                    message="Operation set to processing for provider submission"
                )

        # Выполняем HTTP-запрос к провайдеру ВНЕ транзакции базы данных (чтобы не держать блокировки)
        headers = {
            'Content-Type': 'application/json',
            'Idempotency-Key': operation.operation_id,
            'X-Correlation-ID': operation.operation_id,
        }
        payload = {
            "operationId": operation.operation_id,
            "amount": str(operation.amount),
            "currency": operation.currency,
        }

        response = requests.post(f"{PROVIDER_URL}/payments", json=payload, headers=headers, timeout=10)

        if response.status_code == 202:
            data = response.json()
            provider_payment_id = data.get('providerPaymentId')
            
            with transaction.atomic():
                op = Operation.objects.select_for_update().get(operation_id=operation_id)
                if provider_payment_id and not op.provider_payment_id:
                    op.provider_payment_id = provider_payment_id
                    op.save(update_fields=['provider_payment_id', 'updated_at'])
        
        elif response.status_code == 503 or response.status_code >= 500:
            raise self.retry(exc=Exception(f"Provider returned status {response.status_code}"))

    except (requests.RequestException, Exception) as exc:
        raise self.retry(exc=exc)