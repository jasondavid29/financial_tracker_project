from rest_framework import serializers
from .models import Income, Expense, Budget
from .models import Transaction


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'category', 'amount', 'created_at', 'user']

    def create(self, validated_data):
        request = self.context.get("request")  # Get request context
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user  # Assign the logged-in user
        return super().create(validated_data)