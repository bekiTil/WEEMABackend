from rest_framework import serializers
from .models import SixMonthData, AnnualData, AnnualChildrenStatus

class SixMonthDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SixMonthData
        fields = "__all__"

class AnnualDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualData
        fields = "__all__"

class AnnualChildrenStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualChildrenStatus
        fields = "__all__"
