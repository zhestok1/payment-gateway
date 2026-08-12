from django.urls import path
from .views import (
    HealthCheckView,
    OperationCreateApiView,
    OperationSubmitApiView,
    OperationDetailApiView,
    OperationEventsApiView,
    ReceiptApiView
)

app_name = 'payments'

urlpatterns = [
    path('health', HealthCheckView.as_view(), name='health'),
    path('operations', OperationCreateApiView.as_view(), name='operation-create'),
    path('operations/<str:operation_id>/submit', OperationSubmitApiView.as_view(), name='operation-submit'),
    path('operations/<str:operation_id>', OperationDetailApiView.as_view(), name='operation-detail'),
    path('operations/<str:operation_id>/events', OperationEventsApiView.as_view(), name='operation-events'),
    path('receipts', ReceiptApiView.as_view(), name='receipt-webhook'),
]