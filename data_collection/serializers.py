from rest_framework import serializers
from .models import SixMonthData, AnnualData, AnnualChildrenStatus, AnnualSelfHelpGroupData

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

class AnnualSelfHelpGroupDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualSelfHelpGroupData
        fields = "__all__"
