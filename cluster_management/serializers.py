from rest_framework import serializers
from .models import Cluster, SelfHelpGroup, Member

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = '__all__'

class SelfHelpGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfHelpGroup
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'