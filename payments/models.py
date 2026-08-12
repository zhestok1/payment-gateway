from django.db import models

class Operation(models.Model):
    operation_id = models.CharField(max_length=600, unique=True, primary_key=True)
    amount = models.DecimalField(max_digits=30, decimal_places=2)
    currency = models.CharField(default='RUB')
    description = models.TextField(blank=True, null=True)
    
    class OperationStatus(models.TextChoices):
        CREATED = 'CREATED', 'СОЗДАН'
        PROCESSING = 'PROCESSING', 'В ПРОЦЕССЕ'
        COMPLETED = 'COMPLETED', 'ВЫПОЛНЕН'
        REJECTED = 'REJECTED', 'ОТМЕНЕН'
        
    status = models.CharField(
        max_length=25,
        choices=OperationStatus.choices,
    )
    
    provider_payment_id = models.CharField(unique=True, blank=True, null=True, max_length=600)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'
        ordering = ['-updated_at']
        
    def __str__(self):
        return self.operation_id
    

class OperationEvent(models.Model):
    
    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='events'
    )
    
    from_status = models.CharField(max_length=25, blank=True, null=True)
    to_status = models.CharField(max_length=25)
    
    event_id = models.BigIntegerField()
    
    message = models.TextField()
    
    occured_at = models.DateTimeField(auto_now_add=True)
    
    def log_event(self, from_status, to_status, message):
        last_event = self.events.order_by('-event_id').first()
        next_event_id = (last_event.event_id + 1) if last_event else 1
        
        OperationEvent.objects.create(
            operation=self,
            event_id=next_event_id,
            from_status=from_status,
            to_status=to_status,
            message=message
        )

