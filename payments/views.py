from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Operation, OperationEvent
from .serializers import (
    OperationCreateSerializer,
    OperationSerializer,
    ReceiptSerializer
)
from .services import OperationService
from .tasks import send_operation_to_provider


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class OperationCreateApiView(APIView):
    def post(self, request):
        serializer = OperationCreateSerializer(data=request.data)
        if serializer.is_valid():
            operation_id = serializer.validated_data['operation_id']
            
            if Operation.objects.filter(operation_id=operation_id).exists():
                return Response({"error": "Operation already exists"}, status=status.HTTP_409_CONFLICT)
            
            operation = OperationService.create_operation(serializer.validated_data)
            response_serializer = OperationSerializer(operation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OperationSubmitApiView(APIView):
    def post(self, request, operation_id):
        try:
            with transaction.atomic():
                operation = Operation.objects.select_for_update().get(operation_id=operation_id)
                
                if operation.status in [Operation.OperationStatus.PROCESSING, Operation.OperationStatus.COMPLETED, Operation.OperationStatus.REJECTED]:
                    serializer = OperationSerializer(operation)
                    return Response(serializer.data, status=status.HTTP_200_OK)

                old_status = operation.status
                operation.status = Operation.OperationStatus.PROCESSING
                operation.save(update_fields=['status', 'updated_at'])
                
                operation.log_event(
                    from_status=old_status,
                    to_status=Operation.OperationStatus.PROCESSING,
                    message="Submission requested, intent saved"
                )

                transaction.on_commit(lambda: send_operation_to_provider.delay(operation.operation_id))

        except Operation.DoesNotExist:
            return Response({"error": "Operation not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OperationSerializer(operation)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class OperationDetailApiView(APIView):
    def get(self, request, operation_id):
        operation = get_object_or_404(Operation, operation_id=operation_id)
        serializer = OperationSerializer(operation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OperationEventsApiView(APIView):
    def get(self, request, operation_id):
        operation = get_object_or_404(Operation, operation_id=operation_id)
        events = operation.events.all().order_by('event_id')
        
        events_data = [{
            "eventId": event.event_id,
            "type": event.to_status,
            "fromStatus": event.from_status if event.from_status else None,
            "toStatus": event.to_status,
            "message": event.message,
            "occurredAt": event.occured_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        } for event in events]
        
        return Response(events_data, status=status.HTTP_200_OK)


class ReceiptApiView(APIView):
    def post(self, request):
        serializer = ReceiptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        operation_id = data.get('operation_id')
        provider_payment_id = data.get('provider_payment_id')
        result = data.get('result')  
        message = data.get('message', '')

        try:
            with transaction.atomic():
                operation = Operation.objects.select_for_update().get(operation_id=operation_id)

                # Если provider_payment_id уже установлен и не совпадает — 409 Conflict
                if operation.provider_payment_id and operation.provider_payment_id != provider_payment_id:
                    return Response({"error": "Provider payment ID mismatch"}, status=status.HTTP_409_CONFLICT)

                # Установка provider_payment_id из первой валидной квитанции, если его не было
                if not operation.provider_payment_id:
                    operation.provider_payment_id = provider_payment_id

                # Если операция уже в финальном статусе
                if operation.status in [Operation.OperationStatus.COMPLETED, Operation.OperationStatus.REJECTED]:
                    # Повтор той же квитанции или поздняя квитанция с результатом отвечает 204
                    return Response(status=status.HTTP_204_NO_CONTENT)

                old_status = operation.status
                new_status = (
                    Operation.OperationStatus.COMPLETED 
                    if result == 'COMPLETED' 
                    else Operation.OperationStatus.REJECTED
                )

                operation.status = new_status
                operation.save(update_fields=['status', 'provider_payment_id', 'updated_at'])

                operation.log_event(
                    from_status=old_status,
                    to_status=new_status,
                    message=message or f"Receipt received with result: {result}"
                )

        except Operation.DoesNotExist:
            return Response({"error": "Operation not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)