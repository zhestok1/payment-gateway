from rest_framework import serializers
from .models import Operation

class OperationCreateSerializer(serializers.ModelSerializer):
    operation_id = serializers.CharField(max_length=600, required=True)
    amount = serializers.DecimalField(max_digits=30, decimal_places=2)
    currency = serializers.CharField(max_length=10, default='RUB')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Operation
        fields = ['operation_id', 'amount', 'currency', 'description']
        
class OperationSerializer(serializers.ModelSerializer):
    operation_id = serializers.CharField()
    provider_payment_id = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Operation
        fields = [
            'operation_id',
            'amount',
            'currency',
            'description',
            'status',
            'provider_payment_id'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['operationId'] = representation.pop('operation_id')
        representation['providerPaymentId'] = representation.pop('provider_payment_id')
        return representation   
    
class ReceiptSerializer(serializers.Serializer):
    provider_payment_id = serializers.CharField(max_length=600)
    operation_id = serializers.CharField(max_length=600)
    result = serializers.ChoiceField(choices=['COMPLETED', 'REJECTED'])
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    occurred_at = serializers.DateTimeField(required=False, allow_null=True)
        
        

