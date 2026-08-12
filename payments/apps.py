from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'

    def ready(self):
        # Избегаем запуска во время миграций и авторелоада
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv or 'celery' in sys.argv:
            from .models import Operation
            from .tasks import send_operation_to_provider
            
            try:
                # Находим все операции, которые зависли в статусе PROCESSING при перезапуске
                processing_operations = Operation.objects.filter(status=Operation.OperationStatus.PROCESSING)
                for op in processing_operations:
                    send_operation_to_provider.delay(op.operation_id)
            except Exception:
                pass  